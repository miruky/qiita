# envs/dev.tfvars
environment = "dev"
aws_region  = "ap-northeast-1"

vpc_cidr           = "10.0.0.0/16"
availability_zones = ["ap-northeast-1a", "ap-northeast-1c"]

instance_type    = "t3.micro"
instance_count   = 1
single_nat_gateway = true

db_instance_class       = "db.t3.micro"
db_allocated_storage    = 20
db_multi_az             = false
db_deletion_protection  = false
