# マップで複数リソースを作成
variable "s3_buckets" {
  type = map(object({
    versioning = bool
    lifecycle_days = number
  }))
  default = {
    "logs" = {
      versioning     = true
      lifecycle_days = 90
    }
    "artifacts" = {
      versioning     = false
      lifecycle_days = 30
    }
  }
}

resource "aws_s3_bucket" "buckets" {
  for_each = var.s3_buckets

  bucket = "${var.project}-${each.key}"
  
  tags = {
    Name = each.key
  }
}

resource "aws_s3_bucket_versioning" "buckets" {
  for_each = {
    for k, v in var.s3_buckets : k => v
    if v.versioning
  }

  bucket = aws_s3_bucket.buckets[each.key].id
  versioning_configuration {
    status = "Enabled"
  }
}
