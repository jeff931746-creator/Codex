# Codex Workspace

This workspace is organized into a few stable top-level groups.

## Layout

- `projects/`: active project folders and shared capability packs
- `workspace/`: active execution space for projects, playground work, and temporary files
- `archive/`: accumulated methods, reusable materials, mechanism studies, and tools
- `reference/`: stable standards, templates, and department rules
- `tools/`: reusable utilities and local tool repos

## Usage

Open files from the grouped directories directly. The workspace root is intentionally kept minimal.

## Directory Hygiene

不同类型的目录采用不同模板，不把 `skills/` 的打包规范原样套到所有地方。

共通原则：

- 长期保留的目录应有 `README.md` 或等价入口说明。
- 原始资料、过程产物、最终产物分开存放。
- 临时文件放进 `tmp/` 或局部 `_sandbox/`，不要混入长期目录。
- 可交付文件和测试、评估、缓存文件分开。
- `.DS_Store`、缓存、安装包、下载包、运行时依赖不应作为工作区资产保留。
- 只有可分发对象才需要明确打包边界，例如 skill 的 `.skill` 包需要排除 `evals/` 和 `tests/`。

## Session Protocol

The workspace follows the root [`CLAUDE.md`](/Users/mt/Documents/Codex/CLAUDE.md) session protocol, including memory loading, routing, compacting, rewinding, and subagent delegation.

## Knowledge Rule

- Reusable materials, mechanism studies, external structured data, and approved reusable analysis belong under `archive/资料/`.
- Reusable methods belong under `archive/方法论/`.
- Stable standards and templates belong under `reference/`, and require explicit user permission before modification.
- Execution artifacts belong under `workspace/projects/`; temporary drafts belong under `workspace/tmp/`.
- `research/` is ignored local/deprecated space and is not the canonical knowledge base.

## Current Map

### Workspace

- `workspace/projects`
- `workspace/playground`
- `workspace/tmp`

### Archive

- `archive/资料`
- `archive/方法论`
- `archive/经验`
- `archive/skills/skills`
- `archive/tools`

### Reference

- `reference/部门标准`
- `reference/模板`

### Tools

- `tools/codex-guard`
- `tools/breakdown-worker`
- `archive/tools/services`
- `archive/tools/repos`
- `archive/tools/model-tools`
- `archive/tools/scripts`
- `archive/skills/skills`

Most reusable tooling now lives under `archive/tools/`; root-level `tools/` is kept for active Codex-facing guards and lightweight entrypoints.
