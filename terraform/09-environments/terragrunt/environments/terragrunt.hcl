# environments/terragrunt.hcl（共通設定）
remote_state {
  backend = "s3"
  config = {
    bucket         = "my-terraform-state-${get_aws_account_id()}"
    key            = "${path_relative_to_include()}/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}

terraform {
  source = "../../modules//vpc"
}
