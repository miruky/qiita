#!/bin/bash
echo "=== ApplicationStart ==="

systemctl start httpd
systemctl enable httpd
