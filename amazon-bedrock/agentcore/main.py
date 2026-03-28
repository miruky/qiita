# =============================================================================
# Amazon Bedrock #6 — AgentCore Runtime 用エントリポイント
# =============================================================================
# Qiita 記事: 【Amazon Bedrock #6】AgentCoreを使ってAIエージェントの本番運用基盤を
#              構築してみる
#
# デプロイ手順:
#   agentcore configure --entrypoint main.py
#   agentcore launch
# =============================================================================

"""
AgentCore Runtime にデプロイするためのエントリポイント。
agent.py で定義したエージェントを Runtime 上で動作するようにラップする。
"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from agent import agent

app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload):
    """AgentCore Runtime のエントリポイント"""
    user_message = payload.get("prompt", "Hello")
    response = agent(user_message)
    return {"result": str(response)}


if __name__ == "__main__":
    app.run()
