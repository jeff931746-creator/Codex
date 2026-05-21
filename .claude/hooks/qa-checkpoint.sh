#!/usr/bin/env bash
# QA 收尾检查点（旧轨道兼容保留）
# 推荐使用 neat-freak Skill + neat-freak-checkpoint.sh 替代。
# check-neat-freak.py 现在检查 .neat-freak-checkpoint，不再检查此文件。

REPO="/Users/mt/Documents/Codex"
CHECKPOINT_FILE="$REPO/.claude/.qa-checkpoint"
date +%s > "$CHECKPOINT_FILE"
echo "✅ QA 检查点已记录（$(date '+%H:%M:%S')）。[注意：请改用 neat-freak-checkpoint.sh]"
