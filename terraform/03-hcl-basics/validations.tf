variable "environment" {
  description = "環境名"
  type        = string

  validation {
    condition     = contains(["dev", "stg", "prod"], var.environment)
    error_message = "environment は dev, stg, prod のいずれかを指定してください。"
  }
}

variable "instance_type" {
  description = "EC2 インスタンスタイプ"
  type        = string

  validation {
    condition     = can(regex("^t3\\.", var.instance_type))
    error_message = "instance_type は t3 ファミリーを指定してください。"
  }
}

variable "cidr_block" {
  description = "VPC CIDR ブロック"
  type        = string

  # 複数のバリデーションルールを定義可能
  validation {
    condition     = can(cidrhost(var.cidr_block, 0))
    error_message = "有効な CIDR ブロックを指定してください。"
  }

  validation {
    condition     = tonumber(split("/", var.cidr_block)[1]) <= 24
    error_message = "CIDR ブロックは /24 以上のネットワークを指定してください。"
  }
}
