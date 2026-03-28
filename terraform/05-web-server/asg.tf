resource "aws_autoscaling_group" "web" {
  name                = "${local.name_prefix}-asg"
  min_size            = var.asg_min_size
  max_size            = var.asg_max_size
  desired_capacity    = var.asg_desired_capacity
  vpc_zone_identifier = var.private_subnet_ids

  # 起動テンプレート
  launch_template {
    id      = aws_launch_template.web.id
    version = "$Latest"
  }

  # ALB ターゲットグループとの紐付け
  target_group_arns = [aws_lb_target_group.web.arn]

  # ヘルスチェックタイプ
  health_check_type         = "ELB"
  health_check_grace_period = 300  # 起動後5分はヘルスチェックを猶予

  # インスタンス更新（ローリングアップデート）
  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 50
      instance_warmup        = 120
    }
  }

  # 終了ポリシー
  termination_policies = ["OldestInstance"]

  # ウォームプール（すぐにスケールアウトできるよう待機インスタンスを確保）
  # warm_pool {
  #   pool_state                  = "Stopped"
  #   min_size                    = 1
  #   max_group_prepared_capacity = 2
  # }

  tag {
    key                 = "Name"
    value               = "${local.name_prefix}-web"
    propagate_at_launch = true
  }

  lifecycle {
    # desired_capacity は手動スケーリング後に Terraform で上書きしない
    ignore_changes = [desired_capacity]
  }
}
