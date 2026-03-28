# moved ブロックの例
moved {
  from = aws_s3_bucket.old_name
  to   = aws_s3_bucket.new_name
}

moved {
  from = aws_vpc.main
  to   = module.vpc.aws_vpc.this
}
