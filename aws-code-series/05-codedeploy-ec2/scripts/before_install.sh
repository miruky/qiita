#!/bin/bash
echo "=== BeforeInstall ==="

# Apacheのインストール確認
if ! command -v httpd &> /dev/null; then
    yum install -y httpd
fi

# 旧ファイルの削除
rm -rf /var/www/html/*
