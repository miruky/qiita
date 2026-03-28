# AWS Code Series サンプルコード集

Qiita連載「AWS Codeシリーズ」（全12回）のサンプルコードをまとめたリポジトリです。

## 記事一覧

| # | タイトル | ディレクトリ |
|:--|:--|:--|
| 1 | CI/CDって何？AWS Codeシリーズの全体像をつかんでみる | （コードなし） |
| 2 | CodeCommitの非推奨化とGitHubへの移行を整理してみる | （コードなし） |
| 3 | CodeBuildではじめてのビルドプロジェクトを作ってみる | `03-first-build/` |
| 4 | buildspec.ymlを深掘りしてCodeBuildを高速化してみる | `04-buildspec-deep-dive/` |
| 5 | CodeDeployでEC2にアプリをデプロイしてみる | `05-codedeploy-ec2/` |
| 6 | In-PlaceとBlue/Greenのデプロイ戦略を比較してみる | （コードなし） |
| 7 | CodeDeployでECS・Lambdaにカナリアデプロイしてみる | `07-ecs-lambda-deploy/` |
| 8 | CodePipelineではじめてのCI/CDパイプラインを組んでみる | （コードなし） |
| 9 | CodePipeline V2のトリガー・変数・手動承認を使ってみる | `09-pipeline-v2/` |
| 10 | CodePipelineでマルチステージ・クロスアカウント構成を作ってみる | `10-multi-stage/` |
| 11 | CI/CDパイプラインをゼロから一気に構築してみる | `11-e2e-handson/` |
| 12 | セキュリティ・コスト・モニタリングの運用ベストプラクティスまとめ | `12-best-practices/` |

## 主要ファイル

### CodeBuild（#3, #4）
- `buildspec.yml` — ビルド仕様ファイル（基礎〜Docker/ECR/バッチビルド/レポート）
- `Dockerfile` — コンテナビルド例

### CodeDeploy（#5, #7）
- `appspec.yml` — EC2/ECS/Lambda各デプロイ仕様
- `scripts/` — ライフサイクルフックスクリプト

### CodePipeline（#9, #10）
- `pipeline-definition.json` — V2パイプラインのIaC定義
- クロスアカウント/クロスリージョン設定例

### 総合ハンズオン（#11）
- GitHub → CodeBuild → CodeDeploy の完全E2Eサンプル

### 運用ベストプラクティス（#12）
- セキュリティ: S3暗号化ポリシー、最小権限IAM、シークレット管理
- コスト最適化: キャッシュ、トリガーフィルタ
- モニタリング: CloudWatch Logs Insightsクエリ

## 注意事項

- サンプルコード内の `123456789012`、`ACCOUNT_ID`、`BUCKET_NAME` 等はプレースホルダーです
- `#10 template.yml` は教材用の簡易版です（VPCId パラメータと RegionMap マッピングは省略）
- 本番利用時は各IAMポリシーを最小権限に調整してください
