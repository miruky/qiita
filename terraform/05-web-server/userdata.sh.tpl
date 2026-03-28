#!/bin/bash
set -euxo pipefail

# ログ出力
exec > >(tee /var/log/userdata.log) 2>&1

echo "=== User Data Start ==="

# システム更新
dnf update -y

# Nginx インストール
dnf install -y nginx

# アプリケーション設定
cat > /usr/share/nginx/html/index.html << 'HTMLEOF'
<!DOCTYPE html>
<html>
<head><title>Terraform Web Server</title></head>
<body>
<h1>Hello from Terraform!</h1>
<p>Environment: ${environment}</p>
<p>Instance ID: <span id="instance-id">Loading...</span></p>
<script>
  fetch('http://169.254.169.254/latest/meta-data/instance-id')
    .then(r => r.text())
    .then(id => document.getElementById('instance-id').textContent = id)
    .catch(() => document.getElementById('instance-id').textContent = 'N/A');
</script>
</body>
</html>
HTMLEOF

# ヘルスチェックエンドポイント
mkdir -p /usr/share/nginx/html/health
cat > /usr/share/nginx/html/health/index.html << 'HTMLEOF'
{"status": "ok"}
HTMLEOF

# Nginx 設定（ポート ${app_port} で待ち受け）
cat > /etc/nginx/conf.d/app.conf << 'NGINXEOF'
server {
    listen ${app_port};
    server_name _;

    location / {
        root /usr/share/nginx/html;
        index index.html;
    }

    location /health {
        root /usr/share/nginx/html;
        index index.html;
        access_log off;
    }
}
NGINXEOF

# デフォルトのポート80設定を無効化
sed -i 's/listen       80;/# listen       80;/' /etc/nginx/nginx.conf
sed -i 's/listen       \[::]:80;/# listen       \[::]:80;/' /etc/nginx/nginx.conf

# Nginx 起動
systemctl enable nginx
systemctl start nginx

echo "=== User Data Complete ==="
