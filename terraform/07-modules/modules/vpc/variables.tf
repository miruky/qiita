variable "name_prefix" {
  description = "リソース名のプレフィックス"
  type        = string
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

  validation {
    condition     = length(var.availability_zones) >= 2
    error_message = "AZ は2つ以上指定してください。"
  }
}

variable "public_subnet_cidrs" {
  description = "パブリックサブネットの CIDR リスト"
  type        = list(string)
  default     = []
}

variable "private_subnet_cidrs" {
  description = "プライベートサブネットの CIDR リスト"
  type        = list(string)
  default     = []
}

variable "isolated_subnet_cidrs" {
  description = "Isolated サブネットの CIDR リスト"
  type        = list(string)
  default     = []
}

variable "single_nat_gateway" {
  description = "NAT ゲートウェイを1つに集約するか"
  type        = bool
  default     = false
}

variable "enable_nat_gateway" {
  description = "NAT ゲートウェイを作成するか"
  type        = bool
  default     = true
}

variable "tags" {
  description = "追加タグ"
  type        = map(string)
  default     = {}
}
