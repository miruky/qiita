#!/bin/bash
echo "=== Install Dependencies ==="

# Apacheの確認・インストール
if ! command -v httpd &> /dev/null; then
    yum install -y httpd
fi

# 旧ファイルの削除
rm -rf /var/www/html/*

echo "Dependencies installed."
