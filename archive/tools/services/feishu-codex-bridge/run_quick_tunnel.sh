#!/bin/sh
set -eu

DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

if [ -f "$DIR/.env" ]; then
  set -a
  . "$DIR/.env"
  set +a
fi

CLOUDFLARED_BIN="${CLOUDFLARED_BIN:-}"
if [ -z "$CLOUDFLARED_BIN" ]; then
  for candidate in /opt/homebrew/bin/cloudflared /usr/local/bin/cloudflared "$(command -v cloudflared 2>/dev/null || true)"; do
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then
      CLOUDFLARED_BIN="$candidate"
      break
    fi
  done
fi

if [ -z "${CLOUDFLARED_BIN:-}" ] || [ ! -x "$CLOUDFLARED_BIN" ]; then
  echo "cloudflared not found. Set CLOUDFLARED_BIN or install cloudflared." >&2
  exit 1
fi

TARGET_URL="${QUICK_TUNNEL_TARGET_URL:-}"
if [ -z "$TARGET_URL" ]; then
  PORT_VALUE="${PORT:-3000}"
  HOST_VALUE="${QUICK_TUNNEL_TARGET_HOST:-127.0.0.1}"
  TARGET_URL="http://${HOST_VALUE}:${PORT_VALUE}"
fi

exec "$CLOUDFLARED_BIN" tunnel --url "$TARGET_URL"
