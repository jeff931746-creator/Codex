# Codex Workspace

This workspace is organized into a few stable top-level groups.

## Layout

- `projects/`: active project folders and shared capability packs
- `research/`: canonical knowledge base, whitepapers, and durable reference material
- `tools/`: reusable utilities and local tool repos
- `playground/`: ad hoc demos and experiments
- `tmp/`: local scratch space that is ignored by Git

## Usage

Open files from the grouped directories directly. The workspace root is intentionally kept minimal.

## Session Protocol

The workspace follows the root [`CLAUDE.md`](/Users/mt/Documents/Codex/CLAUDE.md) session protocol, including memory loading, routing, compacting, rewinding, and subagent delegation.

## Knowledge Rule

- All durable knowledge capture, notes, research, and reusable references must be stored under `research/资料/`.
- Other top-level folders may contain project work, tools, demos, or scratch files, but not the canonical knowledge base.
- If a task produces reusable analysis or breakdowns, archive the final output in `research/资料/`, even if the work was performed from a project folder.

## Current Map

### Projects

- `projects/00-共享能力`
- `projects/10-立项预演`

### Research

- `research/立项白皮书`
- `research/资料`

### Tools

- `tools/codex-desktop-bridge`
- `tools/codex-skills-repo`
- `tools/feishu-codex-bridge`
- `tools/gemini-breakdown-worker`
- `tools/gemma4`

### Playground

- `playground/web-demo`
