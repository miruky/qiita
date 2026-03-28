# Terraform 入門シリーズ

Terraform を使った AWS インフラ構築の実践コード集です。  
全 10 回の連載記事に対応しています。

## 記事一覧

| # | タイトル | ディレクトリ | 主なリソース |
|:--|:--|:--|:--|
| 1 | Terraform って何？IaC の全体像と CloudFormation・CDK との違いを整理してみる | `01-overview/` | 比較用コード（CFn / HCL） |
| 2 | Terraform をインストールして最初の AWS リソースをデプロイしてみる | `02-first-deploy/` | S3 バケット |
| 3 | HCL の基本文法を深掘りしてみる | `03-hcl-basics/` | 変数、データソース、dynamic ブロック |
| 4 | VPC・サブネット・セキュリティグループで AWS ネットワークを構築してみる | `04-network/` | VPC, サブネット, NAT GW, SG |
| 5 | EC2・ALB・Auto Scaling で高可用性な Web サーバーを構築してみる | `05-web-server/` | ALB, ASG, 起動テンプレート |
| 6 | S3・Lambda・API Gateway でサーバーレス API を構築してみる | `06-serverless/` | Lambda, API Gateway (HTTP API) |
| 7 | モジュールで再利用可能なインフラ部品を作ってみる | `07-modules/` | VPC モジュール, terraform test |
| 8 | State ファイルの管理とリモートバックエンドを設定してみる | `08-state/` | S3 + DynamoDB バックエンド |
| 9 | Workspaces・tfvars で環境分離と実務のディレクトリ構成を整理してみる | `09-environments/` | 環境分離パターン, Terragrunt |
| 10 | CI/CD パイプラインと terraform test で安全な自動デプロイ環境を構築してみる | `10-cicd/` | GitHub Actions, OPA, Atlantis |

## 前提条件

- Terraform >= 1.14.0
- AWS CLI v2（認証設定済み）
- AWS アカウント（AdministratorAccess 推奨）

## 使い方

```bash
cd terraform/02-first-deploy

# 初期化
terraform init

# 実行計画の確認
terraform plan -var-file="dev.tfvars"

# デプロイ
terraform apply -var-file="dev.tfvars"

# 破棄
terraform destroy -var-file="dev.tfvars"
```

## ディレクトリ構成

```text
terraform/
├── 01-overview/          # IaC 比較コード
├── 02-first-deploy/      # 初めての S3 デプロイ
├── 03-hcl-basics/        # HCL 文法サンプル集
├── 04-network/           # マルチ AZ ネットワーク
├── 05-web-server/        # EC2 + ALB + Auto Scaling
├── 06-serverless/        # Lambda + API Gateway
│   └── src/              # Lambda ソースコード
├── 07-modules/           # モジュール設計
│   └── modules/vpc/      # VPC カスタムモジュール
├── 08-state/             # State 管理
│   └── bootstrap/        # バックエンド用リソース
├── 09-environments/      # 環境分離パターン
│   ├── envs/             # tfvars / backend 設定
│   ├── environments/     # ディレクトリ分離パターン
│   └── terragrunt/       # Terragrunt 設定例
└── 10-cicd/              # CI/CD パイプライン
    ├── .github/workflows/ # GitHub Actions
    ├── bootstrap/        # OIDC 設定
    └── policy/           # OPA ポリシー
```

## 注意事項

- 各ディレクトリのコードは記事の説明用サンプルです。そのまま `terraform apply` すると AWS リソースが作成され課金が発生します
- `dev.tfvars` 内のリソース ID（`vpc-xxxxxxxxxx` 等）はプレースホルダーです。実際の値に置き換えてください
- #5 は #4 で作成したネットワークの出力値を前提としています
