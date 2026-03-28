locals {
  name_prefix   = "${var.environment}-${var.project}"
  function_name = "${local.name_prefix}-api"
}
