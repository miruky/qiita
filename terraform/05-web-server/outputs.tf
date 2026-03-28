output "alb_dns_name" {
  description = "ALB の DNS 名"
  value       = aws_lb.web.dns_name
}

output "alb_arn" {
  description = "ALB の ARN"
  value       = aws_lb.web.arn
}

output "target_group_arn" {
  description = "ターゲットグループの ARN"
  value       = aws_lb_target_group.web.arn
}

output "asg_name" {
  description = "Auto Scaling グループ名"
  value       = aws_autoscaling_group.web.name
}

output "launch_template_id" {
  description = "起動テンプレート ID"
  value       = aws_launch_template.web.id
}

output "launch_template_latest_version" {
  description = "起動テンプレートの最新バージョン"
  value       = aws_launch_template.web.latest_version
}
