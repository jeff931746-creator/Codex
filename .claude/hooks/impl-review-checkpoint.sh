#!/usr/bin/env bash
# implementation independent review 检查点
# 在 independent review subagent 完成后运行，写入时间戳。
# Stop hook (check-impl-checklist.py) 会验证此检查点是否存在且未过期。

set -euo pipefail

CHECKPOINT_FILE="/Users/mt/Documents/Codex/.claude/.impl-review-checkpoint"
date +%s > "$CHECKPOINT_FILE"
echo "✅ independent review 检查点已记录（$(date '+%H:%M:%S')）。30 分钟内有效。"
