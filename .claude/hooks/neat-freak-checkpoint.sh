#!/usr/bin/env bash
# neat-freak 收尾检查点
# 在 neat-freak 全部步骤完成后运行，写入时间戳和当前工作树 diff hash。
# check-neat-freak.py 验证：同一工作树状态下检查点永久有效（状态改变后失效）。

REPO="/Users/mt/Documents/Codex"
CHECKPOINT_FILE="$REPO/.claude/.neat-freak-checkpoint"

ts=$(date +%s)
# 记录当前工作树与 HEAD 的 diff hash（空 diff 时为固定哈希）
diff_hash=$(git -C "$REPO" diff HEAD 2>/dev/null | md5 -q 2>/dev/null || echo "nodiff")

printf '%s:%s\n' "$ts" "$diff_hash" > "$CHECKPOINT_FILE"
echo "✅ neat-freak 检查点已记录（$(date '+%H:%M:%S')）。工作树状态不变则永久有效。"
