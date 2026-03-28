# Amazon Comprehend #4 — Lambda によるリアルタイム安全性チェック
# ファイル: safety_check_handler.py
# 概要: API Gateway + Lambda 構成で、ユーザー入力テキストに対して
#       毒性検出 → PII 検出・マスキングをリアルタイムで処理する。
#
# 修正点（元記事からの変更）:
#   - Comprehend の 100KB/ドキュメント 上限に対応するテキスト長チェックを追加

import json
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

comprehend = boto3.client("comprehend")

# 設定
TOXICITY_THRESHOLD = 0.7
PII_CONFIDENCE_THRESHOLD = 0.8
MAX_TEXT_BYTES = 100_000  # Comprehend の 100KB 制限


def lambda_handler(event, context):
    """テキストの安全性チェックと PII マスキングを行う Lambda 関数。

    入力 JSON:
        {
            "text": "分析対象のテキスト",
            "language_code": "en"
        }

    Returns
    -------
    dict
        statusCode と body を含むレスポンス
    """
    text = event.get("text", "")
    language_code = event.get("language_code", "en")

    # テキスト長チェック
    text_bytes = len(text.encode("utf-8"))
    if text_bytes > MAX_TEXT_BYTES:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "error": f"テキストサイズ ({text_bytes:,} bytes) が "
                    f"上限 ({MAX_TEXT_BYTES:,} bytes) を超えています。"
                },
                ensure_ascii=False,
            ),
        }

    result = {
        "original_text": text,
        "is_safe": True,
        "processed_text": text,
        "pii_detected": False,
        "toxicity_detected": False,
        "details": {},
    }

    # ステップ1: 毒性検出
    toxicity_response = comprehend.detect_toxic_content(
        TextSegments=[{"Text": text}],
        LanguageCode=language_code,
    )

    toxicity_score = toxicity_response["ResultList"][0]["Toxicity"]
    if toxicity_score > TOXICITY_THRESHOLD:
        result["is_safe"] = False
        result["toxicity_detected"] = True
        result["details"]["toxicity_score"] = toxicity_score
        result["details"]["toxicity_labels"] = [
            {"name": l["Name"], "score": l["Score"]}
            for l in toxicity_response["ResultList"][0]["Labels"]
            if l["Score"] > 0.3
        ]
        return {
            "statusCode": 400,
            "body": json.dumps(result, ensure_ascii=False),
        }

    # ステップ2: PII検出（英語テキストの場合）
    if language_code == "en":
        pii_check = comprehend.contains_pii_entities(
            Text=text,
            LanguageCode=language_code,
        )

        has_pii = any(
            label["Score"] > PII_CONFIDENCE_THRESHOLD
            for label in pii_check["Labels"]
        )

        if has_pii:
            # PIIの詳細位置を取得してマスキング
            pii_response = comprehend.detect_pii_entities(
                Text=text,
                LanguageCode=language_code,
            )

            redacted_text = text
            entities = sorted(
                pii_response["Entities"],
                key=lambda x: x["BeginOffset"],
                reverse=True,
            )

            for entity in entities:
                if entity["Score"] > PII_CONFIDENCE_THRESHOLD:
                    begin = entity["BeginOffset"]
                    end = entity["EndOffset"]
                    pii_type = entity["Type"]
                    redacted_text = (
                        redacted_text[:begin]
                        + f"[{pii_type}]"
                        + redacted_text[end:]
                    )

            result["pii_detected"] = True
            result["processed_text"] = redacted_text
            result["details"]["pii_entities"] = [
                {"type": e["Type"], "score": e["Score"]}
                for e in pii_response["Entities"]
                if e["Score"] > PII_CONFIDENCE_THRESHOLD
            ]

    return {
        "statusCode": 200,
        "body": json.dumps(result, ensure_ascii=False),
    }
