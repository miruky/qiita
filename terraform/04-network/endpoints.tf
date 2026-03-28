# =============================================================================
# S3 ゲートウェイエンドポイント（無料）
# =============================================================================
resource "aws_vpc_endpoint" "s3" {
  count = var.enable_vpc_endpoints ? 1 : 0

  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.aws_region}.s3"

  vpc_endpoint_type = "Gateway"

  route_table_ids = concat(
    [aws_route_table.public.id],
    aws_route_table.private[*].id,
    [aws_route_table.isolated.id],
  )

  tags = {
    Name = "${local.name_prefix}-s3-endpoint"
  }
}

# =============================================================================
# DynamoDB ゲートウェイエンドポイント（無料）
# =============================================================================
resource "aws_vpc_endpoint" "dynamodb" {
  count = var.enable_vpc_endpoints ? 1 : 0

  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.aws_region}.dynamodb"

  vpc_endpoint_type = "Gateway"

  route_table_ids = concat(
    aws_route_table.private[*].id,
    [aws_route_table.isolated.id],
  )

  tags = {
    Name = "${local.name_prefix}-dynamodb-endpoint"
  }
}
