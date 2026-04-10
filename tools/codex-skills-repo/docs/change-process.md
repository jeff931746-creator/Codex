# Change Process

This document defines how shared agent-team assets are changed and rolled out.

## Standard Flow

1. Classify the proposed change.
2. Edit the source-of-truth files in this repository.
3. Validate locally.
4. Review with Git.
5. Roll out to runtime projections.
6. Verify runtime health after rollout.

## Classification First

Before editing, decide whether the change belongs in:

- `rules/`
- `skills/`
- `references/`
- `profiles/`
- `overrides/`

Use `docs/asset-decision-guide.md` when the classification is unclear.

## Validation Requirements

At minimum, maintainers should run:

```bash
bash scripts/audit-skills.sh
bash scripts/doctor-agent-team.sh
```

If scripts are changed, run a realistic smoke test for the affected runtime path as well.

## Review Rules

1. Shared assets must be reviewed in Git before rollout.
2. Breaking changes require an explicit migration note in the PR or commit description.
3. Any change that increases global context footprint must justify the added value.
4. Any change that moves files or directories must verify runtime mappings afterward.

## Rollout Rules

1. Roll out through scripts, not manual copy-paste.
2. After a structural move, relink runtime projections immediately.
3. After relinking, run `doctor-agent-team.sh`.
4. If runtime health fails, stop rollout and fix the mapping first.

## Rollback Rules

1. Roll back through Git when possible.
2. Keep retired assets in `archive/` when historical reference matters.
3. If a rollout breaks runtime behavior, restore link health first, then revert content if needed.

## Temporary Policy

Until stable and canary channels exist, `main` acts as the shared stable line.

That means:

- avoid unreviewed breaking changes
- avoid risky global edits late in the day
- prefer smaller, easy-to-revert changes
