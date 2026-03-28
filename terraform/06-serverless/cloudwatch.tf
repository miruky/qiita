# =============================================================================
# Lambda 用ロググループ
# =============================================================================
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.function_name}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${local.name_prefix}-lambda-logs"
  }
}

# =============================================================================
# API Gateway 用ロググループ
# =============================================================================
resource "aws_cloudwatch_log_group" "api_gw" {
  name              = "/aws/apigateway/${local.name_prefix}-api"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${local.name_prefix}-api-gw-logs"
  }
}

# =============================================================================
# Lambda エラーアラーム
# =============================================================================
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${local.name_prefix}-lambda-errors"
  alarm_description   = "Lambda 関数のエラーが発生したときにアラート"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.api.function_name
  }

  # alarm_actions = [var.sns_topic_arn]
}

# =============================================================================
# Lambda 実行時間アラーム
# =============================================================================
resource "aws_cloudwatch_metric_alarm" "lambda_duration" {
  alarm_name          = "${local.name_prefix}-lambda-duration"
  alarm_description   = "Lambda の実行時間がタイムアウトに近いときにアラート"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  extended_statistic  = "p99"
  threshold           = var.lambda_timeout * 1000 * 0.8  # タイムアウトの80%

  dimensions = {
    FunctionName = aws_lambda_function.api.function_name
  }

  # alarm_actions = [var.sns_topic_arn]
}
