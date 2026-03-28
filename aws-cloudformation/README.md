# AWS CloudFormation シリーズ — コードポートフォリオ

Qiita 連載「AWS CloudFormation」シリーズ（全 7 回）で使用した CloudFormation テンプレート・設定ファイルをまとめたリポジトリです。

## ファイル一覧

| ファイル | 記事 | 内容 |
|:--|:--|:--|
| [first-stack.yml](first-stack.yml) | #1 IaCの基本と入門 | S3 バケット（バージョニング・暗号化・パブリックアクセスブロック） |
| [vpc-network.yml](vpc-network.yml) | #2 テンプレート詳解 | VPC + パブリックサブネット×2 + IGW + ルートテーブル |
| [env-ec2.yml](env-ec2.yml) | #3 組み込み関数・Conditions・Outputs | 環境別 EC2（Mappings / Conditions / UserData） |
| [cross-stack-vpc.yml](cross-stack-vpc.yml) | #4 ネステッドスタック・StackSets | クロススタック参照 — VPC 側（Export） |
| [cross-stack-ec2.yml](cross-stack-ec2.yml) | #4 ネステッドスタック・StackSets | クロススタック参照 — EC2 側（ImportValue） |
| [nested-vpc.yml](nested-vpc.yml) | #4 ネステッドスタック・StackSets | ネステッドスタック — VPC 子テンプレート |
| [nested-ec2.yml](nested-ec2.yml) | #4 ネステッドスタック・StackSets | ネステッドスタック — EC2 子テンプレート |
| [nested-parent.yml](nested-parent.yml) | #4 ネステッドスタック・StackSets | ネステッドスタック — 親テンプレート |
| [drift-handson.yml](drift-handson.yml) | #5 変更セット・ドリフト検出 | ドリフト検出ハンズオン用 S3 バケット |
| [drift-handson-v2.yml](drift-handson-v2.yml) | #5 変更セット・ドリフト検出 | ドリフト修正版（Version タグ追加） |
| [stack-policy.json](stack-policy.json) | #5 変更セット・ドリフト検出 | DB 置換を拒否するスタックポリシー |
| [cfn-deploy-role.yml](cfn-deploy-role.yml) | #6 IaC の CI/CD | CodePipeline 用 CloudFormation デプロイロール |
| [buildspec-validate.yml](buildspec-validate.yml) | #6 IaC の CI/CD | cfn-lint + validate-template の CodeBuild Buildspec |
| [security-rules.guard](security-rules.guard) | #6 IaC の CI/CD | cfn-guard セキュリティルール |
| [best-practices-stack-policy.json](best-practices-stack-policy.json) | #7 ベストプラクティス | RDS・DynamoDB の置換を拒否するスタックポリシー |

## シリーズ構成

| # | タイトル | 主な内容 |
|:--|:--|:--|
| #1 | IaC の基本と CloudFormation 入門 | IaC 概念、テンプレート構造、スタックライフサイクル |
| #2 | テンプレート詳解 | Resources・Parameters・Mappings・DeletionPolicy |
| #3 | 組み込み関数・Conditions・Outputs | Ref / Fn::Sub / Fn::If / Export / ImportValue |
| #4 | ネステッドスタック・StackSets | テンプレート分割・クロススタック参照・マルチアカウント展開 |
| #5 | 変更セット・ドリフト検出 | 変更プレビュー・ドリフト検知・リソースインポート・スタックポリシー |
| #6 | CloudFormation × Code ファミリー | CodePipeline との統合・cfn-lint・cfn-guard |
| #7 | ベストプラクティスと運用 | テンプレート設計・セキュリティ・トラブルシューティング |

## 前提条件

- AWS CLI v2（`aws configure` 済み）
- 適切な IAM 権限（CloudFormation / EC2 / S3 / IAM 等）

## テンプレートの検証

```bash
# 構文チェック
aws cloudformation validate-template --template-body file://first-stack.yml

# cfn-lint による静的解析
pip install cfn-lint
cfn-lint *.yml
```
