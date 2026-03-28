#!/bin/bash
echo "=== ValidateService ==="

sleep 5

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)
if [ "$HTTP_CODE" = "200" ]; then
    echo "Validation passed! (HTTP $HTTP_CODE)"
    exit 0
else
    echo "Validation failed! (HTTP $HTTP_CODE)"
    exit 1
fi
