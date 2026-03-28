# cidrsubnet の実用例
locals {
  vpc_cidr = "10.0.0.0/16"
  
  # /16 から /24 のサブネットを切り出し
  public_subnets = [
    cidrsubnet(local.vpc_cidr, 8, 0),   # 10.0.0.0/24
    cidrsubnet(local.vpc_cidr, 8, 1),   # 10.0.1.0/24
  ]
  
  private_subnets = [
    cidrsubnet(local.vpc_cidr, 8, 10),  # 10.0.10.0/24
    cidrsubnet(local.vpc_cidr, 8, 11),  # 10.0.11.0/24
  ]
}
