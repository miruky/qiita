# プロジェクト B から プロジェクト A（ネットワーク）の State を参照
data "terraform_remote_state" "network" {
  backend = "s3"

  config = {
    bucket = "my-terraform-state-123456789012"
    key    = "network/terraform.tfstate"
    region = "ap-northeast-1"
  }
}

# ネットワークプロジェクトの出力値を参照
resource "aws_instance" "web" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  subnet_id     = data.terraform_remote_state.network.outputs.private_subnet_ids[0]

  vpc_security_group_ids = [
    data.terraform_remote_state.network.outputs.app_security_group_id
  ]
}
