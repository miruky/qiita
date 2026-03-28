# =============================================================================
# Amazon Bedrock #7 — Strands Agents によるマルチエージェント構成の実装例
# =============================================================================
# Qiita 記事: 【Amazon Bedrock #7】AgentCore応用編 ― Stateful Runtimeとメモリ機能で
#              高度なエージェントを実現する
#
# 必要パッケージ:
#   pip install strands-agents
#
# マルチエージェント: 複数の専門エージェントが協調して1つのタスクを処理する
# アーキテクチャ。Manager Agent が各専門エージェントにタスクを委任する。
# =============================================================================

"""
Strands Agents フレームワークを使ったマルチエージェント構成のサンプル（概念実装）。
Manager Agent が情報収集エージェントと分析エージェントにタスクを委任し、
結果を統合してユーザーに報告する。
"""

from strands import Agent, tool


# === Agent A: 情報収集エージェント ===
@tool
def search_database(query: str) -> str:
    """社内データベースを検索します。"""
    return f"「{query}」に関する検索結果: ..."


info_agent = Agent(
    system_prompt="あなたは情報収集の専門家です。指示に従いデータを検索してください。",
    tools=[search_database],
)


# === Agent B: 分析エージェント ===
@tool
def analyze_data(data: str) -> str:
    """データを分析し、要約を返します。"""
    return f"分析結果: {data} の傾向は..."


analysis_agent = Agent(
    system_prompt="あなたはデータ分析の専門家です。与えられたデータを分析してください。",
    tools=[analyze_data],
)


# === Manager Agent: 統括エージェント ===
@tool
def delegate_to_info_agent(query: str) -> str:
    """情報収集エージェントにタスクを委任します。"""
    response = info_agent(query)
    return str(response)


@tool
def delegate_to_analysis_agent(data: str) -> str:
    """分析エージェントにタスクを委任します。"""
    response = analysis_agent(data)
    return str(response)


manager_agent = Agent(
    system_prompt="""あなたは複数の専門エージェントを統括するマネージャーです。
ユーザーの要求に応じて、適切な専門エージェントにタスクを委任してください。
1. 情報が必要な場合 → 情報収集エージェントに委任
2. 分析が必要な場合 → 分析エージェントに委任
3. 結果を統合してユーザーに報告してください。""",
    tools=[delegate_to_info_agent, delegate_to_analysis_agent],
)


if __name__ == "__main__":
    # 実行
    response = manager_agent("先月の売上データを調べて、傾向を分析してください。")
    print(response)
