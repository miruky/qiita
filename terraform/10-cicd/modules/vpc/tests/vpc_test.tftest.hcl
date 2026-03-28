# modules/vpc/tests/vpc_test.tftest.hcl
# CI 環境でのモジュールテスト

variables {
  vpc_cidr         = "10.0.0.0/16"
  project          = "ci-test"
  environment      = "test"
  public_subnets   = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets  = ["10.0.11.0/24", "10.0.12.0/24"]
  azs              = ["ap-northeast-1a", "ap-northeast-1c"]
}

# plan のみのテスト
run "vpc_plan" {
  command = plan

  assert {
    condition     = aws_vpc.main.cidr_block == "10.0.0.0/16"
    error_message = "VPC CIDR が想定と異なります"
  }
}

# 実リソースを作成するテスト
run "vpc_apply" {
  command = apply

  assert {
    condition     = aws_vpc.main.cidr_block == "10.0.0.0/16"
    error_message = "VPC CIDR が想定と異なります"
  }

  assert {
    condition     = length(aws_subnet.public) == 2
    error_message = "パブリックサブネットの数が想定と異なります"
  }

  assert {
    condition     = length(aws_subnet.private) == 2
    error_message = "プライベートサブネットの数が想定と異なります"
  }
}
