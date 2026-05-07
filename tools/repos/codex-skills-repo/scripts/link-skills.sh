#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_ROOT="$REPO_ROOT/skills"
TARGET_DIR="${1:-}"

if [[ -z "$TARGET_DIR" ]]; then
  echo "usage: $0 <target-skills-dir>"
  exit 1
fi

mkdir -p "$TARGET_DIR"

timestamp="$(date +%Y%m%d-%H%M%S)"

for skill_dir in "$SKILLS_ROOT"/*; do
  [[ -d "$skill_dir" ]] || continue
  skill_name="$(basename "$skill_dir")"
  target_path="$TARGET_DIR/$skill_name"

  if [[ -L "$target_path" ]]; then
    current_target="$(readlink "$target_path")"
    if [[ "$current_target" == "$skill_dir" ]]; then
      echo "ok: $skill_name already linked"
      continue
    fi
  fi

  if [[ -e "$target_path" && ! -L "$target_path" ]]; then
    backup_path="${target_path}.backup-${timestamp}"
    mv "$target_path" "$backup_path"
    echo "backup: $target_path -> $backup_path"
  elif [[ -L "$target_path" ]]; then
    rm "$target_path"
  fi

  ln -s "$skill_dir" "$target_path"
  echo "linked: $target_path -> $skill_dir"
done
