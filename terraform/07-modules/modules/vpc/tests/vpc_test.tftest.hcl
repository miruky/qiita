# tests/vpc_test.tftest.hcl

# =============================================================================
# テスト用の変数
# =============================================================================
variables {
  name_prefix        = "test"
  vpc_cidr           = "10.0.0.0/16"
  availability_zones = ["ap-northeast-1a", "ap-northeast-1c"]
  public_subnet_cidrs  = ["10.0.0.0/24", "10.0.1.0/24"]
  private_subnet_cidrs = ["10.0.10.0/24", "10.0.11.0/24"]
  isolated_subnet_cidrs = []
  single_nat_gateway = true
  enable_nat_gateway = true
  tags = {}
}

# =============================================================================
# Plan のみのテスト（リソースを作成しない）
# =============================================================================
run "vpc_plan_test" {
  command = plan

  assert {
    condition     = aws_vpc.this.cidr_block == "10.0.0.0/16"
    error_message = "VPC CIDR が期待値と異なります。"
  }

  assert {
    condition     = aws_vpc.this.enable_dns_support == true
    error_message = "DNS サポートが有効ではありません。"
  }

  assert {
    condition     = aws_vpc.this.enable_dns_hostnames == true
    error_message = "DNS ホスト名が有効ではありません。"
  }

  assert {
    condition     = length(aws_subnet.public) == 2
    error_message = "パブリックサブネットの数が期待値と異なります。"
  }

  assert {
    condition     = length(aws_subnet.private) == 2
    error_message = "プライベートサブネットの数が期待値と異なります。"
  }
}

# =============================================================================
# Apply で実際にリソースを作成するテスト
# =============================================================================
run "vpc_apply_test" {
  command = apply

  assert {
    condition     = output.vpc_id != ""
    error_message = "VPC ID が空です。"
  }

  assert {
    condition     = length(output.public_subnet_ids) == 2
    error_message = "パブリックサブネット ID のリスト長が正しくありません。"
  }

  assert {
    condition     = length(output.private_subnet_ids) == 2
    error_message = "プライベートサブネット ID のリスト長が正しくありません。"
  }
}
