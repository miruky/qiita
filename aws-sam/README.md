# AWS SAM（Qiita 連載シリーズ）

Qiita 連載「AWS SAM」シリーズ（全6回）のコードをまとめたディレクトリです。

## ファイル一覧

### #1 Hello World

| ファイル | 説明 |
|:--|:--|
| 01-hello-world/template.yaml | Hello World SAMテンプレート |
| 01-hello-world/hello_world/app.py | Hello World Lambda関数 |

### #2 テンプレート構造・Globals

| ファイル | 説明 |
|:--|:--|
| 02-template-structure/template.yaml | Globalsを活用したマルチ関数テンプレート |

### #3 リソースタイプ

| ファイル | 説明 |
|:--|:--|
| 03-resource-types/statemachine/order.asl.json | Step Functions ASL定義（DefinitionSubstitutions使用） |

### #4 SAM CLI

| ファイル | 説明 |
|:--|:--|
| 04-sam-cli/samconfig.toml | 環境別設定（default / staging / prod） |

### #5 ローカル開発

| ファイル | 説明 |
|:--|:--|
| 05-local-development/events/api-event.json | API Gatewayテストイベント |
| 05-local-development/events/dynamodb-event.json | DynamoDB Streamsテストイベント |
| 05-local-development/.vscode/launch.json | VS Code Pythonデバッグ設定 |

### #6 REST API + CI/CD（rest-api-app/）

| ファイル | 説明 |
|:--|:--|
| rest-api-app/template.yaml | CRUD API SAMテンプレート（5関数 + Connectors） |
| rest-api-app/samconfig.toml | 環境別設定（dev / staging / prod） |
| rest-api-app/src/utils/response.py | レスポンスヘルパー |
| rest-api-app/src/handlers/list_items.py | GET /items ハンドラー |
| rest-api-app/src/handlers/create_item.py | POST /items ハンドラー |
| rest-api-app/src/handlers/get_item.py | GET /items/{id} ハンドラー |
| rest-api-app/src/handlers/update_item.py | PUT /items/{id} ハンドラー |
| rest-api-app/src/handlers/delete_item.py | DELETE /items/{id} ハンドラー |
| rest-api-app/events/create-item.json | POST テストイベント |
| rest-api-app/events/get-item.json | GET テストイベント |
| rest-api-app/events/list-items.json | LIST テストイベント |
| rest-api-app/.github/workflows/pipeline.yml | GitHub Actions CI/CDパイプライン |

## シリーズ構成

| 回 | テーマ |
|:--|:--|
| #1 | SAMって何？サーバーレス開発の第一歩を踏み出してみる |
| #2 | SAMテンプレートのGlobals・TransformとCloudFormationの違いを整理してみる |
| #3 | Function・Api・TableなどSAMリソースタイプを一通り使ってみる |
| #4 | SAM CLIのinit・build・deploy・syncを一通り使ってみる |
| #5 | sam localでローカル開発・テスト・デバッグしてみる |
| #6 | REST APIアプリを構築してCI/CDパイプラインまで通してみる |
