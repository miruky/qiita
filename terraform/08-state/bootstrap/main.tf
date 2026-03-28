# bootstrap/main.tf
# このファイルだけは「ローカル State」で管理する（鶏と卵問題）

terraform {
  required_version = ">= 1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-1"

  default_tags {
    tags = {
      Project   = "terraform-backend"
      ManagedBy = "Terraform"
    }
  }
}

# =============================================================================
# S3 バケット（State 保存用）
# =============================================================================
resource "aws_s3_bucket" "terraform_state" {
  bucket = "my-terraform-state-${data.aws_caller_identity.current.account_id}"

  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name = "Terraform State"
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# バケットポリシー（HTTPS のみ許可）
resource "aws_s3_bucket_policy" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "EnforceTLS"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.terraform_state.arn,
          "${aws_s3_bucket.terraform_state.arn}/*",
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      }
    ]
  })
}

# =============================================================================
# DynamoDB テーブル（State ロック用）
# =============================================================================
resource "aws_dynamodb_table" "terraform_lock" {
  name         = "terraform-state-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name = "Terraform State Lock"
  }
}

# =============================================================================
# データソース
# =============================================================================
data "aws_caller_identity" "current" {}

# =============================================================================
# 出力値
# =============================================================================
output "state_bucket_name" {
  description = "State 用 S3 バケット名"
  value       = aws_s3_bucket.terraform_state.id
}

output "lock_table_name" {
  description = "ロック用 DynamoDB テーブル名"
  value       = aws_dynamodb_table.terraform_lock.name
}
