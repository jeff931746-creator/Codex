#!/usr/bin/env bash
set -euo pipefail

repo="${AGENT_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
runtime="${AGENT_RUNTIME:-agent}"
checkpoint_dir="$repo/workspace/tmp/agent-checkpoints/$runtime"
checkpoint_file="$checkpoint_dir/.qa-checkpoint"

mkdir -p "$checkpoint_dir"
date +%s > "$checkpoint_file"
echo "✅ QA 检查点已记录（$(date '+%H:%M:%S')）。[注意：请改用 neat-freak checkpoint]"

