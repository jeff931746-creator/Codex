# Agent Team Repo

This repository is the source of truth for shared AI coding governance assets.

## Layout

- `rules/`: lightweight trigger rules and routing logic
- `skills/`: active custom skills and SOP-style execution guides
- `references/`: long-form reference material loaded on demand
- `profiles/`: editor or runtime specific mappings such as Cursor and Claude
- `overrides/`: project-local exceptions or extensions layered on top of shared defaults
- `archive/`: retired skills kept for reference
- `docs/`: usage policy, contribution rules, and change process
- `catalog.yaml`: maintenance inventory for owners, status, scope, and notes
- `scripts/link-skills.sh`: symlink active skills into a target Codex skills directory
- `scripts/audit-skills.sh`: quick structural checks for required files
- `scripts/doctor-agent-team.sh`: health check for the repo layout and runtime links

## Recommended Workflow

1. Edit skills in this repository, not directly in the runtime skills directory.
2. Keep shared instructions slim at the entry layer; move long details into `references/`.
3. Review changes with Git before rollout.
4. Use `scripts/audit-skills.sh` after skill edits.
5. Use `scripts/doctor-agent-team.sh` before rollout or after moving the repo.
6. Use `scripts/link-skills.sh <target-skills-dir>` to link active skills into runtime.

## Operating Rules

Team usage rules and constraints live in:

- `docs/usage-policy.md`
- `docs/change-process.md`
- `docs/asset-decision-guide.md`

## Runtime Recommendation

- Keep reusable cross-project skills in the repo and link them into the runtime directory.
- Keep project-specific skills in that project's `.agents/skills/`.
- Keep high-frequency routing logic in `rules/`; keep long specifications in `references/`.
- Use `overrides/<project>/` when one project needs local policy without forking shared defaults.
- Move retired skills into `archive/` instead of deleting them immediately.

## Current Migration Note

The custom skills in this repo were originally copied from `/Users/mt/.codex/skills`.
The active runtime symlinks now point to this repo under `tools/codex-skills-repo`.
