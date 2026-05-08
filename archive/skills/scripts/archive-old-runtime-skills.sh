#!/usr/bin/env bash

set -euo pipefail

ARCHIVE_ROOT="/Users/mt/Documents/Codex/codex-skills-repo/archive"
SOURCE_ROOT="/Users/mt/.codex/skills"
STAMP="${1:-20260407-181622}"
TARGET_DIR="$ARCHIVE_ROOT/runtime-backups-$STAMP"

mkdir -p "$TARGET_DIR"

shopt -s nullglob
for path in "$SOURCE_ROOT"/*.backup-"$STAMP"; do
  name="$(basename "$path")"
  mv "$path" "$TARGET_DIR/$name"
  echo "archived: $path -> $TARGET_DIR/$name"
done
