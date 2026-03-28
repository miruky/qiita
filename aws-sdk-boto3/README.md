# AWS SDK for Python (Boto3)（Qiita 連載シリーズ）

Qiita 連載「AWS SDK (Boto3)」シリーズ（全6回）のコードをまとめたディレクトリです。

## ファイル一覧

| ファイル | 記事 | 説明 |
|:--|:--|:--|
| getting_started.py | #1 | 基本的な API 呼び出し（S3/EC2/STS/IAM/リージョン一覧） |
| session_client_resource.py | #2 | Session・Client・Resource の使い分けとコード例 |
| paginator_waiter.py | #2 | Paginator によるページネーションと Waiter による状態待ち |
| s3_bucket_operations.py | #3 | S3 バケットの作成・一覧・存在確認・削除 |
| s3_object_operations.py | #3 | S3 オブジェクトのアップロード・ダウンロード・コピー・削除 |
| s3_presigned_url.py | #3 | 署名付き URL（ダウンロード/アップロード/POST）の生成 |
| s3_multipart_transfer.py | #3 | TransferConfig を使ったマルチパートアップロード |
| s3_bucket_config.py | #3 | バケットポリシー・CORS・ライフサイクルルールの設定 |
| dynamodb_table_setup.py | #4 | DynamoDB テーブル作成（GSI 付き含む） |
| dynamodb_crud.py | #4 | DynamoDB の Put/Get/Update/Delete 操作 |
| dynamodb_query_scan.py | #4 | Query・Scan・パラレル Scan |
| dynamodb_batch.py | #4 | バッチ書き込み・バッチ読み込み・バッチ削除 |
| lambda_operations.py | #5 | Lambda 関数の作成・同期/非同期呼び出し・更新 |
| sqs_operations.py | #5 | SQS キュー作成・メッセージ送受信・DLQ 設定 |
| sns_operations.py | #5 | SNS トピック作成・サブスクリプション・メッセージ発行 |
| event_driven_patterns.py | #5 | SNS→SQS ファンアウト、SQS→Lambda、S3→Lambda 連携 |
| error_handling.py | #6 | ClientError/BotoCoreError のハンドリングパターン |
| retry_strategies.py | #6 | リトライモード設定とカスタムリトライ戦略 |
| performance_optimization.py | #6 | 接続プーリング・スレッド並列・バッチ処理・Lambda 最適化 |
