# environments/prod/terraform.tf
terraform {
  required_version = ">= 1.14.0"

  backend "s3" {
    bucket         = "my-terraform-state-123456789012"
    key            = "prod/myapp/terraform.tfstate"  # key が異なる
    region         = "ap-northeast-1"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
