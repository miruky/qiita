# Amazon Comprehend #5 — Bedrock × Comprehend ガードレールパイプライン
# ファイル: bedrock_guardrail.py
# 概要: Amazon Bedrock の入出力に対して Comprehend を使った多層防御を実装する。
#       InputGuardrail: プロンプト安全性 → 毒性検出 → PII マスキング
#       OutputGuardrail: 毒性検出 → PII マスキング
#       safe_bedrock_invoke: 入力チェック → Bedrock 呼び出し → 出力チェック
#
# 修正点（元記事からの変更）:
#   - PII 検出前に 100KB テキスト長チェックを追加
#   - プロンプト安全性エンドポイントのリージョン注記を追加

import json
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

comprehend = boto3.client("comprehend", region_name="ap-northeast-1")
bedrock_runtime = boto3.client("bedrock-runtime", region_name="ap-northeast-1")

# 設定
TOXICITY_THRESHOLD = 0.7
PII_CONFIDENCE_THRESHOLD = 0.8
MAX_TEXT_BYTES = 100_000  # Comprehend の 100KB 制限
MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"


class InputGuardrail:
    """Bedrock 入力ガードレール。

    プロンプト安全性 → 毒性検出 → PII マスキングの順にチェックする。
    """

    def __init__(self):
        self.checks_passed = []
        self.checks_failed = []

    def check_prompt_safety(self, text):
        """プロンプト安全性を確認する。"""
        response = comprehend.classify_document(
            Text=text,
            EndpointArn=(
                "arn:aws:comprehend:ap-northeast-1:aws:"
                "document-classifier-endpoint/prompt-safety"
            ),
        )

        for cls in response["Classes"]:
            if cls["Name"] == "UNSAFE" and cls["Score"] > 0.5:
                self.checks_failed.append(
                    {
                        "check": "prompt_safety",
                        "reason": "安全でないプロンプトが検出されました",
                        "score": cls["Score"],
                    }
                )
                return False

        self.checks_passed.append("prompt_safety")
        return True

    def check_toxicity(self, text):
        """毒性を確認する。"""
        response = comprehend.detect_toxic_content(
            TextSegments=[{"Text": text}],
            LanguageCode="en",
        )

        score = response["ResultList"][0]["Toxicity"]
        if score > TOXICITY_THRESHOLD:
            toxic_labels = [
                l["Name"]
                for l in response["ResultList"][0]["Labels"]
                if l["Score"] > 0.5
            ]
            self.checks_failed.append(
                {
                    "check": "toxicity",
                    "reason": f"有害コンテンツが検出されました: {', '.join(toxic_labels)}",
                    "score": score,
                }
            )
            return False

        self.checks_passed.append("toxicity")
        return True

    def mask_pii(self, text):
        """PII を検出してマスキングする。"""
        # テキスト長チェック
        if len(text.encode("utf-8")) > MAX_TEXT_BYTES:
            logger.warning("テキストが 100KB を超えているため PII チェックをスキップします")
            self.checks_passed.append("pii_skipped_too_long")
            return text

        pii_check = comprehend.contains_pii_entities(
            Text=text,
            LanguageCode="en",
        )

        has_pii = any(
            label["Score"] > PII_CONFIDENCE_THRESHOLD
            for label in pii_check["Labels"]
        )

        if not has_pii:
            self.checks_passed.append("pii_clean")
            return text

        # PII を検出してマスキング
        response = comprehend.detect_pii_entities(
            Text=text,
            LanguageCode="en",
        )

        masked_text = text
        entities = sorted(
            response["Entities"],
            key=lambda x: x["BeginOffset"],
            reverse=True,
        )

        for entity in entities:
            if entity["Score"] > PII_CONFIDENCE_THRESHOLD:
                begin = entity["BeginOffset"]
                end = entity["EndOffset"]
                masked_text = (
                    masked_text[:begin]
                    + f"[{entity['Type']}]"
                    + masked_text[end:]
                )

        self.checks_passed.append("pii_masked")
        return masked_text

    def validate(self, text):
        """すべてのチェックを実行する。

        Returns
        -------
        tuple[str | None, list | None]
            (安全なテキスト, None) または (None, エラーリスト)
        """
        self.checks_passed = []
        self.checks_failed = []

        # Step 1: プロンプト安全性
        if not self.check_prompt_safety(text):
            return None, self.checks_failed

        # Step 2: 毒性検出
        if not self.check_toxicity(text):
            return None, self.checks_failed

        # Step 3: PII マスキング
        safe_text = self.mask_pii(text)

        return safe_text, None


class OutputGuardrail:
    """Bedrock 出力ガードレール。

    毒性検出 → PII マスキングの順にチェックする。
    """

    FALLBACK_MESSAGE = (
        "申し訳ございませんが、適切な回答を生成できませんでした。"
        "別の表現でお試しください。"
    )

    def validate(self, response_text):
        """Bedrock の出力を検証する。

        Returns
        -------
        tuple[str, dict]
            (処理済みテキスト, アクション情報)
        """
        # Step 1: 毒性チェック
        toxicity = comprehend.detect_toxic_content(
            TextSegments=[{"Text": response_text[:1000]}],
            LanguageCode="en",
        )

        toxicity_score = toxicity["ResultList"][0]["Toxicity"]
        if toxicity_score > TOXICITY_THRESHOLD:
            return self.FALLBACK_MESSAGE, {
                "action": "replaced",
                "reason": "出力に有害コンテンツが検出されました",
                "score": toxicity_score,
            }

        # Step 2: PII マスキング
        if len(response_text.encode("utf-8")) > MAX_TEXT_BYTES:
            return response_text, {"action": "pii_skipped_too_long"}

        pii_check = comprehend.contains_pii_entities(
            Text=response_text,
            LanguageCode="en",
        )

        has_pii = any(
            l["Score"] > PII_CONFIDENCE_THRESHOLD for l in pii_check["Labels"]
        )

        if has_pii:
            pii_response = comprehend.detect_pii_entities(
                Text=response_text,
                LanguageCode="en",
            )

            masked = response_text
            entities = sorted(
                pii_response["Entities"],
                key=lambda x: x["BeginOffset"],
                reverse=True,
            )

            for entity in entities:
                if entity["Score"] > PII_CONFIDENCE_THRESHOLD:
                    begin = entity["BeginOffset"]
                    end = entity["EndOffset"]
                    masked = (
                        masked[:begin]
                        + f"[{entity['Type']}]"
                        + masked[end:]
                    )

            return masked, {"action": "pii_masked"}

        return response_text, {"action": "passed"}


# ---------------------------------------------------------------------------
# 入出力ガードレールを組み合わせた完全なパイプライン
# ---------------------------------------------------------------------------


def safe_bedrock_invoke(user_input, system_prompt="あなたは親切なアシスタントです。"):
    """安全な Bedrock 呼び出しパイプライン。

    Parameters
    ----------
    user_input : str
        ユーザーからの入力テキスト
    system_prompt : str
        システムプロンプト

    Returns
    -------
    dict
        status, message, guardrail_info を含む結果
    """
    # === 入力ガードレール ===
    input_guard = InputGuardrail()
    safe_input, errors = input_guard.validate(user_input)

    if errors:
        return {
            "status": "blocked",
            "message": "入力が安全基準を満たしていません。",
            "details": errors,
        }

    # === Bedrock 呼び出し ===
    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": [{"role": "user", "content": safe_input}],
        }
    )

    response = bedrock_runtime.invoke_model(modelId=MODEL_ID, body=body)

    response_body = json.loads(response["body"].read())
    ai_response = response_body["content"][0]["text"]

    # === 出力ガードレール ===
    output_guard = OutputGuardrail()
    safe_output, output_info = output_guard.validate(ai_response)

    return {
        "status": "success",
        "message": safe_output,
        "guardrail_info": {
            "input_checks": input_guard.checks_passed,
            "output_action": output_info["action"],
        },
    }


# ---------------------------------------------------------------------------
# メイン実行
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    result = safe_bedrock_invoke("What are AWS best practices for security?")
    print(json.dumps(result, indent=2, ensure_ascii=False))
