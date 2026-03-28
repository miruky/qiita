# =============================================================================
# Amazon Bedrock #7 — AgentCore Memory: セマンティック（長期）記憶の実装
# =============================================================================
# Qiita 記事: 【Amazon Bedrock #7】AgentCore応用編 ― Stateful Runtimeとメモリ機能で
#              高度なエージェントを実現する
#
# 必要パッケージ:
#   pip install strands-agents bedrock-agentcore
#
# 注意: 長期記憶の抽出・統合は非同期処理で行われ、完了まで約 20〜40 秒かかる。
#       即時の文脈参照には短期記憶を使い、長期記憶はバックグラウンドで蓄積される。
# =============================================================================

"""
AgentCore Memory のセマンティック（長期）記憶を実装するサンプル。
セッションをまたいでユーザーの好みや過去のやり取りを記憶し、
パーソナライズされた対応を実現する。
"""

from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import (
    AgentCoreMemorySessionManager,
)
from strands import Agent, tool

# ---------------------------------------------------------------------------
# 1. メモリリソースの作成（セマンティック + ユーザー好み戦略）
# ---------------------------------------------------------------------------


def create_long_term_memory(region: str = "ap-northeast-1") -> str:
    """セマンティック + ユーザー好み戦略のメモリリソースを作成する。

    Returns:
        作成されたメモリの ID
    """
    client = MemoryClient(region_name=region)

    memory = client.create_memory_and_wait(
        name="customer-support-memory",
        strategies=[
            {
                "semanticMemoryStrategy": {
                    "name": "facts",
                    "namespaces": ["/support/facts/"],
                }
            },
            {
                "userPreferenceMemoryStrategy": {
                    "name": "prefs",
                    "namespaces": ["/support/preferences/"],
                }
            },
        ],
        event_expiry_days=30,  # イベントの保持期間（日数）
    )

    memory_id = memory["id"]
    print(f"Memory ID: {memory_id}")
    return memory_id


# ---------------------------------------------------------------------------
# 2. ツールの定義
# ---------------------------------------------------------------------------


@tool
def lookup_product(product_name: str) -> str:
    """商品情報を検索します。"""
    products = {
        "ワイヤレスイヤホン": "価格: 8,980円 / カラー: ブラック, ホワイト / 在庫あり",
        "モバイルバッテリー": "価格: 3,480円 / 容量: 10000mAh / 在庫あり",
    }
    return products.get(product_name, f"「{product_name}」は見つかりませんでした。")


# ---------------------------------------------------------------------------
# 3. 長期記憶付きエージェントの作成
# ---------------------------------------------------------------------------


def create_agent_with_memory(
    memory_id: str,
    session_id: str,
    actor_id: str,
    region: str = "ap-northeast-1",
) -> Agent:
    """長期記憶付きエージェントを作成する。

    Args:
        memory_id: 作成済みのメモリ ID
        session_id: セッション ID
        actor_id: ユーザー ID（actor_id ごとにメモリが分離される）
        region: AWS リージョン

    Returns:
        長期記憶付き Agent
    """
    memory_config = AgentCoreMemoryConfig(
        memory_id=memory_id,
        session_id=session_id,
        actor_id=actor_id,
    )
    session_manager = AgentCoreMemorySessionManager(
        agentcore_memory_config=memory_config,
        region_name=region,
    )

    return Agent(
        system_prompt="""あなたは親切で丁寧なカスタマーサポートのAIアシスタントです。
ユーザーの好みや過去の情報を記憶し、パーソナライズされた対応を心がけてください。""",
        tools=[lookup_product],
        session_manager=session_manager,
    )


# ---------------------------------------------------------------------------
# 4. セッションをまたいだ記憶の活用デモ
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    MEMORY_ID = "作成したメモリID"  # ← 置き換えてください

    # === セッション1（3月1日） ===
    print("=== セッション 1 ===")
    agent_s1 = create_agent_with_memory(
        memory_id=MEMORY_ID,
        session_id="s1-20260301",
        actor_id="user-tanaka",
    )

    response = agent_s1("日本語で回答してほしいです。あと、ブラックのイヤホンが好きです。")
    print(response)
    # → preferences 戦略により「言語: 日本語」「好み: ブラック」が長期記憶に保存

    # === セッション2（3月5日 — 別セッション） ===
    print("\n=== セッション 2 ===")
    agent_s2 = create_agent_with_memory(
        memory_id=MEMORY_ID,
        session_id="s2-20260305",
        actor_id="user-tanaka",
    )

    response = agent_s2("おすすめのイヤホンはありますか？")
    print(response)
    # → 長期記憶から「ブラックが好み」を取得し、
    #   「ワイヤレスイヤホン（ブラック）がおすすめです。」と回答
