#!/bin/bash
echo "=== Validate Service ==="

# ヘルスチェック（最大10回リトライ）
for i in {1..10}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)
    if [ "$HTTP_CODE" = "200" ]; then
        echo "Health check passed! (HTTP $HTTP_CODE)"
        exit 0
    fi
    echo "Waiting for server... ($i/10, HTTP $HTTP_CODE)"
    sleep 3
done

echo "Health check failed!"
exit 1
