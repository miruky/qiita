#!/bin/bash
echo "=== Start Server ==="

# ファイル権限の設定
chown -R apache:apache /var/www/html
chmod -R 755 /var/www/html

# Apache起動
systemctl start httpd
systemctl enable httpd

echo "Server started."
