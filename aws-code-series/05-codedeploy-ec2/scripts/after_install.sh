#!/bin/bash
echo "=== AfterInstall ==="

# ファイル権限の設定
chown -R apache:apache /var/www/html
chmod -R 755 /var/www/html
