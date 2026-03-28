# main.tf（Root Module）
module "vpc" {
  source = "./modules/vpc"

  name_prefix        = "${var.environment}-${var.project}"
  vpc_cidr           = "10.0.0.0/16"
  availability_zones = ["ap-northeast-1a", "ap-northeast-1c"]

  public_subnet_cidrs  = ["10.0.0.0/24", "10.0.1.0/24"]
  private_subnet_cidrs = ["10.0.10.0/24", "10.0.11.0/24"]
  isolated_subnet_cidrs = ["10.0.20.0/24", "10.0.21.0/24"]

  single_nat_gateway = var.environment != "prod"
  enable_nat_gateway = true

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

# モジュールの出力値を参照
output "vpc_id" {
  value = module.vpc.vpc_id
}

# 別のモジュールにモジュールの出力を渡す
module "web_server" {
  source = "./modules/ec2"

  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnet_ids
  # ...
}
