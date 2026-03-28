# 開発環境用の変数
aws_region         = "ap-northeast-1"
project            = "terraform-network"
environment        = "dev"
vpc_cidr           = "10.0.0.0/16"
availability_zones = ["ap-northeast-1a", "ap-northeast-1c"]
single_nat_gateway = true   # 開発環境は NAT GW 1つでコスト節約
enable_vpc_endpoints = true
