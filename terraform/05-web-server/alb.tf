# =============================================================================
# Application Load Balancer
# =============================================================================
resource "aws_lb" "web" {
  name               = "${local.name_prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_security_group_id]
  subnets            = var.public_subnet_ids

  enable_deletion_protection = var.environment == "prod" ? true : false

  # アクセスログ（S3 バケットに保存する場合）
  # access_logs {
  #   bucket  = aws_s3_bucket.alb_logs.id
  #   prefix  = "alb"
  #   enabled = true
  # }

  tags = {
    Name = "${local.name_prefix}-alb"
  }
}

# =============================================================================
# ターゲットグループ
# =============================================================================
resource "aws_lb_target_group" "web" {
  name     = "${local.name_prefix}-tg"
  port     = var.app_port
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  # ターゲットタイプ
  target_type = "instance"

  # ヘルスチェック
  health_check {
    enabled             = true
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  # 登録解除の遅延（秒）
  deregistration_delay = 60

  # スティッキーセッション（必要な場合）
  # stickiness {
  #   type            = "lb_cookie"
  #   cookie_duration = 3600
  #   enabled         = true
  # }

  tags = {
    Name = "${local.name_prefix}-tg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# =============================================================================
# リスナー（HTTP → HTTPS リダイレクト）
# =============================================================================
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.web.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# =============================================================================
# リスナー（HTTPS）
# ※ ACM 証明書がない場合は HTTP リスナーで代用
# =============================================================================
# HTTPS リスナー（ACM 証明書がある場合）
# resource "aws_lb_listener" "https" {
#   load_balancer_arn = aws_lb.web.arn
#   port              = 443
#   protocol          = "HTTPS"
#   ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
#   certificate_arn   = var.acm_certificate_arn
#
#   default_action {
#     type             = "forward"
#     target_group_arn = aws_lb_target_group.web.arn
#   }
# }

# HTTP リスナー（開発環境用 - 直接転送）
resource "aws_lb_listener" "http_forward" {
  load_balancer_arn = aws_lb.web.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web.arn
  }

  # HTTPS リスナーを使う場合はこちらをコメントアウト
  # 上の http リダイレクトリスナーと排他
}
