# Asset Decision Guide

Use this guide to decide where a new team instruction belongs.

## Put It In `rules/` When

- the content is a trigger or routing layer
- the content selects standards by file glob, language, or scenario
- the content should stay short and selective

Do not put long explanations in `rules/`.

## Put It In `skills/` When

- the content is an execution playbook or SOP
- the task needs a repeatable workflow
- the task may use helper scripts, agents, or structured references

Skills should explain how to do the work, not act as a dumping ground for every policy document.

## Put It In `references/` When

- the material is long
- the content is useful but not needed on every invocation
- the information is better loaded on demand than injected by default

Examples:

- architecture notes
- domain-specific standards
- API schemas
- troubleshooting guides

## Put It In `profiles/` When

- the logic is runtime-specific
- the same shared asset needs different exposure in Cursor and Claude
- the content describes mapping, installation, or runtime wiring rather than policy itself

## Put It In `overrides/` When

- the behavior is project-specific
- the change should not affect every team or repository
- the rule depends on one project's domain, naming, or workflow

Use `overrides/` before copying and forking a shared asset unless the project truly needs a fully local asset.

## Keep It Out Of Shared Global Assets When

- it contains secrets
- it only serves one temporary experiment
- it is not yet proven reusable
- it expands default context without clear payoff
