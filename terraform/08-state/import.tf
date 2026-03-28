# import ブロック（v1.5+）
import {
  to = aws_vpc.main
  id = "vpc-0123456789abcdef0"
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "imported-vpc"
  }
}
