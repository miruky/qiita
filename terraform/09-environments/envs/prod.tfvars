# envs/prod.tfvars
environment = "prod"
aws_region  = "ap-northeast-1"

vpc_cidr           = "10.2.0.0/16"
availability_zones = ["ap-northeast-1a", "ap-northeast-1c", "ap-northeast-1d"]

instance_type    = "t3.medium"
instance_count   = 3
single_nat_gateway = false

db_instance_class       = "db.r6g.large"
db_allocated_storage    = 100
db_multi_az             = true
db_deletion_protection  = true
