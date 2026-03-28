# =============================================================================
# Amazon Bedrock #7 — AgentCore Memory: エピソード記憶の実装
# =============================================================================
# Qiita 記事: 【Amazon Bedrock #7】AgentCore応用編 ― Stateful Runtimeとメモリ機能で
#              高度なエージェントを実現する
#
# 必要パッケージ:
#   pip install strands-agents bedrock-agentcore
#
# エピソード記憶: エージェントの過去のタスク実行経験（目標・推論・行動・結果・反省）
# を構造化して保持する仕組み。同じ失敗を繰り返さず、成功体験を活用できる。
# =============================================================================

"""
AgentCore Memory のエピソード記憶を含むメモリリソースを作成するサンプル。
セマンティック + ユーザー好み + エピソード の3戦略を組み合わせる。
"""

from bedrock_agentcore.memory import MemoryClient


def create_episodic_memory(region: str = "ap-northeast-1") -> str:
    """エピソード記憶戦略を含むメモリリソースを作成する。

    Returns:
        作成されたメモリの ID
    """
    client = MemoryClient(region_name=region)

    # エピソード記憶戦略を含むメモリの作成
    memory = client.create_memory_and_wait(
        name="support-agent-episodic-memory",
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
            {
                "episodicMemoryStrategy": {
                    "name": "episodes",
                    "namespaces": ["/support/episodes/"],
                }
            },  # ← エピソード記憶を追加
        ],
        event_expiry_days=30,  # イベントの保持期間（日数）
    )

    memory_id = memory["id"]
    print(f"Memory ID: {memory_id}")
    return memory_id


if __name__ == "__main__":
    memory_id = create_episodic_memory()
    print(f"エピソード記憶付きメモリを作成しました: {memory_id}")
