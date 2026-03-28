# =============================================================================
# ALB の異常ターゲット数アラーム
# =============================================================================
resource "aws_cloudwatch_metric_alarm" "unhealthy_hosts" {
  alarm_name          = "${local.name_prefix}-unhealthy-hosts"
  alarm_description   = "Unhealthy ターゲットが存在するときにアラート"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "UnHealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Average"
  threshold           = 0

  dimensions = {
    LoadBalancer = aws_lb.web.arn_suffix
    TargetGroup  = aws_lb_target_group.web.arn_suffix
  }

  # alarm_actions = [var.sns_topic_arn]  # SNS 通知先
}

# =============================================================================
# ALB の 5xx エラー率アラーム
# =============================================================================
resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name          = "${local.name_prefix}-alb-5xx"
  alarm_description   = "ALB の 5xx エラーが閾値を超えたときにアラート"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_ELB_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = aws_lb.web.arn_suffix
  }

  # alarm_actions = [var.sns_topic_arn]
}

# =============================================================================
# ALB のレスポンスタイムアラーム
# =============================================================================
resource "aws_cloudwatch_metric_alarm" "response_time" {
  alarm_name          = "${local.name_prefix}-response-time"
  alarm_description   = "レスポンスタイムが閾値を超えたときにアラート"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  extended_statistic  = "p99"
  threshold           = 3  # 3秒

  dimensions = {
    LoadBalancer = aws_lb.web.arn_suffix
  }

  # alarm_actions = [var.sns_topic_arn]
}
