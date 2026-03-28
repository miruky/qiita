# Amazon Bedrock（Qiita 連載シリーズ）

Qiita 連載「Amazon Bedrock」シリーズ（#5〜#7）のコードをまとめたディレクトリです。

> **注意**: #1〜#4 は主にコンソール操作中心のため、コードの抽出対象外としています。

## ファイル一覧

| ファイル | 記事 | 説明 |
|:--|:--|:--|
| guardrails/converse_with_guardrail.py | #5 | Converse API にガードレールを適用して推論する |
| guardrails/knowledge_base_with_guardrail.py | #5 | Knowledge Bases（RAG）にガードレールを適用する |
| guardrails/blocked_words.txt | #5 | ワードフィルター用 NG ワードリスト（サンプル） |
| agentcore/agent.py | #6 | Strands Agents で実装したカスタマーサポートエージェント |
| agentcore/main.py | #6 | AgentCore Runtime 用エントリポイント |
| agentcore/requirements.txt | #6 | AgentCore デプロイ用の依存パッケージ |
| agentcore/invoke_agent_runtime.py | #6 | boto3 で AgentCore Runtime を呼び出すサンプル |
| agentcore/gateway_agent.py | #6 | AgentCore Gateway 経由でツールを接続するサンプル |
| memory/short_term_memory.py | #7 | AgentCore Memory — 短期記憶の実装 |
| memory/long_term_memory.py | #7 | AgentCore Memory — セマンティック（長期）記憶の実装 |
| memory/episodic_memory.py | #7 | AgentCore Memory — エピソード記憶の実装 |
| memory/multi_agent.py | #7 | Strands Agents によるマルチエージェント構成の実装例 |
