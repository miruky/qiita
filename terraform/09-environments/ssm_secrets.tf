# SSM Parameter Store から機密情報を参照する例

# NG: tfvars にパスワードを書いてしまうパターン
# prod.tfvars
# db_password = "SuperSecretPassword123!"

# OK: SSM Parameter Store から参照
data "aws_ssm_parameter" "db_password" {
  name            = "/${var.environment}/database/master-password"
  with_decryption = true
}

resource "aws_db_instance" "main" {
  # ...
  password = data.aws_ssm_parameter.db_password.value
}
