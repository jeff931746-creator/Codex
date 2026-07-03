# Task Flow And Delegation Rules

Unified task classification, gate definitions, plan requirements, delegation rules, and hook triggers for any AI agent working in `/Users/mt/Documents/Codex-codex-work`.

## Global Rules

- Classify every new task as `quick`, `standard`, or `strict`.
- `standard` and `strict` tasks must specify a task type and plan before execution.
- `strict` tasks must not skip planning.
- Complete gates in order; do not advance while the current gate is incomplete.
- If blocked, stay at the current gate, rewind, or re-plan.
- When task type changes, stop and choose the new flow through a plan.
- Delegated work inherits a bounded task type and gate.
- Re-plan when task direction changes materially.

Track each active task:

`flow intensity` · `task type` · `current gate` · `completed gates` · `next gate` · `blocked on`

## Plan Requirements

For `standard` / `strict` tasks, a plan must:

1. Summarize the intended approach.
2. Name files, systems, or behaviors that may change.
3. Explain non-obvious tradeoffs or risks.
4. Wait for user approval when the task is `strict` or high-risk.

`doc-change` and `implementation` plans must include a gate sequence section.

`knowledge-asset` plans must explicitly list:

- similar existing assets searched, with paths
- README and rule files read, with paths and summaries
- automation/script entry points checked, with paths

Missing any of the above means the plan is incomplete.

## Trigger Routing

Default to `knowledge-asset` + `strict` when the request includes:

`标准`, `规范`, `流程`, `体系`, `框架`, `方法论`, `沉淀`, `长期管理`, `长期演进`, or knowledge-asset libraries such as `知识库`, `机制库`, `题材库`, `方法论库`, `人群库`, `竞品库`, `买量组合库`, `复盘库`, `建立XX库`, `维护XX库`.

Do not trigger this route for:

- `代码库`
- `依赖库`
- `库函数`
- `标准库`
- one-off collection where the user explicitly says it does not need long-term maintenance

## GDD Writing Route

When creating a new game design document, feature requirements document, system design, gameplay design, activity/economy/monetization design, or GDD, route through `archive/skills/skills/gdd-write/SKILL.md`.

This route applies to the design-forming process itself, not only to files written to disk. It is required when the user asks for a game feature design, gameplay/activity/economy/monetization design, system design, requirements draft, direction validation draft, proposal, or feature plan, including when the requested output is chat-only, exploratory, "just a draft", "first direction", `方向稿`, `初稿`, `不落文件`, or based on an existing GDD/reference document such as `参考已有 GDD 做新方案`.

Do not bypass the route by saying the output is not a formal document, will not be written to a file, is only for discussion, or is only a preliminary version. Before G1-G6 have produced real sub-agent evidence and the required main-planner decisions, the main agent may only deliver process status, rule/standard summaries, blocking questions, or workflow plans. It must not deliver the actual feature scheme, partial feature scheme, final design direction, section draft, or complete draft in the main thread.

The GDD writing route must use `reference/部门标准/策划/gdd/多Agent设计文档工作流.md` as the workflow source, use `reference/部门标准/策划/gdd/多Agent设计文档调度规则.md` for state/rollback/checkpoint semantics, and load only the current-stage files under `reference/部门标准/策划/gdd/多Agent设计文档判断原则/`.

Before the GDD writing route starts G1, the main agent may read only routing and workflow context needed to classify the task and assemble the G1 task package. Business evidence such as reference GDDs, historical mechanism memory, competitor material, or existing design-document body text must be first interpreted by the G1 sub-agent. If the main agent has already interpreted business evidence, that interpretation is not valid workflow evidence and G1 must be restarted without inheriting the main-thread business conclusion.

The GDD writing route requires real sub-agent evidence. Main-thread simulation of G1/G2/G3/G4/G5/G6 is not valid. For any changed Markdown design document under `workspace/projects/`, except `README.md`, record `workspace/tmp/agent-checkpoints/gdd-write/<doc-id>/workflow-state.json` with `.agents/hooks/checkpoint-gdd-workflow.py`. The checkpoint must bind the target document, current document diff hash, main agent id, actual sub-agent ids and per-stage proof tokens for G1/G2/G3/G4/G5/G6, and main-planner pass decisions for M1/M2/M3/M4. The proof token for each stage must appear with that stage's sub-agent id in the current runtime transcript. The Stop hook `check-gdd-workflow.py` blocks delivery when this evidence is missing, incomplete, expired, stale, not observed in the current runtime transcript, or when the G6 evidence no longer matches the current document diff.

Do not copy the workflow or judgment principles into `.agents/`; `.agents` only routes and gates this behavior.

## Flow Types

### analysis

Use for research, comparison, synthesis, theory building, and decision support.

Gates: `intake` -> `plan` -> `evidence` -> `synthesis` -> `review` -> `delivery`

- `evidence`: conclusions have sufficient support. Factual claims about external products, games, markets, companies, or recent events require web or source evidence.
- `synthesis`: the answer is structured for decision support.
- `review`: weak claims and missing evidence are marked.

### doc-change

Use for rule edits, README updates, template changes, and design documents.

Gates: `intake` -> `plan` -> `target-inspection` -> `edit` -> `self-review` -> `validation` -> `delivery`

- `target-inspection`: affected files and current content are known. If a relevant department standard exists, confirm it has been read.
- `edit`: text changes are applied.
- `self-review`: wording conflicts, scope drift, and logic coverage are checked. If the main agent wrote or edited a design document in the current turn, the design-document review must be delegated to another worker/runtime-supported review path before delivery. Exception: a fresh session where the current agent did not participate in drafting.
- `validation`: relevant local checks are run, or skipped checks are explained.

### implementation

Use for code changes, script changes, and generated work products.

Gates: `intake` -> `plan` -> `context-inspection` -> `implementation` -> `validation` -> `review` -> `delivery`

- `context-inspection`: relevant files and constraints are understood.
- `implementation`: scoped changes are applied.
- `validation`: tests or equivalent verification are run.
- `review`: main risks, regressions, and omissions are identified.

### review

Use for code review, document review, QA, scoring, and verification.

Gates: `intake` -> `plan` -> `standard-check` -> `target-inspection` -> `findings` -> `cross-check` -> `delivery`

- `standard-check`: locate applicable standards in `reference/部门标准/` or user-provided standards. If none exist, report the gap and wait for direction.
- `standard-check` for game design documents: when the reviewed object is a game feature proposal, feature requirements document, system design, gameplay design, activity/economy/monetization design, GDD, or a user says `审核这个案子` / `review 这个设计文档`, first read `reference/部门标准/策划/gdd/GDD写作标准.md` and, when useful, `reference/部门标准/策划/gdd/GDD输出模板.md`. Then add narrower standards such as system-planning, numeric review, project-initiation, art, or development standards. Narrower standards may only supplement the GDD review; they must not replace it.
- `target-inspection`: the reviewed object is fully identified.
- `findings`: findings are based on confirmed standards, not ad hoc criteria.
- `cross-check`: findings are tied to evidence.

### collection

Use for product collection, structured import, and batch normalization.

Gates: `intake` -> `plan` -> `schema-check` -> `collection` -> `normalization` -> `validation` -> `delivery`

- `schema-check`: target fields and format are fixed.
- `collection`: source data is collected.
- `normalization`: data is mapped to the target structure.
- `validation`: obvious gaps, duplicates, and format errors are checked.

### knowledge-asset

Use for standards, knowledge bases, methodologies, long-term workflows, and anything that must evolve or be reused across sessions.

Gates: `intake` -> `plan` -> `governance-design` -> `target-inspection` -> `edit` -> `validation` -> `delivery`

`governance-design` must provide concrete paths/lists for all five fields:

| # | Field | Passing Form |
|---|---|---|
| 1 | Long-term reuse impact | List affected paths under `archive/`, `reference/`, `archive/skills/`, `.agents/`, or `archive/tools/`; if none, state `none, output only lands in workspace/` |
| 2 | Rules/directories/skills/scripts touched | List concrete paths |
| 3 | Memory/archive/reference writes | Target directory and write timing |
| 4 | Similar assets scanned | Read path list; empty list means incomplete |
| 5 | Source of truth ownership | Source-of-truth path and derived-file refresh method |

- `target-inspection`: assets listed in field 4 have actually been read.
- `edit`: scoped changes are applied.
- `validation`: memory, README, rules, and references are checked for consistency.

## Scope Changes And Correction

When the task changes materially:

1. Stop.
2. Re-plan.
3. Decide whether to change flow type.
4. Restart from the correct gate.

If classification was wrong, rewind to `intake`. Existing output becomes draft until reviewed under the correct flow.

Classification is wrong when the user points it out, when the output lacks source-of-truth ownership/lifecycle/integration relationships, or when the task creates a long-term asset while running as `doc-change` or `implementation`.


### Mandatory Independent Review For Shared Assets

For `knowledge-asset` + `strict` work that changes any long-term workflow asset under `.agents/`, `reference/`, `archive/`, `archive/skills/`, or `archive/tools/`, the main agent must not be the only actor from edit through delivery.

Hard requirements:

1. The main agent owns classification, plan, gate transitions, integration, and final delivery.
2. A delegated independent reviewer must review the changed asset scope against the applicable standard or rule source before delivery.
3. The independent reviewer must not be the same actor that authored the changes and must not own final completion.
4. Blocking findings must be fixed or explicitly escalated to the user before delivery.
5. Before delivery, declare the reviewed scope and record a structured checkpoint with `.agents/hooks/checkpoint-independent-review.py --runtime codex --reviewer-runtime <independent-agent-id> --scope <path> ...`.
6. The checkpoint must be written for the runtime that will run the Stop hook, must name a reviewer runtime different from the main runtime, and must match the current diff within the reviewed scope.
7. The checkpoint must include the required `knowledge-asset` plan fields: similar assets scanned, rules read, automation entrypoints checked, and source of truth.
8. The Stop hook `check-flow-gates.py` blocks delivery when scoped long-term assets changed but no matching passing independent review checkpoint exists.

This requirement is not optional. Local grep, diff review, or main-agent self-review does not satisfy the independent review gate.

## Delegation Rules

The main agent owns planning, gate transitions, and final delivery. Delegated workers or parallel tools handle bounded heavy work.

Main agent owns:

- task-level plan
- gate completion decisions
- gate transitions
- user approval
- final integrated answer
- flow type changes

Delegated workers must not own task-level plans, gate-transition approval, all-task completion declarations, scope changes, or review-dimension definitions.

Delegate or parallelize when:

- reading three or more files without editing
- producing large intermediate output
- doing verification, scoring, or drafting
- independent questions can run in parallel
- repetitive extraction or normalization is needed
- the main thread has enough context to integrate but should not hold all exploration detail

Before delegating, ask: do I already have a conclusion? If yes, finish locally. Do not delegate merely to validate a predetermined conclusion.

For review tasks, the main agent must locate and provide the standard first. Delegated review must not invent dimensions.

Before delegating, include:

- precise question
- relevant file paths
- task type and current gate
- expected output format

Delegated output should be compact by default, such as a short bullet list, JSON, or a summary under 300 tokens, unless the task explicitly needs more detail.

Use the current runtime's default model/tier for ordinary delegation. For fast extraction, formatting, or simple checks, use a lightweight model/tier when the runtime supports it. For unusually long reasoning chains or high-confidence judgments, use a stronger model/tier only when clearly needed.

For review delegation, the main agent must:

1. Locate the applicable standard in `reference/部门标准/` or user-provided sources.
2. Provide the standard content or precise path to the delegate.
3. Tell the delegate to evaluate against that standard and not invent review dimensions.

If no standard exists, stay at `standard-check`, report the gap, and wait for direction.

If delegated results are insufficient, stay at the current gate and narrow the question or solve locally. If multiple delegated results conflict, the main agent compares evidence and owns the final integrated judgment.

Keep the main thread focused on task type, current/completed/next gates, approved plan, confirmed conclusions, and user-visible risks. Put exploratory logs, repeated extraction, and speculative branches outside the main answer when possible.

## Context And Failure Routing

- If context pressure is noticeable, compact using the current runtime's memory protocol.
- If context use exceeds roughly 30%, compact before continuing substantial work.
- If context use exceeds roughly 60% during an already-running task, do not interrupt that task solely because of context usage. Finish the current task at the smallest safe scope, avoid optional exploration, and set `workspace/tmp/agent-checkpoints/<runtime>/context-pressure.json` to `status=pending-next-task`.
- If a new user task, material scope change, or substantial new execution would start while context use is still above roughly 60%, automatically perform a compact continuation handoff before any analysis-heavy work, file edits, rule changes, long script runs, git operations, or non-handoff delivery. Set the context-pressure checkpoint to `status=active` for that new-task gate until the handoff is complete.
- The 60% threshold is a workflow handoff brake, not a promise that the desktop app or model runtime can auto-compact. If the runtime has no programmatic context meter, treat user reports, screenshots, or visible context pressure as the signal.
- A context-pressure handoff must preserve: current user request, active workspace, governing rule sources, completed decisions, changed files or intended edits, unresolved risks, validation status, and exact next action.
- After the handoff is written or delivered, mark `workspace/tmp/agent-checkpoints/<runtime>/context-pressure.json` as `status=handoff-complete` or `status=resolved` before executing the new task.
- If the same issue fails three times, rewind to the correct gate instead of continuing in place.

## Hook Trigger Table

| Condition | Action |
|---|---|
| New task or material scope change | plan |
| Task not classified | classify |
| Request contains knowledge-asset trigger words | `knowledge-asset` + `strict` |
| `knowledge-asset` plan lacks required scan lists | reject plan |
| `doc-change` / `implementation` plan lacks gate sequence | reject plan |
| `doc-change` target has department standard but standard was not read | block edit |
| `doc-change` produces a design document but delegated self-review was not performed | block delivery |
| Classification becomes wrong mid-task | rewind to intake; output becomes draft |
| Current gate incomplete | stay at current gate |
| Context exceeds roughly 30% | compact through current runtime protocol |
| Context exceeds roughly 60% during current task | finish current task narrowly; set context-pressure checkpoint to pending-next-task |
| New task starts while context remains above roughly 60% | auto-create handoff first; set context-pressure checkpoint active until complete |
| Same issue fails three times | rewind |
| Repeated failure or direction drift | rewind |
| Target drifts into a new task | rewind and re-plan |
| Read-heavy/noisy/verification-only work | delegate or parallelize |
| Shared assets edited | local validation + Git review + independent-review checkpoint |
| `knowledge-asset` + `strict` changes scoped long-term workflow assets without matching independent-review checkpoint | block delivery |
| `analysis-scaffold`: deliverable text violates `reference/部门标准/策划/机制拆解/拆解质量标准.md` expression requirements | block delivery; return to the standard and rewrite as natural conclusion + logic paragraphs |
| Game design document/case review starts without GDD standard in `standard-check` | rewind to `standard-check`; previous output is draft until checked against GDD |
| New game design document/GDD writing starts without `gdd-write` and the multi-Agent workflow source | rewind to GDD writing route |
| GDD writing main agent interprets business evidence before G1 | discard that interpretation as workflow evidence; restart G1 with an unpolluted task package |
| Game feature/system/activity/economy/monetization design answer is being formed in chat without `gdd-write`, even if described as draft, direction, discussion, partial feature scheme, section draft, or no-file output | block delivery; rewind to GDD writing route; do not deliver the feature scheme from the main thread |
| User provides an existing GDD/reference document and asks to design a related feature without `gdd-write` | block delivery; rewind to GDD writing route |
| Changed design document covered by the GDD writing route lacks `gdd-write` workflow evidence with actual sub-agent ids | block delivery; main-thread simulation is invalid |
