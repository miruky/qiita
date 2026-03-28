variable "aws_region" {
  description = "AWS リージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "project" {
  description = "プロジェクト名"
  type        = string
  default     = "terraform-network"
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

variable "vpc_cidr" {
  description = "VPC の CIDR ブロック"
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "有効な CIDR ブロックを指定してください。"
  }
}

variable "availability_zones" {
  description = "使用する AZ のリスト"
  type        = list(string)
  default     = ["ap-northeast-1a", "ap-northeast-1c"]
}

variable "single_nat_gateway" {
  description = "NAT ゲートウェイを1つに集約するか（コスト節約）"
  type        = bool
  default     = true
}

variable "enable_vpc_endpoints" {
  description = "VPC エンドポイントを作成するか"
  type        = bool
  default     = true
}
