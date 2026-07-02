#!/usr/bin/env bash
set -euo pipefail

repo="${AGENT_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
runtime="${AGENT_RUNTIME:-agent}"
checkpoint_dir="$repo/workspace/tmp/agent-checkpoints/$runtime"
checkpoint_file="$checkpoint_dir/.impl-review-checkpoint"

mkdir -p "$checkpoint_dir"
date +%s > "$checkpoint_file"
echo "✅ independent review 检查点已记录（$(date '+%H:%M:%S')）。30 分钟内有效。"

