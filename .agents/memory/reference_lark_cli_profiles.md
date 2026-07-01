---
name: reference-lark-cli-profiles
description: lark-cli profile quick reference for current workspace tasks; detailed historical bridge setup is archived
metadata:
  node_type: memory
  type: reference
---

# lark-cli Profile Quick Reference

Use this only when a task needs local `lark-cli` profile selection.
Treat credentials, scopes, bridge state, and bot behavior as current-state facts that must be rechecked before use.

## Known profiles

| profile | identity | use |
|---|---|---|
| `cli_a954b67267b99bdb` | user: Jeff-汪书丞 | enterprise default profile; used by strategy database and game-data tasks |
| `personal` | bot/user for personal app | personal app experiments; use only when explicitly needed |

## Usage notes

- Default profile is the enterprise profile unless a command explicitly sets another profile.
- For personal app bot commands, use `--profile personal` and the correct `--as` identity.
- Before changing auth, scopes, bot membership, daemon state, or secrets, verify current `lark-cli profile list` / relevant status live.
- Do not rely on historical bridge setup details as current truth.

## Archive

Full historical setup notes, including personal bot bridge details and old troubleshooting, were moved to:

`archived/reference_lark_cli_profiles_full_2026-07-01.md`
