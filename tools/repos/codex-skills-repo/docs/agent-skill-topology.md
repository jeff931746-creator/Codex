# Agent Skill Topology

This document defines the recommended relationship between agents and skills for the current Codex workspace.

The goal is not to create a large abstract framework. The goal is to keep the system stable, reusable, and easy to evolve across projects.

## 1. Core Model

Use this mental model:

- `agent` = role and execution boundary
- `skill` = reusable workflow and task method
- `references` = long material loaded on demand
- `scripts` = deterministic execution support
- `rules` = lightweight routing layer

In short:

`agent decides who works`
`skill decides how the work is done`

Do not use agents as knowledge dumps.
Do not use skills as fake personalities.

## 2. Recommended Minimal Topology

Start with four stable agent roles only.

### A. Coordinator

Purpose:

- understand the user request
- decide whether the task is generation, analysis, review, collection, or execution
- choose which skills are needed
- decide whether work should stay local or be delegated

Owns:

- task decomposition
- routing
- output integration
- final decision and handoff

Should not own:

- long domain instructions
- detailed SOP text
- project-specific schemas

### B. Explorer

Purpose:

- inspect codebases, folders, documents, and local structures
- answer bounded questions
- gather context for the coordinator or worker

Owns:

- repository exploration
- file discovery
- structural comparison
- evidence gathering

Should not own:

- long-running execution workflows
- final synthesis standards

### C. Worker

Purpose:

- produce artifacts
- edit files
- run deterministic workflows
- generate output using a selected skill

Owns:

- implementation
- content generation
- file organization
- script-driven production work

Should not own:

- broad routing policy
- final acceptance criteria

### D. Reviewer

Purpose:

- evaluate outputs against a standard
- score, reject, or send work back
- identify rollback and stop conditions

Owns:

- structured review
- scoring
- risk callouts
- pass, hold, rollback, or return decisions

Should not own:

- primary generation
- exploratory data gathering unless explicitly required

## 3. Recommended Mapping For Your Current Workflow

For the workflows already active in this workspace, use this mapping.

### Shared agent roles

- `coordinator`: route the request and assemble the workflow
- `explorer`: inspect project structure, documents, and status
- `worker`: generate prompts, organize files, update templates, run scripts
- `reviewer`: run structured review and scoring

### Shared skills

These already fit the current shared layer well:

- `prompt-save-workflow`
- `chat-archive-cleaner`
- `产品收集`
- `forevernine-material-downloader`

### Skills that should be added next

These are strong candidates based on current repeated work:

- `立项评审`
- `纸面原型生成`
- `纸面原型评审`
- `立项预演文件结构整理`

These should be skills, not agents, because they are repeatable workflows rather than independent organizational roles.

## 4. What Belongs In A Skill

Put something in `skills/` when:

- the task repeats across requests or projects
- the task has a stable SOP
- the task benefits from helper scripts or references
- the task needs a reusable input and output structure

Examples:

- paper prototype generation
- paper prototype review
- prompt packaging and save rules
- product collection and structured import

Do not create a skill when:

- the task is a one-off
- the task is just a long reference note
- the task is only a routing decision

## 5. What Belongs In An Agent

Create or formalize an agent role when:

- work needs clear ownership
- context should be isolated
- tasks benefit from parallel execution
- review should be separated from generation

Examples:

- one role generates a paper prototype
- one role reviews it
- one role coordinates the workflow and decides rollback

Do not create a separate agent for every skill.

Bad pattern:

- `paper-prototype-agent`
- `paper-prototype-review-agent`
- `prompt-save-agent`
- `feishu-agent`

This usually creates overlapping roles and bloated routing.

Better pattern:

- one `worker` agent can use multiple skills
- one `reviewer` agent can review many kinds of outputs

## 6. Shared vs Project Local

Keep the current shared source-of-truth model.

### Shared global layer

Path:

- [`tools/codex-skills-repo`](/Users/mt/Documents/Codex/tools/codex-skills-repo)

Use for:

- cross-project workflows
- stable review standards
- shared utilities
- shared references

### Runtime layer

Path:

- [`~/.codex/skills`](/Users/mt/.codex/skills)

Rule:

- runtime only
- do not edit here directly
- keep symlink projection behavior

### Project local layer

Recommended future path inside a project:

```text
<project-root>/
  .agents/
    skills/
    rules/
    references/
```

Use project-local assets when:

- the workflow depends on project-only schema
- naming is project-specific
- prompts should not affect other teams
- the logic is still experimental

Use shared assets when:

- the workflow is reused across multiple projects
- the standard should stay consistent globally

## 7. Recommended Directory Strategy

Keep the current shared repository layout. It is structurally sound:

```text
tools/codex-skills-repo/
  docs/
  rules/
  skills/
  references/
  profiles/
  overrides/
  scripts/
  archive/
```

What to add next is not more top-level categories.
What to add next is actual content in the thin layers:

- add real `rules/` entries
- add project examples under `overrides/` or project-local `.agents/`
- add one or two documented agent mappings in `profiles/`

## 8. Current Assessment

The current structure is good at the skill layer and not yet mature at the agent layer.

More specifically:

- shared skill source-of-truth is correct
- runtime projection design is correct
- documentation and governance are stronger than average
- skill classification is already healthy
- project-local override usage is not yet active enough
- rules and agent topology are still underbuilt

So the right next move is:

- do not redesign the whole repo
- do not add many new top-level folders
- do not multiply agents early
- instead formalize a small role topology and add missing workflow skills

## 9. Recommended Rollout Order

Follow this order.

### Step 1

Freeze the current shared layout as the stable base.

Do not change:

- source-of-truth in `tools/codex-skills-repo`
- runtime symlink projection into `~/.codex/skills`

### Step 2

Add three workflow skills first:

- `立项评审`
- `纸面原型生成`
- `纸面原型评审`

These will give the biggest immediate return for the current workspace.

### Step 3

Start using project-local `.agents/skills/` for one real project with strong local workflow differences.

Good first candidates:

- a project with custom collection schema
- a project with custom paper prototype review rules

### Step 4

Add lightweight rules that route common tasks to the correct skill.

Examples:

- route prompt packaging requests to `prompt-save-workflow`
- route product collection tasks to `产品收集`
- route paper prototype generation to `纸面原型生成`
- route paper prototype scoring to `纸面原型评审`

### Step 5

Document one concrete runtime-facing agent mapping in `profiles/`.

Only after the skills and routing are stable should you formalize more explicit agent files.

## 10. Practical Standard

Use this decision rule:

- if the problem is repeatable, make a skill
- if the problem is role separation, make an agent
- if the problem is long material, make a reference
- if the problem is trigger logic, make a rule
- if the problem is one-project divergence, make a project-local override

## 11. Suggested Next Concrete Build

If continuing from the current workspace, the best next concrete build is:

1. add a shared skill for `纸面原型生成`
2. add a shared skill for `纸面原型评审`
3. add a shared skill or override for `立项预演文件结构整理`
4. define one minimal role map:
   - coordinator
   - explorer
   - worker
   - reviewer
5. pilot one project-local `.agents/skills/` folder on a real project before broad rollout

This gets you the benefits of an agent-skill system without overbuilding it.
