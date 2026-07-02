# Workspace Guard

This directory contains local safeguards for this independent workspace.

`check-paths.sh` verifies that file-changing commands target only:

- `/Users/mt/Documents/Codex-codex-work`
- `/private/tmp`
- `/private/var/folders/wy/ljz0r5_s13lf1jlpv88cn7h00000gn/T`

It blocks writes to external project locations unless the user explicitly asks for that work and the agent intentionally bypasses this local-only guard.

Use it before commands or scripts that may create, edit, move, delete, format, or sync files.

Examples:

```bash
bash /Users/mt/Documents/Codex-codex-work/tools/workspace-guard/check-paths.sh AGENTS.md tools/workspace-guard/check-paths.sh
bash /Users/mt/Documents/Codex-codex-work/tools/workspace-guard/check-paths.sh /Users/mt/Documents/External/AGENTS.md
```

The first command exits `0`; the second exits non-zero.
