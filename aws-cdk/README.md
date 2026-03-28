# AWS CDK（Qiita 連載シリーズ）

Qiita 連載「AWS CDK」シリーズ（全7回）のコードをまとめたディレクトリです。

## ファイル一覧

| ファイル | 記事 | 説明 |
|:--|:--|:--|
| 01-overview/comparison-cdk.ts | #1 | S3 + Lambda + API Gateway を CDK で定義する比較例 |
| 02-first-stack/bin/my-first-cdk.ts | #2 | CDK アプリのエントリーポイント |
| 02-first-stack/lib/my-first-cdk-stack.ts | #2 | S3 + DynamoDB + CfnOutput のスタック定義 |
| 03-constructs/lib/l1-example-stack.ts | #3 | L1 コンストラクト（CfnBucket）の例 |
| 03-constructs/lib/l2-example-stack.ts | #3 | L2 コンストラクト（Bucket）の例 + L1/L2 Lambda 比較 |
| 03-constructs/lib/l3-example-stack.ts | #3 | L3 コンストラクト（LambdaRestApi）の例 |
| 03-constructs/lib/escape-hatch-examples.ts | #3 | エスケープハッチ（L2 → L1 降格）の例 |
| 03-constructs/constructs/data-processor.ts | #3 | カスタムコンストラクトの作成例 |
| 04-serverless-api/bin/cdk-serverless-api.ts | #4 | サーバーレス API のエントリーポイント（環境分離） |
| 04-serverless-api/lib/cdk-serverless-api-stack.ts | #4 | DynamoDB + Lambda + API Gateway のスタック定義 |
| 04-serverless-api/lambda/list-items.ts | #4 | GET /items ハンドラー |
| 04-serverless-api/lambda/create-item.ts | #4 | POST /items ハンドラー |
| 04-serverless-api/lambda/get-item.ts | #4 | GET /items/{id} ハンドラー |
| 04-serverless-api/lambda/update-item.ts | #4 | PUT /items/{id} ハンドラー |
| 04-serverless-api/lambda/delete-item.ts | #4 | DELETE /items/{id} ハンドラー |
| 05-event-driven/lib/event-driven-stack.ts | #5 | DynamoDB Streams + SNS + SQS + EventBridge のスタック |
| 05-event-driven/lambda/stream-processor.ts | #5 | DynamoDB Streams 処理 Lambda |
| 06-testing-aspects/test/assertions.test.ts | #6 | Fine-Grained Assertions テスト |
| 06-testing-aspects/test/snapshot.test.ts | #6 | スナップショットテスト |
| 06-testing-aspects/test/aspects.test.ts | #6 | Aspects のテスト |
| 06-testing-aspects/lib/aspects/tagging-aspect.ts | #6 | タグ付け Aspect |
| 06-testing-aspects/lib/aspects/bucket-versioning-checker.ts | #6 | S3 バージョニング / 暗号化チェック Aspect |
| 06-testing-aspects/lib/stacks/network-stack.ts | #6 | マルチスタック設計: ネットワーク |
| 06-testing-aspects/lib/stacks/application-stack.ts | #6 | マルチスタック設計: アプリケーション |
| 07-cdk-pipelines/bin/pipeline-app.ts | #7 | CDK Pipelines エントリーポイント |
| 07-cdk-pipelines/lib/pipeline-stack.ts | #7 | セルフミューテーティングパイプライン（3ステージ） |
| 07-cdk-pipelines/lib/application-stage.ts | #7 | アプリケーションステージ定義 |

## シリーズ構成

| 回 | テーマ |
|:--|:--|
| #1 | CDKって何？CloudFormation・SAMとの違いを整理してみる |
| #2 | CDKプロジェクトを作成して最初のスタックをデプロイしてみる |
| #3 | L1・L2・L3コンストラクトを使い分けてみる |
| #4 | S3・Lambda・API GatewayでサーバーレスAPIを構築してみる |
| #5 | DynamoDB・SQS・SNSでイベント駆動アーキテクチャを作ってみる |
| #6 | CDKのテスト・Aspects・ベストプラクティスをまとめてみる |
| #7 | CDK PipelinesとCodeシリーズでCI/CDパイプラインを構築してみる |
