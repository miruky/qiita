# Amazon Comprehend シリーズ — コードポートフォリオ

Amazon Comprehend の Qiita 記事シリーズ（#1〜#5）で使用したコードをまとめたリポジトリです。

## シリーズ概要

| 記事 | テーマ |
|:--|:--|
| #1 | Comprehend の全体像をつかむ（概要のみ・コードなし） |
| #2 | 感情分析・エンティティ抽出・キーフレーズ抽出 |
| #3 | カスタム分類とカスタムエンティティ認識 |
| #4 | PII 検出・毒性検出・プロンプト安全性分類 |
| #5 | Bedrock と Comprehend を組み合わせた高度なテキスト分析 |

## ファイル構成

```
amazon-comprehend/
├── README.md
├── scripts/
│   ├── text_analysis_basics.py        # #2 感情分析・エンティティ・キーフレーズ・構文解析
│   ├── batch_and_async.py             # #2 バッチ処理・非同期ジョブ
│   ├── custom_classifier.py           # #3 カスタムドキュメント分類器の作成
│   ├── custom_entity_recognizer.py    # #3 カスタムエンティティ認識器の作成
│   ├── model_deploy_and_inference.py  # #3 エンドポイントのデプロイと推論
│   ├── flywheel_management.py         # #3 Flywheel によるモデル継続改善
│   ├── pii_detection.py              # #4 PII 検出とマスキング
│   ├── toxicity_and_safety.py        # #4 毒性検出・プロンプト安全性・コンテンツモデレーション
│   ├── bedrock_guardrail.py          # #5 Bedrock 入出力ガードレールパイプライン
│   ├── rag_pii_processor.py          # #5 RAG ドキュメントの PII マスキング
│   └── conversation_analyzer.py      # #5 会話ログ分析とコンテキストスコアリング
├── lambda/
│   └── safety_check_handler.py       # #4 リアルタイム安全性チェック Lambda
├── config/
│   └── lambda-iam-policy.json        # #4 Lambda 用 IAM ポリシー
└── data/
    ├── training-data-classification.csv  # #3 分類トレーニングデータ（サンプル）
    └── entity-list.csv                   # #3 エンティティリスト（サンプル）
```

## 元記事からの修正点

| 修正箇所 | 内容 |
|:--|:--|
| PII 検出（#4, #5） | `detect_pii_entities` 呼び出し前に 100KB テキスト長チェックを追加 |
| プロンプト安全性（#4） | エンドポイントのリージョン可用性に関する注記を追加 |

## 前提条件

- Python 3.9+
- boto3
- AWS アカウントと適切な IAM 権限
- カスタム分類器を使う場合は S3 にトレーニングデータをアップロード済みであること

## セットアップ

```bash
pip install boto3
aws configure
```

## 注意事項

- `data/` ディレクトリのファイルはサンプルデータです。実際のトレーニングには十分な量のデータが必要です
- プロンプト安全性分類（`classify_document` with prompt-safety）は一部リージョンでのみ利用可能です
- Comprehend の API にはテキストサイズの上限（多くの API で 100KB）があります
