variable "aws_region" {
  description = "AWS リージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "project" {
  description = "プロジェクト名"
  type        = string
  default     = "terraform-web"
}

variable "environment" {
  description = "環境名"
  type        = string
  default     = "dev"
}

# ネットワーク（#4 で作成した VPC の情報）
variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "public_subnet_ids" {
  description = "パブリックサブネット ID のリスト"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "プライベートサブネット ID のリスト"
  type        = list(string)
}

variable "alb_security_group_id" {
  description = "ALB セキュリティグループ ID"
  type        = string
}

variable "app_security_group_id" {
  description = "App セキュリティグループ ID"
  type        = string
}

# EC2 設定
variable "instance_type" {
  description = "EC2 インスタンスタイプ"
  type        = string
  default     = "t3.micro"
}

variable "app_port" {
  description = "アプリケーションのポート番号"
  type        = number
  default     = 8080
}

# Auto Scaling 設定
variable "asg_min_size" {
  description = "Auto Scaling の最小台数"
  type        = number
  default     = 2
}

variable "asg_max_size" {
  description = "Auto Scaling の最大台数"
  type        = number
  default     = 6
}

variable "asg_desired_capacity" {
  description = "Auto Scaling の希望台数"
  type        = number
  default     = 2
}
