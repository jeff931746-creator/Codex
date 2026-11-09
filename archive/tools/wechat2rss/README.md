# 文章列表 API 检查

跨平台入口为 `test_api.py`，仅依赖 Python 标准库。

```powershell
$env:WX_API_KEY = 'YOUR_API_KEY'
python test_api.py
```

脚本验证 API Key 并读取两个公众号的搜索结果；可用 `WX_BASE_URL` 覆盖 API 地址。不会修改 `data/` 中的数据库。原 `test_api.sh` 供已有 Bash 环境使用。本轮只验证代码语法，没有请求外部 API。
