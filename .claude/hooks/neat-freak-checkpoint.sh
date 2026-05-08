#!/usr/bin/env bash
# neat-freak 收尾检查点
# 在 neat-freak 全部步骤完成后运行，写入时间戳。
# pre-commit hook 会验证此检查点是否存在且未过期。

set -euo pipefail

CHECKPOINT_FILE="/Users/mt/Documents/Codex/.claude/.neat-freak-checkpoint"
date +%s > "$CHECKPOINT_FILE"
echo "✅ neat-freak 检查点已记录（$(date '+%H:%M:%S')）。30 分钟内 commit 有效。"
