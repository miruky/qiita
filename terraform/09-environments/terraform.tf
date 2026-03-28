# terraform.tf
terraform {
  backend "s3" {
    # bucket, key, region は -backend-config で指定
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}
