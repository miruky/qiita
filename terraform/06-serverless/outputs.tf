output "api_endpoint" {
  description = "API Gateway のエンドポイント URL"
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "api_id" {
  description = "API Gateway ID"
  value       = aws_apigatewayv2_api.main.id
}

output "lambda_function_name" {
  description = "Lambda 関数名"
  value       = aws_lambda_function.api.function_name
}

output "lambda_function_arn" {
  description = "Lambda 関数 ARN"
  value       = aws_lambda_function.api.arn
}

output "s3_bucket_name" {
  description = "データストア S3 バケット名"
  value       = aws_s3_bucket.data.id
}
