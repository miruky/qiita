locals {
  name_prefix = "${var.environment}-${var.project}"

  # サブネット CIDR の計算
  public_subnet_cidrs = [
    for i in range(length(var.availability_zones)) :
    cidrsubnet(var.vpc_cidr, 8, i)
  ]

  private_subnet_cidrs = [
    for i in range(length(var.availability_zones)) :
    cidrsubnet(var.vpc_cidr, 8, i + 10)
  ]

  isolated_subnet_cidrs = [
    for i in range(length(var.availability_zones)) :
    cidrsubnet(var.vpc_cidr, 8, i + 20)
  ]

  # NAT ゲートウェイの数
  nat_gateway_count = var.single_nat_gateway ? 1 : length(var.availability_zones)
}
