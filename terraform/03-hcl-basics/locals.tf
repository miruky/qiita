locals {
  # 定数の定義
  project = "my-web-app"
  
  # 変数を組み合わせた値
  name_prefix = "${var.environment}-${local.project}"
  
  # 共通タグ
  common_tags = {
    Project     = local.project
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
  
  # 条件分岐
  is_production = var.environment == "prod"
  
  # リスト内包表記的な使い方
  subnet_cidrs = [
    for i in range(length(var.availability_zones)) :
    cidrsubnet(var.vpc_cidr, 8, i)
  ]
}
