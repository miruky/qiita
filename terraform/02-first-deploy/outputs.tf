output "bucket_id" {
  description = "S3 バケット名"
  value       = aws_s3_bucket.main.id
}

output "bucket_arn" {
  description = "S3 バケット ARN"
  value       = aws_s3_bucket.main.arn
}

output "bucket_region" {
  description = "S3 バケットのリージョン"
  value       = aws_s3_bucket.main.region
}
