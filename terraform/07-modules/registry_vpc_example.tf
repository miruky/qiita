# terraform-aws-modules/vpc/aws レジストリモジュールの使用例
#
# NOTE: enable_s3_endpoint / enable_dynamodb_endpoint は
# terraform-aws-modules/vpc/aws v5.x で非推奨となっています。
# v5.x 以降では別途 aws_vpc_endpoint リソースで定義してください。
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.environment}-${var.project}"
  cidr = "10.0.0.0/16"

  azs             = ["ap-northeast-1a", "ap-northeast-1c"]
  public_subnets  = ["10.0.0.0/24", "10.0.1.0/24"]
  private_subnets = ["10.0.10.0/24", "10.0.11.0/24"]

  enable_nat_gateway     = true
  single_nat_gateway     = true
  one_nat_gateway_per_az = false

  enable_dns_hostnames = true
  enable_dns_support   = true

  # VPC エンドポイント
  enable_s3_endpoint       = true
  enable_dynamodb_endpoint = true

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  public_subnet_tags = {
    Tier = "Public"
  }

  private_subnet_tags = {
    Tier = "Private"
  }
}
