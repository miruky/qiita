# environments/dev/main.tf
module "vpc" {
  source = "../../modules/vpc"

  name_prefix        = "dev-myapp"
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  # ...
}

module "web" {
  source = "../../modules/ec2"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
  # ...
}
