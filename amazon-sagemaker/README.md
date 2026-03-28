# Amazon SageMaker AI（Qiita 連載シリーズ）

Qiita 連載「Amazon SageMaker AI」シリーズ（全8回）のコードをまとめたディレクトリです。

> **注意**: #1 は概要解説のためコードなし。#2 以降のハンズオンコードを収録しています。

## ファイル一覧

| ファイル | 記事 | 説明 |
|:--|:--|:--|
| studio/sagemaker_api_basics.py | #2 | SageMaker SDK / boto3 の基本操作（セッション情報・S3・JumpStart モデル一覧） |
| processing/prepare_sample_data.py | #3 | Adult Census Income 風サンプルデータの作成と EDA |
| processing/preprocessing.py | #3 | Processing Job で実行するデータ前処理スクリプト |
| processing/run_processing_job.py | #3 | Processing Job の起動と結果確認 |
| processing/feature_engineering.py | #3 | 特徴量エンジニアリングと重要度分析 |
| training/train_xgboost.py | #4 | XGBoost 組み込みアルゴリズムでの二値分類トレーニング |
| training/hyperparameter_tuning.py | #4 | ベイズ最適化によるハイパーパラメータチューニング |
| training/autopilot.py | #4 | SageMaker Autopilot（AutoML）の実行 |
| inference/deploy_realtime_endpoint.py | #5 | リアルタイム推論エンドポイントのデプロイと推論 |
| inference/deploy_serverless_endpoint.py | #5 | サーバーレスエンドポイントのデプロイとコールドスタート計測 |
| inference/run_batch_transform.py | #5 | バッチ変換による一括推論 |
| inference/evaluate_model.py | #5 | モデル精度の評価（Accuracy / Precision / Recall / F1 / AUC） |
| inference/cleanup_endpoints.py | #5 | エンドポイント・モデルの一括削除 |
| pipelines/evaluation.py | #6 | パイプライン用モデル評価スクリプト（Processing Job 内で実行） |
| pipelines/build_pipeline.py | #6 | SageMaker Pipelines パイプライン定義・実行 |
| pipelines/model_registry.py | #6 | Model Registry の確認と承認 |
| jumpstart/deploy_and_generate.py | #7 | JumpStart で Llama 3.1 をデプロイしてテキスト生成 |
| jumpstart/finetune_text_classifier.py | #7 | DistilBERT のファインチューニング（感情分析） |
| bedrock_integration/review_analysis.py | #8 | SageMaker で前処理 → Bedrock Claude で分析 |
| bedrock_integration/vector_search.py | #8 | Bedrock Titan Embeddings でベクトル検索 |
| bedrock_integration/bedrock_analysis.py | #8 | Processing Job 内で Bedrock を呼び出すスクリプト |
| bedrock_integration/bedrock_pipeline.py | #8 | SageMaker Pipelines + Bedrock 連携パイプライン |
| bedrock_integration/hybrid_inference.py | #8 | SageMaker カスタムモデル + Bedrock の ハイブリッド推論 |
| bedrock_integration/cleanup_all.py | #8 | シリーズ全体のリソース一括クリーンアップ |
