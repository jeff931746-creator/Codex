#!/bin/bash
# 微信公众号文章列表 API 测试脚本
# 使用 wechat-article-exporter 的 API
#
# 用法：
#   export WX_API_KEY="你的API密钥"
#   bash test_api.sh

BASE_URL="https://down.mptext.top"

if [ -z "$WX_API_KEY" ]; then
  echo "❌ 请先设置 API Key："
  echo "   export WX_API_KEY=\"069940d6cb1d4c478b5200aeb98f55b3\""
  exit 1
fi

echo "=== 1. 验证 API Key ==="
curl -s "$BASE_URL/api/public/v1/authkey" \
  -H "X-Auth-Key: $WX_API_KEY" | python3 -m json.tool

echo ""
echo "=== 2. 搜索公众号：GameLook ==="
curl -s "$BASE_URL/api/public/v1/account?keyword=GameLook" \
  -H "X-Auth-Key: $WX_API_KEY" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(json.dumps(data, ensure_ascii=False, indent=2)[:1000])
"

echo ""
echo "=== 3. 搜索公众号：出海独联体 ==="
curl -s "$BASE_URL/api/public/v1/account?keyword=出海独联体" \
  -H "X-Auth-Key: $WX_API_KEY" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(json.dumps(data, ensure_ascii=False, indent=2)[:1000])
"
