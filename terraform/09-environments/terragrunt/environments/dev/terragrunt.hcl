# environments/dev/terragrunt.hcl
include "root" {
  path = find_in_parent_folders()
}

inputs = {
  environment        = "dev"
  vpc_cidr           = "10.0.0.0/16"
  availability_zones = ["ap-northeast-1a", "ap-northeast-1c"]
  instance_type      = "t3.micro"
  single_nat_gateway = true
}
