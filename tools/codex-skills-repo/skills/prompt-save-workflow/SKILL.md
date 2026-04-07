---
name: prompt-save-workflow
description: Save and organize prompt deliverables for the user. Use when the user asks to generate, package, archive, iterate, or save prompts/prompts packages into folders or files. This skill decides whether to update an existing prompt in place or create a new Chinese-named folder based on whether the request is an iteration of an existing prompt or a brand-new prompt request.
---

# Prompt Save Workflow

Follow this workflow whenever the user wants prompts to be saved locally.

## Core Folder Rule

Always save prompt deliverables inside a folder.

- Never save a new prompt file directly into the workspace root as a loose file.
- For `iteration` requests, reuse the existing prompt folder and update files inside it.
- For `new` requests, create a new Chinese-named folder first, then save the prompt files into that folder.
- Even when the output is only one Markdown file, still place it inside a folder.

## Prompt Separation Rule

Save different prompts into different folders when they are not part of the same prompt package.

- If multiple prompts serve different goals, different audiences, or different topics, create separate new folders for them.
- If prompts belong to one coherent deliverable set, keep them in the same folder as one prompt package.
- Do not mix unrelated prompts such as `立项判断`, `老板汇报`, `买量素材分析`, and `用户访谈` into one new folder unless the user explicitly asks for one bundled package.
- Use the folder name to reflect the specific prompt theme rather than a broad catch-all bucket.

## Decide Update vs New

Classify the request before writing files.

- Treat the request as `iteration` when the user explicitly says it is based on an existing prompt, asks to revise, expand, optimize, rewrite, or continue a prior prompt, or points to an existing prompt file or folder.
- Treat the request as `new` when the user asks for a fresh prompt or prompt package without tying it to an existing saved prompt.
- Before deciding `new`, always scan the current workspace for likely existing prompt folders or files when the user's wording suggests this may be based on earlier work.
- If there is clear local evidence of the exact prior prompt file, update that file in place.
- If multiple candidate prior files exist and choosing the wrong one would overwrite unrelated work, ask one concise clarification question.
- If no prior file is identifiable, treat it as `new` and state that assumption briefly after saving.

## Auto-Scan Workflow

When there may be an existing prompt to iterate on, use a lightweight local scan before creating a new folder.

1. Search the current workspace for likely prompt files and prompt folders.
2. Prefer exact name matches first, then keyword matches, then nearby thematic folders.
3. Check for files with names like `*Prompt*.md`, `*prompt*.md`, `Prompt包.md`, `立项Prompt.md`, `分析Prompt.md`.
4. Check folders whose Chinese names match the user's topic, audience, or project label.
5. If one candidate is clearly the prior version, treat the task as `iteration` and update it.
6. If multiple files are close matches, avoid guessing when overwrite risk is meaningful.

Suggested scan signals:

- Same topic words, such as `塔防`, `RPG`, `发行制作人`, `副玩法`, `买量`, `立项`
- Same audience words, such as `老板`, `制作人`, `策划`, `发行`
- Same deliverable words, such as `Prompt包`, `立项Prompt`, `分析框架`, `素材策略`

## Save Rules

For `iteration` requests:

- Edit the original prompt file instead of creating a parallel copy.
- Preserve the existing folder unless the user explicitly asks to rename or restructure it.
- If the original folder contains a prompt bundle, update the most central prompt document first and keep related files consistent.
- If the folder already has a clear naming system, continue using it.
- Do not move an iterated prompt out of its existing folder.

For `new` requests:

- Create a new folder with a Chinese name.
- Use the request's core identifying information as the folder name.
- Prefer short, high-signal names such as `发行制作人`, `塔防立项`, `副玩法吸量`, `RPG承接设计`.
- Avoid generic names like `prompt`, `新prompt`, `文档1`.
- Save the new prompt into that folder as a clearly named Markdown file.
- If multiple files are generated together, keep the whole set in that same folder only when they belong to the same prompt package.
- If the request contains multiple distinct prompts, split them into separate new folders by theme, audience, or use case.

## Naming Conventions

When creating a new folder:

- Use Chinese.
- Base the name on the prompt's purpose, audience, or topic.
- Keep it concise, usually 2-8 Chinese characters plus necessary qualifiers.
- If the prompt bundle covers multiple related prompts, name the folder after the shared theme, not one sub-prompt.
- Prefer names in the form `主题`, `主题+对象`, or `主题+用途`.
- For multiple new prompts in one request, give each folder a distinct theme label rather than numbering them mechanically.

When creating a new file:

- Use Markdown by default.
- Use a descriptive Chinese filename.
- If there is already a naming pattern in the folder, follow it.
- Read `references/naming-templates.md` when choosing a default filename for a new prompt package.

## Default File Naming Templates

Use these defaults unless the user asks for a specific file name.

- Single strategic prompt: `立项Prompt.md`
- Prompt bundle: `Prompt包.md`
- Market/genre insight prompt: `市场洞察Prompt.md`
- User research prompt: `用户洞察Prompt.md`
- Buying-traffic/material analysis prompt: `买量素材Prompt.md`
- Topic/style analysis prompt: `题材风格Prompt.md`
- MVP planning prompt: `MVP方案Prompt.md`
- Framework-oriented prompt: `分析框架.md`
- Meeting-ready short prompt: `会议版Prompt.md`
- Customized prompt for an existing project: `定制版Prompt.md`

If the folder already contains one of these files, prefer updating it instead of creating a nearly identical new file.

## File Placement

- Save into the current workspace unless the user specifies another location.
- Reuse the user's existing folder structure when iterating.
- For new prompt bundles, keep all generated prompt files inside the new Chinese-named folder.
- Do not leave prompt deliverables loose at the workspace top level.
- Do not merge unrelated new prompts into one folder by convenience.

## Output Expectations

After saving:

- Tell the user whether this was treated as an `iteration` or `new` request.
- Provide the saved folder path and file path.
- Mention any assumptions only if they affected where or how the prompt was saved.
- If one request produced multiple folders, explain the split basis briefly.

## Editing Guidance

- Use `apply_patch` for in-workspace edits when possible.
- When writing outside the workspace, use the minimum necessary escalated operation.
- Do not create duplicate prompt files just because the content changed.
- Prefer updating the existing prompt document unless the user asked for variants.
