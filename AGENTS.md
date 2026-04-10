# Workspace Rules

This workspace is for workflow-related assets only.

## Scope

- Keep only files, scripts, notes, research, prompts, and tools that directly support the active workflow.
- Prefer placing work in the existing top-level folders: `projects/`, `research/`, `tools/`, `playground/`, and `tmp/`.

## Software And Runtime Policy

- Do not install software into this workspace by default.
- Do not add local runtimes, SDKs, package manager globals, app installers, or downloaded binary bundles under this workspace unless the user explicitly approves them as workflow-critical.
- If a task can be completed with existing system tools or already-available dependencies, prefer that path.
- If new software appears necessary, stop and ask before installing, downloading, or vendoring it into the workspace.

## Cleanup Expectations

- Treat `tmp/` as scratch space for temporary artifacts.
- Remove temporary installers, caches, extracted runtimes, and other non-workflow files after use unless the user explicitly asks to keep them.
- Avoid leaving behind large support files that are not part of the ongoing workflow.

## Tooling Exceptions

- Reusable scripts or tool repos may live in `tools/` when they directly support this workflow.
- Keep tooling minimal and purpose-built; avoid general environment setup inside this workspace.
