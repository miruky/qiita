# =============================================================================
# Amazon Bedrock #7 — AgentCore Memory: 短期記憶の実装
# =============================================================================
# Qiita 記事: 【Amazon Bedrock #7】AgentCore応用編 ― Stateful Runtimeとメモリ機能で
#              高度なエージェントを実現する
#
# 必要パッケージ:
#   pip install strands-agents bedrock-agentcore
# =============================================================================

"""
AgentCore Memory の短期記憶（セッション内の文脈保持）を実装するサンプル。
短期記憶により、マルチターン対話で前の発言を踏まえた回答が可能になる。
"""

import os
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import (
    AgentCoreMemorySessionManager,
)
from strands import Agent, tool

# ---------------------------------------------------------------------------
# 1. Memory Client の初期化
# ---------------------------------------------------------------------------

# メモリ ID は事前に AgentCore コンソールまたは API で作成
MEMORY_ID = os.getenv("MEMORY_ID", "your-memory-id")
SESSION_ID = "session-001"
ACTOR_ID = "user-tanaka"

# Memory Client の初期化
client = MemoryClient(region_name="ap-northeast-1")

# メモリ設定
memory_config = AgentCoreMemoryConfig(
    memory_id=MEMORY_ID,
    session_id=SESSION_ID,
    actor_id=ACTOR_ID,
)

# セッションマネージャーの作成
session_manager = AgentCoreMemorySessionManager(
    agentcore_memory_config=memory_config,
    region_name="ap-northeast-1",
)

# ---------------------------------------------------------------------------
# 2. ツールの定義
# ---------------------------------------------------------------------------


@tool
def get_order_status(order_id: str) -> str:
    """注文のステータスを取得します。"""
    statuses = {
        "ORD-001": "配送中（2026年3月5日到着予定）",
        "ORD-002": "出荷準備中（2026年3月7日到着予定）",
    }
    return statuses.get(order_id, f"注文番号 {order_id} は見つかりませんでした。")


# ---------------------------------------------------------------------------
# 3. 短期記憶付きエージェント
# ---------------------------------------------------------------------------

agent = Agent(
    system_prompt="""あなたは親切で丁寧なカスタマーサポートのAIアシスタントです。
会話の文脈を記憶し、前の発言を踏まえて回答してください。""",
    tools=[get_order_status],
    session_manager=session_manager,  # ← 短期記憶を付与
)

# ---------------------------------------------------------------------------
# 4. 動作確認
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # 1回目の質問
    response = agent("注文番号ORD-001の状況を教えてください。")
    print(response)
    # → 「ご注文番号 ORD-001 は現在「配送中」で、2026年3月5日到着予定です。」

    # 2回目の質問（文脈を参照 — 「届く」が ORD-001 を指すことを理解）
    response = agent("届くのが遅れる場合はどうなりますか？")
    print(response)
