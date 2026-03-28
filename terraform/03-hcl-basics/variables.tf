# 基本的な変数
variable "instance_type" {
  description = "EC2 インスタンスタイプ"
  type        = string
  default     = "t3.micro"
}

# デフォルト値なし（必須入力）
variable "db_password" {
  description = "RDS のマスターパスワード"
  type        = string
  sensitive   = true  # plan/apply の出力でマスクされる
}

# リスト型
variable "availability_zones" {
  description = "使用する AZ のリスト"
  type        = list(string)
  default     = ["ap-northeast-1a", "ap-northeast-1c"]
}

# マップ型
variable "instance_types" {
  description = "環境ごとのインスタンスタイプ"
  type        = map(string)
  default = {
    dev  = "t3.micro"
    stg  = "t3.small"
    prod = "t3.medium"
  }
}

# オブジェクト型
variable "vpc_config" {
  description = "VPC の設定"
  type = object({
    cidr_block           = string
    enable_dns_support   = bool
    enable_dns_hostnames = bool
  })
  default = {
    cidr_block           = "10.0.0.0/16"
    enable_dns_support   = true
    enable_dns_hostnames = true
  }
}
