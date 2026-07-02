#!/usr/bin/env bash
set -euo pipefail

repo="${AGENT_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
runtime="${AGENT_RUNTIME:-agent}"

cd "$repo"
AGENT_WORKSPACE="$repo" AGENT_RUNTIME="$runtime" python3 - "$@" <<'INNER'
import argparse
import sys
sys.path.insert(0, '.agents/hooks')
from hook_utils import active_task_scope, checkpoint_path, git_diff_hash, now, write_json

parser = argparse.ArgumentParser()
parser.add_argument('--scope', action='append', default=[])
args = parser.parse_args()
scope = args.scope or active_task_scope() or ['.']
write_json(checkpoint_path('neat-freak.json'), {
    'result': 'pass',
    'scope_paths': scope,
    'diff_hash': git_diff_hash(scope),
    'created_at': now(),
})
print('✅ neat-freak 检查点已记录。工作树 scoped diff 改变则失效。')
INNER
