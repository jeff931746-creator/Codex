# Codex Skills Repo

This repository is the source of truth for custom Codex skills.

## Layout

- `skills/`: active custom skills
- `archive/`: retired skills kept for reference
- `catalog.yaml`: maintenance inventory for owners, status, scope, and notes
- `scripts/link-skills.sh`: symlink active skills into a target Codex skills directory
- `scripts/audit-skills.sh`: quick structural checks for required files

## Recommended Workflow

1. Edit skills in this repository, not directly in the runtime skills directory.
2. Review changes with Git before rollout.
3. Use `scripts/audit-skills.sh` after edits.
4. Use `scripts/link-skills.sh <target-skills-dir>` to link active skills into runtime.

## Runtime Recommendation

- Keep reusable cross-project skills in the repo and link them into the runtime directory.
- Keep project-specific skills in that project's `.agents/skills/`.
- Move retired skills into `archive/` instead of deleting them immediately.

## Current Migration Note

The custom skills in this repo were copied from `/Users/mt/.codex/skills` as the first migration step.
After review, switch the runtime directory to symlinks so future edits happen here by default.
