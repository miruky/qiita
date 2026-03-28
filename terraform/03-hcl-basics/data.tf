# 最新の Amazon Linux 2023 AMI を取得
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "state"
    values = ["available"]
  }
}

# 現在のリージョンを取得
data "aws_region" "current" {}

# 現在のアカウント ID を取得
data "aws_caller_identity" "current" {}

# 利用可能な AZ を取得
data "aws_availability_zones" "available" {
  state = "available"
}
