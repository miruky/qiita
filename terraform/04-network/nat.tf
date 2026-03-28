# =============================================================================
# Elastic IP（NAT ゲートウェイ用）
# =============================================================================
resource "aws_eip" "nat" {
  count  = local.nat_gateway_count
  domain = "vpc"

  tags = {
    Name = "${local.name_prefix}-nat-eip-${count.index}"
  }

  # EIP は IGW に依存する
  depends_on = [aws_internet_gateway.main]
}

# =============================================================================
# NAT ゲートウェイ
# =============================================================================
resource "aws_nat_gateway" "main" {
  count = local.nat_gateway_count

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = {
    Name = "${local.name_prefix}-nat-${count.index}"
  }

  depends_on = [aws_internet_gateway.main]
}
