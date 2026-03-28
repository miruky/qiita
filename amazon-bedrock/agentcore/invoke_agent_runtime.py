# =============================================================================
# Amazon Bedrock #6 — boto3 で AgentCore Runtime を呼び出すサンプル
# =============================================================================
# Qiita 記事: 【Amazon Bedrock #6】AgentCoreを使ってAIエージェントの本番運用基盤を
#              構築してみる
#
# 必要な boto3 バージョン: >= 1.36.0 (bedrock-agentcore クライアント対応)
#
# 注意: AgentCore Runtime は curl で直接 HTTP アクセスするのではなく、
#       AWS SDK (boto3) を使って AWS 認証 (SigV4署名) 付きで呼び出す。
# =============================================================================

"""
デプロイ済みの AgentCore Runtime エージェントを boto3 経由で呼び出すサンプル。
"""

import boto3
import json
import uuid


def invoke_agentcore_runtime(
    agent_runtime_arn: str,
    prompt: str,
    session_id: str | None = None,
    region: str = "ap-northeast-1",
) -> dict:
    """AgentCore Runtime にデプロイしたエージェントを呼び出す。

    Args:
        agent_runtime_arn: デプロイ時に発行されたランタイム ARN
        prompt: ユーザーの入力テキスト
        session_id: セッション ID（33文字以上）。None の場合は自動生成
        region: AWS リージョン

    Returns:
        エージェントのレスポンス dict
    """
    client = boto3.client("bedrock-agentcore", region_name=region)

    payload = json.dumps({"prompt": prompt})

    # セッション ID（33文字以上必要。新しい ID で新しいセッションが開始される）
    if session_id is None:
        session_id = "session-" + str(uuid.uuid4())

    response = client.invoke_agent_runtime(
        agentRuntimeArn=agent_runtime_arn,
        runtimeSessionId=session_id,
        payload=payload,
    )

    response_body = response["response"].read()
    response_data = json.loads(response_body)
    return response_data


def main():
    # --- 設定 ---
    RUNTIME_ARN = "arn:aws:bedrock-agentcore:ap-northeast-1:{account_id}:runtime/main-XXXXXXX"

    result = invoke_agentcore_runtime(
        agent_runtime_arn=RUNTIME_ARN,
        prompt="100ドルは日本円でいくらですか？",
    )
    print("Agent Response:", result)


if __name__ == "__main__":
    main()
