# 同じプロジェクトで AWS と GitHub を管理
provider "aws" {
  region = "ap-northeast-1"
}

provider "github" {
  token = var.github_token
}

resource "aws_s3_bucket" "artifacts" {
  bucket = "my-artifacts"
}

resource "github_repository" "app" {
  name        = "my-app"
  description = "Application repository"
  visibility  = "private"
}
