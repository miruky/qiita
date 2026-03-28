# terraform.workspace で現在の Workspace 名を取得
locals {
  environment = terraform.workspace

  # 環境ごとの設定
  instance_types = {
    dev  = "t3.micro"
    stg  = "t3.small"
    prod = "t3.medium"
  }

  instance_counts = {
    dev  = 1
    stg  = 2
    prod = 3
  }

  instance_type  = local.instance_types[local.environment]
  instance_count = local.instance_counts[local.environment]
}

resource "aws_instance" "web" {
  count         = local.instance_count
  ami           = data.aws_ami.amazon_linux.id
  instance_type = local.instance_type

  tags = {
    Name        = "${local.environment}-web-${count.index}"
    Environment = local.environment
  }
}
