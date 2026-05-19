#!/usr/bin/env bash
# QA 收尾检查点
# 由收尾子 agent 在 QA 完成后运行（无论是"有改动已通过 QA"还是"无实质改动跳过 QA"）。
# check-neat-freak.py 会验证此检查点是否存在且未过期。

set -euo pipefail

CHECKPOINT_FILE="/Users/mt/Documents/Codex/.claude/.qa-checkpoint"
date +%s > "$CHECKPOINT_FILE"
echo "✅ QA 检查点已记录（$(date '+%H:%M:%S')）。30 分钟内有效。"
