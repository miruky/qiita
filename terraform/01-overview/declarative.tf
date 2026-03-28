# 「このリソースが存在するべき」と宣言するだけ
# Terraform が差分を計算して必要な操作のみ実行
resource "aws_instance" "web" {
  ami           = "ami-0abcdef1234567890"
  instance_type = "t3.micro"

  tags = {
    Name = "web-server"
  }
}

# 2回目以降の apply では、変更がなければ何もしない
