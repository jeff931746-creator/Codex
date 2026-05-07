#!/bin/sh
set -eu

DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

if [ -f "$DIR/.env" ]; then
  set -a
  . "$DIR/.env"
  set +a
fi

NODE_BIN="${NODE_BIN:-/Users/mt/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node}"
if [ ! -x "$NODE_BIN" ]; then
  NODE_BIN="$(command -v node || true)"
fi

if [ -z "${NODE_BIN:-}" ] || [ ! -x "$NODE_BIN" ]; then
  echo "node not found. Set NODE_BIN or install Node.js." >&2
  exit 1
fi

exec "$NODE_BIN" "$DIR/server.mjs"
