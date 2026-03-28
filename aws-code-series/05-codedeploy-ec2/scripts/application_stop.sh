#!/bin/bash
echo "=== ApplicationStop ==="
systemctl stop httpd || true
