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

CONFIG_FILE="${CLOUDFLARED_CONFIG_FILE:-$DIR/cloudflared/config.yml}"
if [ ! -f "$CONFIG_FILE" ]; then
  echo "Named tunnel config not found: $CONFIG_FILE" >&2
  echo "Copy $DIR/cloudflared/config.example.yml to config.yml and fill your tunnel values first." >&2
  exit 1
fi

exec "$CLOUDFLARED_BIN" tunnel --config "$CONFIG_FILE" run
