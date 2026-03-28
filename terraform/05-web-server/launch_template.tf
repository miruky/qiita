resource "aws_launch_template" "web" {
  name          = "${local.name_prefix}-lt"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  # IAM インスタンスプロファイル
  iam_instance_profile {
    arn = aws_iam_instance_profile.ec2.arn
  }

  # セキュリティグループ
  vpc_security_group_ids = [var.app_security_group_id]

  # ユーザーデータ
  user_data = base64encode(templatefile("${path.module}/userdata.sh.tpl", {
    environment = var.environment
    app_port    = var.app_port
  }))

  # メタデータオプション（IMDSv2 を強制）
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"  # IMDSv2 必須
    http_put_response_hop_limit = 2
  }

  # モニタリング
  monitoring {
    enabled = true  # 詳細モニタリング（1分間隔）
  }

  # EBS 設定
  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_size           = 20
      volume_type           = "gp3"
      encrypted             = true
      delete_on_termination = true
    }
  }

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${local.name_prefix}-web"
    }
  }

  tag_specifications {
    resource_type = "volume"
    tags = {
      Name = "${local.name_prefix}-web-vol"
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}
