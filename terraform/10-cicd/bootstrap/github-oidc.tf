# bootstrap/github-oidc.tf

# GitHub Actions 用の OIDC プロバイダー
# NOTE: thumbprint_list の値はダミーです。
# 実際の運用では GitHub の証明書チェーン情報を確認してください。
resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = ["sts.amazonaws.com"]

  thumbprint_list = [
    "ffffffffffffffffffffffffffffffffffffffff"  # ダミー値（実環境では正しい値を設定）
  ]

  tags = {
    Name = "github-actions-oidc"
  }
}

# GitHub Actions 用の IAM ロール
resource "aws_iam_role" "github_actions" {
  name = "GitHubActionsRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            # 特定のリポジトリ・ブランチに限定
            "token.actions.githubusercontent.com:sub" = "repo:myorg/terraform-infrastructure:*"
          }
        }
      }
    ]
  })

  tags = {
    Name = "github-actions-role"
  }
}

# Terraform 実行に必要な権限
resource "aws_iam_role_policy_attachment" "github_actions" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.terraform_execution.arn
}

resource "aws_iam_policy" "terraform_execution" {
  name = "TerraformExecutionPolicy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "TerraformStateAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
        ]
        Resource = [
          "arn:aws:s3:::my-terraform-state-*",
          "arn:aws:s3:::my-terraform-state-*/*",
        ]
      },
      {
        Sid    = "TerraformStateLock"
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
        ]
        Resource = "arn:aws:dynamodb:*:*:table/terraform-state-lock"
      },
      {
        Sid    = "TerraformResourceManagement"
        Effect = "Allow"
        Action = [
          "ec2:*",
          "iam:*",
          "s3:*",
          "lambda:*",
          "rds:*",
          "elasticloadbalancing:*",
          "autoscaling:*",
          "cloudwatch:*",
          "logs:*",
          "apigateway:*",
          "dynamodb:*",
          "ssm:*",
          "secretsmanager:*",
        ]
        Resource = "*"
      }
    ]
  })
}
