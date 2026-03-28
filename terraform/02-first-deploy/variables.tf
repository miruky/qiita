variable "aws_region" {
  description = "AWS リージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "bucket_name" {
  description = "S3 バケット名"
  type        = string
  default     = "my-first-terraform-bucket-12345"
}

variable "environment" {
  description = "環境名"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "stg", "prod"], var.environment)
    error_message = "environment は dev, stg, prod のいずれかを指定してください。"
  }
}
