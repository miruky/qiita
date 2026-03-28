# =============================================================================
# ターゲット追跡スケーリング（CPU 使用率）
# =============================================================================
resource "aws_autoscaling_policy" "cpu_target_tracking" {
  name                   = "${local.name_prefix}-cpu-target"
  autoscaling_group_name = aws_autoscaling_group.web.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value     = 70.0
    disable_scale_in = false
  }
}

# =============================================================================
# ターゲット追跡スケーリング（リクエスト数）
# =============================================================================
resource "aws_autoscaling_policy" "request_count_target" {
  name                   = "${local.name_prefix}-request-target"
  autoscaling_group_name = aws_autoscaling_group.web.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.web.arn_suffix}/${aws_lb_target_group.web.arn_suffix}"
    }
    target_value = 1000  # ターゲットあたり1000リクエスト/分
  }
}

# =============================================================================
# スケジュールスケーリング（営業時間外の縮退）
# =============================================================================
# 平日朝にスケールアウト
resource "aws_autoscaling_schedule" "scale_up" {
  scheduled_action_name  = "${local.name_prefix}-scale-up"
  autoscaling_group_name = aws_autoscaling_group.web.name
  min_size               = var.asg_min_size
  max_size               = var.asg_max_size
  desired_capacity       = var.asg_desired_capacity
  recurrence             = "0 0 * * MON-FRI"  # UTC 月-金 00:00（JST 09:00）
}

# 平日夜にスケールイン
resource "aws_autoscaling_schedule" "scale_down" {
  scheduled_action_name  = "${local.name_prefix}-scale-down"
  autoscaling_group_name = aws_autoscaling_group.web.name
  min_size               = 1
  max_size               = var.asg_max_size
  desired_capacity       = 1
  recurrence             = "0 13 * * MON-FRI" # UTC 月-金 13:00（JST 22:00）
}
