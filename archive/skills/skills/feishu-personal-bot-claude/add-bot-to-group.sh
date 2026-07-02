#!/usr/bin/env bash
# 把机器人加进一个「已经存在的群」。
# 个人版客户端没有「加机器人」入口，这里用「你的用户身份」通过 API 加
# （接口要求调用者在群内 —— 你在群里，所以可以；机器人不在群无法自助加）。
# 前提：应用已开启「对外共享能力」(外部群才允许应用机器人)。
set -uo pipefail

PROFILE="${PROFILE:-personal}"
BRIDGE="npx -y lark-channel-bridge@latest"
say(){ printf '\n\033[1;36m▶ %s\033[0m\n' "$*"; }

read -rp "机器人 App ID (cli_...): " APP_ID
[ -n "$APP_ID" ] || { echo "App ID 不能为空"; exit 1; }

# ───── 1. 授权用户身份（im:chat 用于加成员，im:chat:read 用于列群）─────
say "授权你的用户身份（一次性，scope 会累积）"
OUT=$(lark-cli auth login --scope "im:chat im:chat:read" --no-wait --json --profile "$PROFILE" 2>/dev/null)
URL=$(printf '%s' "$OUT" | python3 -c "import sys,json;print(json.load(sys.stdin)['verification_url'])" 2>/dev/null)
CODE=$(printf '%s' "$OUT" | python3 -c "import sys,json;print(json.load(sys.stdin)['device_code'])" 2>/dev/null)
if [ -z "${URL:-}" ]; then echo "发起授权失败，输出：$OUT"; exit 1; fi
echo "  打开链接授权（或扫二维码）: $URL"
lark-cli auth qrcode "$URL" --output lark_auth_qr.png >/dev/null 2>&1 && open lark_auth_qr.png 2>/dev/null || true
read -rp "  授权完成后按回车..."
lark-cli auth login --device-code "$CODE" --profile "$PROFILE"
rm -f lark_auth_qr.png

# ───── 2. 列出你所在的群 ─────
say "你所在的群（注意：用第一页，--page-all 在个人版会返回空）"
lark-cli im +chat-list --as user --profile "$PROFILE" --json 2>/dev/null | python3 -c "
import sys, json
d = json.load(sys.stdin)
chats = (d.get('data') or {}).get('chats') or []
if not chats:
    print('  （没列到群）'); sys.exit()
for i, c in enumerate(chats, 1):
    ext = '外部群' if c.get('external') else '内部群'
    print(f\"  {i}. {c.get('name') or '(无名)'}  [{ext}]  {c.get('chat_id')}\")"

# ───── 3. 加机器人进群 ─────
read -rp $'\n目标群 chat_id (oc_...): ' CHAT_ID
[ -n "$CHAT_ID" ] || { echo "chat_id 不能为空"; exit 1; }
say "把机器人加进群（用户身份，member-id-type=app_id）"
lark-cli im chat.members create --as user --profile "$PROFILE" \
  --chat-id "$CHAT_ID" --member-id-type app_id \
  --data "{\"id_list\":[\"$APP_ID\"]}" --succeed-type 1 --json

# ───── 4. 把群加进 bridge 响应白名单 ─────
say "把该群加进 bridge 白名单（否则机器人在群里不响应）"
python3 - "$PROFILE" "$CHAT_ID" <<'PY'
import json, os, sys, shutil
profile, cid = sys.argv[1], sys.argv[2]
p = os.path.expanduser('~/.lark-channel/config.json')
if not os.path.exists(p):
    print('  config.json 不存在，跳过白名单'); sys.exit()
shutil.copy(p, p + '.bak')
d = json.load(open(p))
acc = d.get('profiles', {}).get(profile, {}).get('access')
if acc is None:
    print('  未找到 access 配置，跳过'); sys.exit()
if cid not in acc.setdefault('allowedChats', []):
    acc['allowedChats'].append(cid)
json.dump(d, open(p, 'w'), indent=2, ensure_ascii=False)
print('  allowedChats:', acc.get('allowedChats'))
PY
$BRIDGE restart --profile "$PROFILE" 2>&1 | head -3
say "完成。去群里 @机器人 发消息验证。"
