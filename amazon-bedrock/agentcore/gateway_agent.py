# =============================================================================
# Amazon Bedrock #6 — AgentCore Gateway 経由でツールを接続するサンプル
# =============================================================================
# Qiita 記事: 【Amazon Bedrock #6】AgentCoreを使ってAIエージェントの本番運用基盤を
#              構築してみる
#
# 必要パッケージ:
#   pip install strands-agents bedrock-agentcore
# =============================================================================

"""
AgentCore Gateway 経由で Lambda 関数や外部 API をエージェントに接続するサンプル。
Gateway は Lambda、API、MCP サーバー等のツールを一元管理するコンポーネント。
"""

from strands import Agent
from bedrock_agentcore.gateway import GatewayClient


def create_gateway_agent(
    gateway_id: str,
    region: str = "ap-northeast-1",
) -> Agent:
    """Gateway 経由でツールを取得し、エージェントを作成する。

    Args:
        gateway_id: AgentCore Gateway ID
        region: AWS リージョン

    Returns:
        Gateway ツールが統合された Agent
    """
    # Gateway 経由でツールを取得
    gateway = GatewayClient(region_name=region)
    gateway_tools = gateway.get_tools(gateway_id=gateway_id)

    # Gateway のツールを含むエージェント
    agent = Agent(
        system_prompt="あなたは親切なカスタマーサポートのAIアシスタントです。",
        tools=gateway_tools,
    )
    return agent


def main():
    GATEWAY_ID = "GATEWAY_ID"  # ← 作成した Gateway ID に置き換えてください

    agent = create_gateway_agent(gateway_id=GATEWAY_ID)
    response = agent("注文番号ORD-001を検索してください。")
    print(response)


if __name__ == "__main__":
    main()
