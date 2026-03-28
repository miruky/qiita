# envs/stg.tfvars
environment = "stg"
aws_region  = "ap-northeast-1"

vpc_cidr           = "10.1.0.0/16"
availability_zones = ["ap-northeast-1a", "ap-northeast-1c"]

instance_type    = "t3.small"
instance_count   = 2
single_nat_gateway = true

db_instance_class       = "db.t3.small"
db_allocated_storage    = 50
db_multi_az             = false
db_deletion_protection  = false
