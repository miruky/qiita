# =============================================================================
# Amazon Bedrock #6 — Strands Agents で実装したカスタマーサポートエージェント
# =============================================================================
# Qiita 記事: 【Amazon Bedrock #6】AgentCoreを使ってAIエージェントの本番運用基盤を
#              構築してみる
#
# 必要パッケージ:
#   pip install strands-agents strands-agents-tools
# =============================================================================

"""
Strands Agents フレームワークで実装したカスタマーサポート用 AI エージェント。
@tool デコレーターで定義した関数をエージェントが自律的に呼び出す。
"""

from strands import Agent, tool


@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """通貨を変換します。金額、変換元通貨、変換先通貨を指定してください。"""
    # サンプルのレート（本番では API 等から取得）
    rates = {
        ("USD", "JPY"): 150.0,
        ("JPY", "USD"): 1 / 150.0,
        ("EUR", "JPY"): 162.0,
        ("JPY", "EUR"): 1 / 162.0,
    }
    rate = rates.get((from_currency, to_currency))
    if rate is None:
        return f"{from_currency} → {to_currency} の変換レートは登録されていません。"
    result = amount * rate
    return f"{amount} {from_currency} = {result:.2f} {to_currency}"


@tool
def get_business_hours() -> str:
    """営業時間を返します。"""
    return "当社の営業時間は平日9:00〜18:00です。土日祝日はお休みをいただいております。"


# エージェントの作成
agent = Agent(
    system_prompt="""あなたは親切で丁寧なカスタマーサポートのAIアシスタントです。
以下のルールに従ってください：
1. 必ず日本語で回答してください。
2. 利用可能なツールを適切に使って正確に回答してください。
3. ツールで対応できない質問には、正直に「お答えできません」と伝えてください。
4. 回答は簡潔かつ丁寧にしてください。""",
    tools=[convert_currency, get_business_hours],
)


# ローカルテスト用
if __name__ == "__main__":
    response = agent("100ドルは日本円でいくらですか？")
    print(response)

    response = agent("営業時間を教えてください。")
    print(response)
