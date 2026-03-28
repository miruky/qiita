variable "aws_region" {
  description = "AWS リージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "project" {
  description = "プロジェクト名"
  type        = string
  default     = "terraform-serverless"
}

variable "environment" {
  description = "環境名"
  type        = string
  default     = "dev"
}

variable "lambda_memory_size" {
  description = "Lambda のメモリサイズ (MB)"
  type        = number
  default     = 256

  validation {
    condition     = var.lambda_memory_size >= 128 && var.lambda_memory_size <= 10240
    error_message = "lambda_memory_size は 128〜10240 の範囲で指定してください。"
  }
}

variable "lambda_timeout" {
  description = "Lambda のタイムアウト (秒)"
  type        = number
  default     = 30
}

variable "log_retention_days" {
  description = "CloudWatch Logs の保持日数"
  type        = number
  default     = 14
}
