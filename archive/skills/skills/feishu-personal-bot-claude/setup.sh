#!/usr/bin/env bash
# 飞书个人版自建应用机器人 → Claude Code 自动回复：一键接入向导
# 自动化所有命令行步骤；人工步骤（后台配置）会暂停等待你确认。
# 用法： bash setup.sh        可选环境变量： PROFILE / WORKSPACE
set -uo pipefail

BRIDGE="npx -y lark-channel-bridge@latest"
PROFILE="${PROFILE:-personal}"
WORKSPACE="${WORKSPACE:-$HOME/feishu-bot-workspace}"
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"

say(){ printf '\n\033[1;36m▶ %s\033[0m\n' "$*"; }
warn(){ printf '\033[1;33m  ! %s\033[0m\n' "$*"; }
pause(){ read -rp $'\n  完成后按回车继续...'; }

# ───── 阶段 0：前置检查 ─────
say "阶段 0：前置检查"
for c in node npx python3 lark-cli; do
  command -v "$c" >/dev/null || { echo "缺少 $c，请先安装后再运行"; exit 1; }
done
command -v claude >/dev/null || warn "未找到 claude CLI —— bot 的回复引擎不可用，请先安装并登录 claude"
command -v expect >/dev/null || warn "未装 expect —— secret 存 keystore 那步会跳过（不影响启动，启动用 --app-secret）；建议 brew install expect"

# ───── 阶段 1：开发者后台（人工）─────
say "阶段 1【人工】开发者后台 https://open.feishu.cn/app"
cat <<EOF
  1) 创建企业自建应用 → 添加「机器人」能力
  2) 权限管理 → 导入 → 上传   $SKILL_DIR/permissions.json
     （一次性批量开通，免逐个勾选；这是同事常踩的坑）
  3) 事件与回调 → 订阅方式 = 「使用长连接接收事件」
  4) 事件订阅 → 添加  im.message.receive_v1
  5) 要进外部群/和朋友的群：开启「对外共享能力」(需个人实名认证)
  6) 版本管理 → 创建版本并发布（个人版免审核自动通过）
  7) 凭证与基础信息 → 复制 App ID
EOF
pause

# ───── 阶段 2：输入凭证 ─────
say "阶段 2：输入应用凭证"
read -rp "  App ID (cli_...): " APP_ID
read -rsp "  App Secret (不回显): " APP_SECRET; echo
[ -n "$APP_ID" ] && [ -n "$APP_SECRET" ] || { echo "App ID / Secret 不能为空"; exit 1; }

# ───── 阶段 3：配 lark-cli profile ─────
say "阶段 3：配置 lark-cli profile = $PROFILE（secret 走 stdin，不进进程列表）"
printf '%s' "$APP_SECRET" | lark-cli config init --app-id "$APP_ID" --app-secret-stdin --name "$PROFILE" --brand feishu
if lark-cli im chats get --chat-id oc_probe --as bot --profile "$PROFILE" --json 2>&1 | grep -q '"identity": *"bot"'; then
  echo "  ✓ 凭证有效（已到达飞书 API 层）"
else
  warn "凭证校验未通过，请核对 App ID / Secret 是否正确、版本是否已发布"
fi

# ───── 阶段 4：修 401（认证写进 settings.json）─────
say "阶段 4：把 Claude 认证写进 ~/.claude/settings.json（否则 daemon 里 claude 会 401）"
if command -v zsh >/dev/null; then
  zsh -ic "python3 '$SKILL_DIR/inject_env.py'" || python3 "$SKILL_DIR/inject_env.py"
else
  python3 "$SKILL_DIR/inject_env.py"
fi

# ───── 阶段 5：起 bridge daemon ─────
say "阶段 5：启动 lark-channel-bridge daemon（workspace=$WORKSPACE）"
mkdir -p "$WORKSPACE"
if command -v expect >/dev/null; then
  expect <<EXP >/dev/null 2>&1 || true
log_user 0
set timeout 90
spawn $BRIDGE secrets set --app-id $APP_ID
expect { -re "Secret.*:" { send "$APP_SECRET\r"; exp_continue } eof }
EXP
fi
$BRIDGE start --profile "$PROFILE" --agent claude --app-id "$APP_ID" \
  --app-secret "$APP_SECRET" --workspace "$WORKSPACE" --skip-check-lark-cli
$BRIDGE ps || true

# ───── 阶段 6：设管理员 + 白名单 ─────
say "阶段 6：把你设为 bridge 管理员（之后可在群里发 /invite group）"
read -rp "  你的 open_id (ou_...，留空跳过): " MY_OPENID
python3 - "$PROFILE" "$MY_OPENID" <<'PY'
import json, os, sys, shutil
profile, oid = sys.argv[1], sys.argv[2]
p = os.path.expanduser('~/.lark-channel/config.json')
if not os.path.exists(p):
    print('  config.json 不存在，跳过'); sys.exit()
shutil.copy(p, p + '.bak')
d = json.load(open(p))
acc = d.get('profiles', {}).get(profile, {}).get('access')
if acc is None:
    print('  未找到 profile access 配置，跳过'); sys.exit()
if oid and oid not in acc.setdefault('admins', []):
    acc['admins'].append(oid)
json.dump(d, open(p, 'w'), indent=2, ensure_ascii=False)
print('  admins:', acc.get('admins'))
PY
$BRIDGE restart --profile "$PROFILE" 2>&1 | head -3

cat <<EOF

\033[1;32m✓ 接入完成。\033[0m
  - 把机器人加进群后，在群里 @机器人 发消息即可走 Claude 回复
  - 加机器人进「已有群」： bash "$SKILL_DIR/add-bot-to-group.sh"
  - 管理： $BRIDGE status | restart --profile $PROFILE | stop --profile $PROFILE | ps
EOF
