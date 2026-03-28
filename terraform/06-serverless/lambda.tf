# =============================================================================
# Lambda ソースコードの zip 化
# =============================================================================
data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = "${path.module}/src"
  output_path = "${path.module}/dist/lambda.zip"
}

# =============================================================================
# Lambda 関数
# =============================================================================
resource "aws_lambda_function" "api" {
  function_name = local.function_name
  role          = aws_iam_role.lambda.arn
  handler       = "app.handler"
  runtime       = "python3.13"

  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256

  memory_size = var.lambda_memory_size
  timeout     = var.lambda_timeout

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.data.id
      ENVIRONMENT = var.environment
    }
  }

  # ログ設定
  logging_config {
    log_format = "JSON"
    log_group  = aws_cloudwatch_log_group.lambda.name
  }

  # デッドレターキュー（必要に応じて）
  # dead_letter_config {
  #   target_arn = aws_sqs_queue.dlq.arn
  # }

  # 予約済み同時実行数（必要に応じて）
  # reserved_concurrent_executions = 100

  tags = {
    Name = local.function_name
  }

  depends_on = [aws_cloudwatch_log_group.lambda]
}
