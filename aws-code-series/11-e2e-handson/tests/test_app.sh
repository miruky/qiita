#!/bin/bash
echo "=== Running Application Tests ==="

ERRORS=0

# Test 1: index.html が存在するか
if [ -f index.html ]; then
    echo "PASS: index.html exists"
else
    echo "FAIL: index.html not found"
    ERRORS=$((ERRORS + 1))
fi

# Test 2: CSS ファイルが存在するか
if [ -f css/style.css ]; then
    echo "PASS: css/style.css exists"
else
    echo "FAIL: css/style.css not found"
    ERRORS=$((ERRORS + 1))
fi

# Test 3: JS ファイルが存在するか
if [ -f js/app.js ]; then
    echo "PASS: js/app.js exists"
else
    echo "FAIL: js/app.js not found"
    ERRORS=$((ERRORS + 1))
fi

# Test 4: index.html にバージョン情報が含まれるか
if grep -q "version" index.html; then
    echo "PASS: Version info found in index.html"
else
    echo "FAIL: Version info not found"
    ERRORS=$((ERRORS + 1))
fi

# Test 5: HTMLの基本構文チェック
if grep -q "<!DOCTYPE html>" index.html && grep -q "</html>" index.html; then
    echo "PASS: HTML structure is valid"
else
    echo "FAIL: Invalid HTML structure"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "=== Test Results ==="
if [ $ERRORS -eq 0 ]; then
    echo "All tests passed!"
    exit 0
else
    echo "$ERRORS test(s) failed!"
    exit 1
fi
