#!/usr/bin/env bash
set -eu
exec node "$(cd "$(dirname "$0")" && pwd)/../services/feishu-codex-bridge/run.mjs" "$@"
