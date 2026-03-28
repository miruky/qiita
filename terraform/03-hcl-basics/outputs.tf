# 基本的な出力
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

# 機密情報の出力
output "db_endpoint" {
  description = "RDS エンドポイント"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

# 条件付き出力
output "alb_dns_name" {
  description = "ALB の DNS 名"
  value       = var.create_alb ? aws_lb.main[0].dns_name : null
}

# 複雑な構造の出力
output "subnet_ids" {
  description = "サブネット ID のリスト"
  value       = aws_subnet.private[*].id
}
