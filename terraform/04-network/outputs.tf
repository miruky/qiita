output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "VPC CIDR ブロック"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "パブリックサブネット ID のリスト"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "プライベートサブネット ID のリスト"
  value       = aws_subnet.private[*].id
}

output "isolated_subnet_ids" {
  description = "Isolated サブネット ID のリスト"
  value       = aws_subnet.isolated[*].id
}

output "alb_security_group_id" {
  description = "ALB セキュリティグループ ID"
  value       = aws_security_group.alb.id
}

output "app_security_group_id" {
  description = "App セキュリティグループ ID"
  value       = aws_security_group.app.id
}

output "db_security_group_id" {
  description = "DB セキュリティグループ ID"
  value       = aws_security_group.db.id
}

output "nat_gateway_ips" {
  description = "NAT ゲートウェイの Elastic IP"
  value       = aws_eip.nat[*].public_ip
}
