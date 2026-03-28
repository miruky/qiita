resource "aws_instance" "web" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  lifecycle {
    # 特定の属性変更を無視
    ignore_changes = [
      ami,
      tags["LastUpdated"],
    ]
    
    # 削除を禁止
    prevent_destroy = true
    
    # 新リソースを先に作成してから旧リソースを削除
    create_before_destroy = true
    
    # カスタム条件チェック
    precondition {
      condition     = data.aws_ami.amazon_linux.architecture == "x86_64"
      error_message = "AMI は x86_64 アーキテクチャである必要があります。"
    }
    
    postcondition {
      condition     = self.public_ip != ""
      error_message = "パブリック IP が割り当てられませんでした。"
    }
  }
}
