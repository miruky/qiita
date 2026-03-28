# =============================================================================
# Amazon Bedrock #5 — Knowledge Bases（RAG）にガードレールを適用する
# =============================================================================
# Qiita 記事: 【Amazon Bedrock #5】ガードレールで生成AIの安全性を確保してみる
#
# **重要**: Knowledge Bases の retrieve / retrieve_and_generate は
#   bedrock-agent-runtime クライアントを使用します（bedrock-runtime ではない）。
# 必要な boto3 バージョン: >= 1.34.0
# =============================================================================

"""
Knowledge Bases（RAG）にガードレールを適用して推論するサンプル。
retrieve_and_generate API に guardrailConfiguration を渡すことで、
RAG 応答にもガードレールが適用される。
"""

import boto3


def retrieve_and_generate_with_guardrail(
    query: str,
    knowledge_base_id: str,
    model_arn: str,
    guardrail_id: str,
    guardrail_version: str = "1",
    region: str = "ap-northeast-1",
) -> dict:
    """Knowledge Bases + Guardrail でRAG推論を実行する。

    Args:
        query: ユーザーの質問テキスト
        knowledge_base_id: ナレッジベース ID
        model_arn: 使用するモデルの ARN
        guardrail_id: ガードレール ID
        guardrail_version: ガードレールのバージョン
        region: AWS リージョン

    Returns:
        API レスポンスの dict
    """
    # 注意: bedrock-agent-runtime クライアントを使用すること
    client = boto3.client("bedrock-agent-runtime", region_name=region)

    response = client.retrieve_and_generate(
        input={"text": query},
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": knowledge_base_id,
                "modelArn": model_arn,
                "guardrailConfiguration": {
                    "guardrailId": guardrail_id,
                    "guardrailVersion": guardrail_version,
                },
            },
        },
    )

    return response


def main():
    # --- 設定（すべてご自身の値に置き換えてください） ---
    KB_ID = "KB_ID"
    MODEL_ARN = "arn:aws:bedrock:ap-northeast-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
    GUARDRAIL_ID = "GUARDRAIL_ID"

    query = "返品について教えて"
    print(f"質問: {query}")

    response = retrieve_and_generate_with_guardrail(
        query=query,
        knowledge_base_id=KB_ID,
        model_arn=MODEL_ARN,
        guardrail_id=GUARDRAIL_ID,
    )

    output_text = response["output"]["text"]
    print(f"回答: {output_text}")

    # 引用元の表示
    if "citations" in response:
        print("\n引用元:")
        for citation in response["citations"]:
            for ref in citation.get("retrievedReferences", []):
                print(f"  - {ref['location']['s3Location']['uri']}")


if __name__ == "__main__":
    main()
