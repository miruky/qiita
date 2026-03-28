output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.this.id
}

output "vpc_cidr" {
  description = "VPC CIDR ブロック"
  value       = aws_vpc.this.cidr_block
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

output "nat_gateway_ips" {
  description = "NAT ゲートウェイの Elastic IP リスト"
  value       = aws_eip.nat[*].public_ip
}

output "internet_gateway_id" {
  description = "インターネットゲートウェイ ID"
  value       = length(aws_internet_gateway.this) > 0 ? aws_internet_gateway.this[0].id : null
}
