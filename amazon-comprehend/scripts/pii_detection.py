# Amazon Comprehend #4 — PII 検出とマスキング
# ファイル: pii_detection.py
# 概要: ContainsPiiEntities で PII 有無を高速判定し、
#       DetectPiiEntities で位置を特定してマスキングする。
#
# 修正点（元記事からの変更）:
#   - Comprehend の 100KB/ドキュメント 上限に対応するテキスト長チェックを追加
#   - PII 検出は 2026年3月時点で英語（en）のみ対応

import boto3

comprehend = boto3.client("comprehend", region_name="ap-northeast-1")

# Comprehend の 1 ドキュメントあたりの最大バイト数
MAX_TEXT_BYTES = 100_000  # 100KB


def _check_text_length(text):
    """テキストが Comprehend の上限（100KB）を超えていないか確認する。"""
    text_bytes = len(text.encode("utf-8"))
    if text_bytes > MAX_TEXT_BYTES:
        raise ValueError(
            f"テキストサイズ ({text_bytes:,} bytes) が "
            f"Comprehend の上限 ({MAX_TEXT_BYTES:,} bytes) を超えています。"
        )


def check_contains_pii(text):
    """テキストに PII が含まれるかを高速判定する。

    ContainsPiiEntities の料金は DetectPiiEntities の 1/50。
    大量ドキュメントのスクリーニングに最適。

    Parameters
    ----------
    text : str
        判定対象のテキスト（英語）

    Returns
    -------
    dict
        ContainsPiiEntities レスポンス
    """
    _check_text_length(text)

    response = comprehend.contains_pii_entities(
        Text=text,
        LanguageCode="en",
    )

    print(f"テキスト: {text[:50]}...")
    print("検出されたPIIラベル:")
    for label in response["Labels"]:
        if label["Score"] > 0.5:
            print(f"  {label['Name']}: {label['Score']:.4f}")
    print()

    return response


def detect_and_redact_pii(text):
    """PII を検出してマスキングする。

    Parameters
    ----------
    text : str
        マスキング対象のテキスト（英語）

    Returns
    -------
    str
        マスキング済みテキスト
    """
    _check_text_length(text)

    response = comprehend.detect_pii_entities(
        Text=text,
        LanguageCode="en",
    )

    print(f"元テキスト: {text}")

    # PII エンティティをマスキング
    # オフセットがずれないよう、後ろから置換
    redacted_text = text
    entities = sorted(
        response["Entities"],
        key=lambda x: x["BeginOffset"],
        reverse=True,
    )

    for entity in entities:
        begin = entity["BeginOffset"]
        end = entity["EndOffset"]
        pii_type = entity["Type"]
        redacted_text = (
            redacted_text[:begin]
            + f"[{pii_type}]"
            + redacted_text[end:]
        )

    print(f"編集後:     {redacted_text}")
    print()

    return redacted_text


# ---------------------------------------------------------------------------
# メイン実行
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    check_contains_pii(
        "Hello, my name is John Smith and my email is john@example.com."
    )
    check_contains_pii(
        "The weather is sunny today. It's a great day for a walk."
    )

    detect_and_redact_pii(
        "Hello John Smith. Your credit card 1111-0000-1111-0008 "
        "has a minimum payment of $24.53 due by July 31st."
    )
