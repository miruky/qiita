# prod.tfvars
environment    = "prod"
instance_type  = "t3.medium"
db_password    = "SuperSecretPassword123!"

availability_zones = [
  "ap-northeast-1a",
  "ap-northeast-1c",
  "ap-northeast-1d",
]

vpc_config = {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
}
