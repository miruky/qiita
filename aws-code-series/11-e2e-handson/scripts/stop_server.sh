#!/bin/bash
echo "=== Stop Server ==="

# Apacheの停止（起動していない場合もエラーにしない）
systemctl stop httpd || true

echo "Server stopped."
