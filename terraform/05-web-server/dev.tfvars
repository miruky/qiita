# 開発環境用の変数
aws_region  = "ap-northeast-1"
project     = "terraform-web"
environment = "dev"

# ネットワーク（#4 の出力値を入力）
vpc_id                = "vpc-xxxxxxxxxx"
public_subnet_ids     = ["subnet-aaaaa", "subnet-bbbbb"]
private_subnet_ids    = ["subnet-ccccc", "subnet-ddddd"]
alb_security_group_id = "sg-xxxxxxxxxx"
app_security_group_id = "sg-yyyyyyyyyy"

# EC2
instance_type = "t3.micro"
app_port      = 8080

# Auto Scaling
asg_min_size         = 2
asg_max_size         = 4
asg_desired_capacity = 2
