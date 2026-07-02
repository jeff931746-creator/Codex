# Quality Gates

Factuality, review discipline, and Git hygiene rules for any AI agent working in `/Users/mt/Documents/Codex-codex-work`.

## Factuality Handling

### Core Principle

Search first, then synthesize. Do not use model common knowledge to fill factual gaps.

### Factual vs Analytical

Requires current/source verification:

- product features or parameters
- market performance
- release information
- company background
- events after the knowledge cutoff
- laws, prices, schedules, live status, and other unstable facts

Does not necessarily require web verification:

- reasoning from confirmed facts
- design pattern identification
- if-then conclusions
- structuring user-provided data

### Execution Rules

When using LLM/API analysis over source material:

1. Collect source material first.
2. Feed only that material as context.
3. Ask the model to cite sources and mark uncovered claims as `资料未覆盖`.
4. The prompt must explicitly say: `只使用以上资料，不要补充你自己知道的内容。资料未覆盖的标注"资料未覆盖"。`

When an agent itself answers:

- If web/source access is available and the fact is unstable, verify first.
- If verification is not possible, say the answer is unverified and state the basis.

### Source Labels

| Source | Label | Can Support Factual Judgment |
|---|---|---|
| First-hand use | `第一手：实际使用/实际运行` | Yes |
| Web/search/source | `来源：{URL/path/source}` | Yes |
| User-provided | `用户提供` | Yes |
| Model common knowledge | `LLM通识（未验证）` | No |
| Inference | `推断：基于{已确认事实}` | Only with basis |

Forbidden: source-free claims such as `官方介绍`, `玩家攻略`, or `第一手游玩反馈` when no actual source exists.

## Review Discipline

Applies to all review and analysis tasks, including numeric review, GDD review, project initiation review, competitor scoring, and ad-buying material evaluation.

### Review Quality, Not Mere Existence

When giving a positive conclusion, do not use `the design exists` as the basis. The judgment must answer whether the design is good, reasonable, coherent, and sufficient.

Self-check: before writing `达标`, `通过`, or `合格`, ask whether the basis is merely `X exists`. If yes, add quality evaluation.

### Two Quality Layers

- Within-criterion quality: whether each individual design is reasonable.
- Cross-criterion quality: whether proportions, scale, rhythm, and long-term control work globally.

After going through individual criteria, do a global check.

### Stage Boundary

An agent may evaluate design quality in terms of function, structure, and direction when evidence supports it.

An agent must not evaluate numeric quality such as specific parameters, curve slopes, or exact balance without data.

Hard-judging numeric quality without data is filling gaps with inference and violates search-first/source-first discipline.

### Design Terminology Discipline

When writing or editing game design documents, do not invent abstract terminology that is not present in the source material, project documents, or existing feature names.

Use one of these forms instead:

- Source terms from the referenced project, feature, or planning document.
- Existing feature names already used by the project.
- Player-visible behavior chains, such as `参与 -> 击杀 / 被击杀 -> 战报 -> 复仇 -> 求助 -> 加入军团`.

Forbidden: replacing concrete gameplay behavior with self-created conceptual labels such as `具名矛盾`, `补强`, `入账`, `容器`, or similar terms unless the exact term already exists in the source material and is defined there.

Before delivery, search the edited design document for newly introduced abstract labels. If a term is not source-backed, replace it with the original source term or concrete player-visible behavior.

### References

Department review standards, such as numeric review templates, GDD writing/review standards, and project initiation review templates, should point to this section instead of copying it. This section is the source of truth for review-quality discipline.

## Git Hygiene

### Principles

- Workflow assets belong in version control.
- Generated artifacts should be ignored when appropriate.
- Do not mix unrelated changes.
- Do not revert user changes unless explicitly asked.
- Do not let workflow-rule changes linger unreviewed or uncommitted for more than a working day when version control is available.

### Versioning Judgment

1. `.gitignore` match -> do not add unless explicitly needed.
2. Workflow text under `archive/`, `reference/`, or `workspace/projects/` -> usually version.
3. Agent-neutral rules and hooks under `.agents/` -> version.
4. Runtime adapter examples under `.agents/adapters/` -> version when intentionally maintained.
5. Runtime checkpoints under `workspace/tmp/agent-checkpoints/` -> generated state, do not version.
6. Script products such as `_数据/`, `_logs/`, `_raw/` -> usually ignore.
7. Large binary non-deliverables -> evaluate LFS or ignore.

`.gitignore` is the source of truth for ignore behavior.

### Commit Rhythm

At the end of a working day or a completed workflow-maintenance task, commit scoped workflow changes when version control is available.

When committing:

- inspect status and diff
- stage only scoped files
- use a clear message
- report what was committed

Do not commit unrelated existing changes.

Inspect untracked files promptly and either version them, ignore them, or remove them if they are scratch artifacts.

### Worktree Protocol

When using a separate worktree:

1. Start from a clean main working tree unless the user explicitly asks otherwise.
2. Pull or otherwise refresh before creating the worktree when network/project policy allows it; if refresh is skipped, say why.
3. Finish through PR, merge, or an explicit handoff path.
4. If a worktree is missing required files, fix the source through version control or an explicit sync step; do not silently copy files by hand.
