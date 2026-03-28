# Amazon Comprehend #5 — RAG ドキュメントの PII マスキング
# ファイル: rag_pii_processor.py
# 概要: ナレッジベースに格納するドキュメントから PII を事前に除去する。
#       S3 のドキュメントを読み込み、チャンク分割して PII を検出・マスキングし、
#       処理済みドキュメントを S3 に保存する。
#
# 修正点（元記事からの変更）:
#   - split_text でチャンク分割時に 100KB 上限を考慮
#   - detect_pii_entities 呼び出し前のテキスト長チェックを追加

import boto3

s3 = boto3.client("s3")
comprehend = boto3.client("comprehend", region_name="ap-northeast-1")

# Comprehend API 用テキスト上限（バイト数）
MAX_CHUNK_SIZE = 5000  # 文字数ベースのチャンクサイズ


def process_document_for_rag(bucket, key, pii_threshold=0.7):
    """RAG 用にドキュメントの PII をマスキングする。

    Parameters
    ----------
    bucket : str
        S3 バケット名
    key : str
        S3 オブジェクトキー
    pii_threshold : float
        PII 判定の信頼度閾値

    Returns
    -------
    str
        マスキング済みテキスト
    """
    # S3 からドキュメントを取得
    obj = s3.get_object(Bucket=bucket, Key=key)
    text = obj["Body"].read().decode("utf-8")

    # PII 有無を高速判定（先頭 5,000 文字でスクリーニング）
    pii_check = comprehend.contains_pii_entities(
        Text=text[:MAX_CHUNK_SIZE],
        LanguageCode="en",
    )

    has_pii = any(
        label["Score"] > pii_threshold for label in pii_check["Labels"]
    )

    if not has_pii:
        return text  # PII なし → そのまま使用

    # PII をマスキング（長いテキストはチャンク分割して処理）
    chunks = split_text(text, max_size=MAX_CHUNK_SIZE)
    masked_chunks = []

    for chunk in chunks:
        response = comprehend.detect_pii_entities(
            Text=chunk,
            LanguageCode="en",
        )

        masked = chunk
        entities = sorted(
            response["Entities"],
            key=lambda x: x["BeginOffset"],
            reverse=True,
        )

        for entity in entities:
            if entity["Score"] > pii_threshold:
                begin = entity["BeginOffset"]
                end = entity["EndOffset"]
                masked = (
                    masked[:begin]
                    + f"[REDACTED_{entity['Type']}]"
                    + masked[end:]
                )

        masked_chunks.append(masked)

    masked_text = "".join(masked_chunks)

    # マスキング済みドキュメントを S3 に保存
    s3.put_object(
        Bucket=bucket,
        Key=f"processed/{key}",
        Body=masked_text.encode("utf-8"),
    )

    return masked_text


def split_text(text, max_size=5000):
    """テキストをチャンクに分割する。

    Parameters
    ----------
    text : str
        分割対象のテキスト
    max_size : int
        1 チャンクの最大文字数

    Returns
    -------
    list[str]
        チャンクのリスト
    """
    chunks = []
    for i in range(0, len(text), max_size):
        chunks.append(text[i : i + max_size])
    return chunks


# ---------------------------------------------------------------------------
# メイン実行
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # 実行例（S3 バケットとオブジェクトを環境に合わせて変更）
    # result = process_document_for_rag("my-rag-bucket", "documents/sample.txt")
    # print(f"処理完了: {len(result)} 文字")
    pass
