#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_ROOT="$REPO_ROOT/skills"
TARGET_DIR="${1:-}"
SKILL_NAME="${2:-}"

if [[ -z "$TARGET_DIR" ]]; then
  echo "usage: $0 <target-skills-dir> [skill-name]"
  exit 1
fi

mkdir -p "$TARGET_DIR"

timestamp="$(date +%Y%m%d-%H%M%S)"

if [[ -n "$SKILL_NAME" ]]; then
  skill_dir="$SKILLS_ROOT/$SKILL_NAME"
  if [[ ! -d "$skill_dir" ]]; then
    echo "missing skill: $skill_dir"
    exit 1
  fi
  skill_dirs=("$skill_dir")
else
  skill_dirs=("$SKILLS_ROOT"/*)
fi

for skill_dir in "${skill_dirs[@]}"; do
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
