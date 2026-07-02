#!/usr/bin/env bash
# 把 claude setup-token 生成的长期 OAuth token 写进 settings.json，
# 让 lark-channel-bridge 后台 daemon 的 claude 能认证（修 401）。
#
# 背景：订阅登录的登录态绑在宿主应用进程里，后台 daemon 独立启动 claude 读不到，
# 报 "Not logged in" / 401。解法＝用 `claude setup-token` 生成一年期 token
# （走订阅额度），写进 settings.json 的 env.CLAUDE_CODE_OAUTH_TOKEN。
#
# 用法：
#   1. 先在终端跑：claude setup-token   （浏览器授权，复制输出的 token）
#   2. 再跑本脚本，按提示粘贴 token（不回显）
set -euo pipefail

export PATH="/opt/homebrew/bin:/Users/mt/.local/npm/bin:$PATH"
CLAUDE=/Users/mt/.local/npm/bin/claude
SETTINGS=/Users/mt/.claude/settings.json

# 从剪贴板读取 token，并去掉终端折行带进来的换行/空白（read 会被换行截断，故不用 read）
echo "从剪贴板读取 token（请先复制 claude setup-token 输出的那一长串）..."
TOK=$(pbpaste | tr -d '\n\r\t ')
if [[ ${#TOK} -lt 50 ]]; then
  echo "✗ 剪贴板内容只有 ${#TOK} 个字符，不是完整 token。"
  echo "  请回终端把 setup-token 输出的那一长串完整复制（⌘A 选不行就三击选整行），再跑本脚本。"
  exit 1
fi
echo "  剪贴板 token 长度 ${#TOK}，看起来完整。"

# 写进 settings.json env（不经命令行参数，避免进 history/进程列表）
printf '%s' "$TOK" | python3 -c "
import json, os, sys
tok = sys.stdin.read().strip()
p = os.path.expanduser('$SETTINGS')
import shutil
if os.path.exists(p): shutil.copy(p, p + '.bak')
d = json.load(open(p)) if os.path.exists(p) else {}
d.setdefault('env', {})['CLAUDE_CODE_OAUTH_TOKEN'] = tok
json.dump(d, open(p, 'w'), indent=2, ensure_ascii=False)
print('✓ 已写入 settings.json env.CLAUDE_CODE_OAUTH_TOKEN (len=%d)' % len(tok))
"
unset TOK

echo ""
echo "== 自测：用 daemon 同样的隔离环境跑一次 claude =="
if env -i HOME=/Users/mt PATH="$PATH" TERM=xterm "$CLAUDE" -p "回复 OK" 2>&1 | head -5; then
  echo "↑ 若上面是正常回复而非 'Not logged in'/401，说明 token 生效。"
else
  echo "✗ 自测调用失败，检查 token 是否粘贴完整。"
fi

echo ""
echo "== 重启两个 claude bridge（企业 claude + 个人 personal 都读同一份 token） =="
for prof in claude personal; do
  echo "  重启 profile=$prof ..."
  npx lark-channel-bridge@latest restart --profile "$prof" 2>&1 | tail -2 || \
    echo "  （自动重启失败，可手动跑：npx lark-channel-bridge@latest restart --profile $prof）"
done

echo ""
echo "完成。现在去飞书 @机器人发一条消息验证（企业群里那个就是 claude 了）。"
