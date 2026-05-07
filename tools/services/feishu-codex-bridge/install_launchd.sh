#!/bin/sh
set -eu

DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
LOG_DIR="$HOME/Library/Logs/FeishuCodexBridge"
APP_SUPPORT_DIR="$HOME/Library/Application Support/FeishuCodexBridge"
RUNTIME_DIR="$APP_SUPPORT_DIR/bridge"
USER_DOMAIN="gui/$(id -u)"

usage() {
  cat <<'EOF'
Usage:
  sh ./install_launchd.sh bridge
  sh ./install_launchd.sh named-tunnel
  sh ./install_launchd.sh quick-tunnel
EOF
}

if [ "${1:-}" = "" ]; then
  usage
  exit 1
fi

sync_runtime() {
  mkdir -p "$RUNTIME_DIR" "$RUNTIME_DIR/cloudflared" "$RUNTIME_DIR/launchd"

  cp "$DIR/server.mjs" "$RUNTIME_DIR/server.mjs"
  cp "$DIR/package.json" "$RUNTIME_DIR/package.json"
  if [ -f "$DIR/package-lock.json" ]; then
    cp "$DIR/package-lock.json" "$RUNTIME_DIR/package-lock.json"
  fi
  cp "$DIR/run.sh" "$RUNTIME_DIR/run.sh"
  cp "$DIR/run_named_tunnel.sh" "$RUNTIME_DIR/run_named_tunnel.sh"
  cp "$DIR/run_quick_tunnel.sh" "$RUNTIME_DIR/run_quick_tunnel.sh"
  cp "$DIR/.env.example" "$RUNTIME_DIR/.env.example"

  if [ -f "$DIR/.env" ]; then
    cp "$DIR/.env" "$RUNTIME_DIR/.env"
  fi
  if [ -f "$DIR/cloudflared/config.example.yml" ]; then
    cp "$DIR/cloudflared/config.example.yml" "$RUNTIME_DIR/cloudflared/config.example.yml"
  fi
  if [ -f "$DIR/cloudflared/config.yml" ]; then
    cp "$DIR/cloudflared/config.yml" "$RUNTIME_DIR/cloudflared/config.yml"
  fi
  if [ -d "$DIR/node_modules" ]; then
    rm -rf "$RUNTIME_DIR/node_modules"
    ditto "$DIR/node_modules" "$RUNTIME_DIR/node_modules"
  fi

  chmod +x "$RUNTIME_DIR/run.sh" "$RUNTIME_DIR/run_named_tunnel.sh" "$RUNTIME_DIR/run_quick_tunnel.sh"
}

case "$1" in
  bridge)
    LABEL="com.mt.feishu-codex-bridge"
    SOURCE_PLIST="$DIR/launchd/$LABEL.plist"
    ;;
  named-tunnel)
    LABEL="com.mt.feishu-codex-cloudflared"
    SOURCE_PLIST="$DIR/launchd/$LABEL.plist"
    ;;
  quick-tunnel)
    LABEL="com.mt.feishu-codex-quick-tunnel"
    SOURCE_PLIST="$DIR/launchd/$LABEL.plist"
    ;;
  *)
    usage
    exit 1
    ;;
esac

if [ ! -f "$SOURCE_PLIST" ]; then
  echo "Launchd template not found: $SOURCE_PLIST" >&2
  exit 1
fi

if ! plutil -lint "$SOURCE_PLIST" >/dev/null; then
  echo "Launchd template failed validation: $SOURCE_PLIST" >&2
  exit 1
fi

sync_runtime
mkdir -p "$LAUNCH_AGENTS_DIR" "$LOG_DIR" "$APP_SUPPORT_DIR"
TARGET_PLIST="$LAUNCH_AGENTS_DIR/$LABEL.plist"
cp "$SOURCE_PLIST" "$TARGET_PLIST"

launchctl bootout "$USER_DOMAIN" "$TARGET_PLIST" >/dev/null 2>&1 || true
launchctl bootstrap "$USER_DOMAIN" "$TARGET_PLIST"
launchctl enable "$USER_DOMAIN/$LABEL" >/dev/null 2>&1 || true
launchctl kickstart -k "$USER_DOMAIN/$LABEL"

echo "Installed and started $LABEL"
echo "Plist: $TARGET_PLIST"
echo "Runtime: $RUNTIME_DIR"
