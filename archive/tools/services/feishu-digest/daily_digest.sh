#!/bin/bash
# daily_digest.sh — 每日飞书全群未读消息汇总
# 拉取所有群自上次运行以来的消息，用 Claude 生成摘要，发到机器人群
set -euo pipefail

LARK="$HOME/.local/npm/bin/lark-cli"
CLAUDE="$HOME/.local/npm/bin/claude"
BOT_CHAT_ID="oc_fce293e816ce35afbb34ce9074ddecc2"   # 摘要发送目标群
STATE_DIR="$HOME/.local/share/feishu-digest"
STATE_FILE="$STATE_DIR/last_read.json"               # 记录每个群的最后读取时间（Unix 秒）
LOG="$STATE_DIR/digest.log"
TMP_DIR="$STATE_DIR/tmp"

mkdir -p "$STATE_DIR" "$TMP_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

log "=== 开始全群未读消息汇总 ==="

# ── 获取所有群（ndjson 每行一个对象）────────────────────────────────────────

log "拉取群列表..."
CHATS_FILE="$TMP_DIR/chats.ndjson"
"$LARK" im chats list --as user --page-all --format ndjson 2>/dev/null > "$CHATS_FILE"
CHAT_COUNT=$(wc -l < "$CHATS_FILE" | tr -d ' ')
log "共 $CHAT_COUNT 个群"

# ── 逐群拉取未读消息（Python 主循环）────────────────────────────────────────

ALL_MESSAGES_FILE="$TMP_DIR/all_messages.txt"
> "$ALL_MESSAGES_FILE"

python3 - <<PYEOF
import json, subprocess, os, sys, datetime

chats_file   = '$CHATS_FILE'
tmp_dir      = '$TMP_DIR'
lark         = '$LARK'
state_file   = '$STATE_FILE'
log_file     = '$LOG'
all_msg_file = '$ALL_MESSAGES_FILE'

def log(msg):
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line)
    with open(log_file, 'a') as f:
        f.write(line + '\n')

# 加载群列表
chats = []
with open(chats_file) as f:
    for line in f:
        line = line.strip()
        if line:
            chats.append(json.loads(line))

# 加载已有状态（上次读取的 Unix 秒时间戳）
state = {}
if os.path.exists(state_file):
    with open(state_file) as f:
        state = json.load(f)

# 默认起始时间：昨天 00:00 本地时间
tz_cn = datetime.timezone(datetime.timedelta(hours=8))
yesterday_start = datetime.datetime.now(tz_cn).replace(
    hour=0, minute=0, second=0, microsecond=0
) - datetime.timedelta(days=1)
default_start_ts = str(int(yesterday_start.timestamp()))

all_sections = []
new_state = dict(state)

for chat in chats:
    chat_id   = chat['chat_id']
    chat_name = chat.get('name', chat_id)
    start_ts  = state.get(chat_id, default_start_ts)

    # 拉取消息（直接调飞书 API，绕过 scope 预检查）
    params = json.dumps({
        "container_id_type": "chat",
        "container_id": chat_id,
        "sort_type": "ByCreateTimeAsc",
        "start_time": start_ts,
        "page_size": 50
    })
    msg_file = os.path.join(tmp_dir, f'{chat_id}.json')
    try:
        result = subprocess.run(
            [lark, 'api', 'GET', '/open-apis/im/v1/messages',
             '--as', 'user', '--params', params],
            capture_output=True, text=True, timeout=30
        )
        with open(msg_file, 'w') as f:
            f.write(result.stdout)
    except Exception as e:
        log(f'[WARN] 拉取群 {chat_name} 失败: {e}')
        continue

    # 解析消息
    try:
        with open(msg_file) as f:
            raw = json.load(f)
    except Exception:
        continue

    if raw.get('code', 0) != 0:
        # API 错误（权限不足等），静默跳过
        continue

    messages = raw.get('data', {}).get('items', [])
    lines    = []
    latest_ts = start_ts

    for m in messages:
        if m.get('deleted'):
            continue
        sender      = m.get('sender', {})
        sender_type = sender.get('sender_type', '')
        # 跳过系统消息和 bot 消息
        if sender_type in ('', 'app'):
            continue
        msg_type = m.get('msg_type', '')
        create_ts = m.get('create_time', '0')  # 毫秒
        create_s  = str(int(create_ts) // 1000)

        # 格式化时间
        try:
            t = datetime.datetime.fromtimestamp(
                int(create_ts) / 1000,
                tz=tz_cn
            ).strftime('%m-%d %H:%M')
        except Exception:
            t = create_ts

        # 解析消息内容
        body = m.get('body', {}).get('content', '')
        try:
            c = json.loads(body)
            if isinstance(c, dict) and 'zh_cn' in c:
                # post 富文本
                paragraphs = c['zh_cn'].get('content', [])
                parts = [e.get('text', '') for p in paragraphs for e in p if e.get('tag') == 'text']
                text = ' '.join(parts).strip()
            elif isinstance(c, dict):
                text = c.get('text', '').strip()
            else:
                text = str(c).strip()
        except Exception:
            text = body.strip()

        if text:
            lines.append(f'[{t}] {text}')
            if create_s > latest_ts:
                latest_ts = create_s

    if lines:
        all_sections.append(f'【{chat_name}】\n' + '\n'.join(lines))

    # 更新该群读取进度（记录最新消息时间，下次从这里开始）
    if latest_ts > start_ts:
        new_state[chat_id] = latest_ts

log(f'有新消息的群：{len(all_sections)} 个')

# 写入汇总
with open(all_msg_file, 'w') as f:
    f.write('\n\n'.join(all_sections))

# 保存状态
with open(state_file, 'w') as f:
    json.dump(new_state, f, ensure_ascii=False, indent=2)
PYEOF

if [ ! -s "$ALL_MESSAGES_FILE" ]; then
    log "所有群均无新消息，跳过摘要"
    exit 0
fi

# ── 生成摘要 ──────────────────────────────────────────────────────────────────

TODAY=$(date +%Y-%m-%d)
log "调用 Claude 生成摘要..."

FORMATTED=$(cat "$ALL_MESSAGES_FILE")
PROMPT="以下是飞书工作群今日的未读消息（按群分组，格式：【群名】\n[时间] 消息内容）。

请用中文生成一份简洁的每日汇总，格式：

**${TODAY} 飞书群消息日报**

按群列出，每个群只提炼关键信息：
- 重要决策/事项
- 进展或讨论结论
- 需要跟进的待办（如有）

无实质内容的群（纯打招呼、随机闲聊）跳过不列。总字数控制在 800 字以内。

消息记录：
${FORMATTED}"

SUMMARY=$("$CLAUDE" -p "$PROMPT" 2>&1)

if [ -z "$SUMMARY" ]; then
    log "摘要生成失败"
    exit 1
fi

log "摘要生成完成（${#SUMMARY} 字符），发送中..."

# ── 发送摘要 ──────────────────────────────────────────────────────────────────

"$LARK" im +messages-send \
    --chat-id "$BOT_CHAT_ID" \
    --as bot \
    --markdown "$SUMMARY" 2>&1 | tee -a "$LOG"

log "=== 汇总完成 ==="

# 清理临时文件
rm -f "$TMP_DIR"/*.json "$TMP_DIR"/*.ndjson
