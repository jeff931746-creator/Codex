# Naming Templates

Use this file when creating a new prompt folder or choosing a default Markdown filename.

## Folder-First Rule

Always create or reuse a folder before saving prompt files.

- New prompt request: create a new Chinese-named folder first.
- Iteration request: reuse the existing folder.
- Single-file output still belongs inside a folder.

## Prompt Separation Rule

Split different new prompts into different folders unless they clearly belong to one package.

Use separate folders when prompts differ by:

- topic
- audience
- business goal
- usage stage
- output style

Examples of prompts that should usually go into separate folders:

- `塔防立项`
- `老板汇报`
- `买量素材策略`
- `用户访谈`
- `RPG承接设计`

Examples of prompts that may stay in one folder:

- one main prompt plus its short version
- one prompt package with total version, meeting version, and customized version
- one topic-specific bundle for the same audience and same task chain

## Folder Naming Patterns

Prefer short Chinese folder names based on one of these patterns:

- `主题`
- `主题+用途`
- `主题+对象`
- `主题+方向`

Examples:

- `发行制作人`
- `塔防立项`
- `RPG承接设计`
- `副玩法吸量`
- `买量素材策略`
- `市场洞察框架`
- `老板汇报Prompt`

Avoid:

- `prompt`
- `新Prompt`
- `提示词`
- `文档`
- `文件夹1`

## Default Markdown Filenames

Choose the closest default and reuse it on iteration:

- `立项Prompt.md`
- `Prompt包.md`
- `市场洞察Prompt.md`
- `买量素材Prompt.md`
- `题材风格Prompt.md`
- `MVP方案Prompt.md`
- `分析框架.md`
- `会议版Prompt.md`
- `定制版Prompt.md`

## Reuse Rule

When iterating on an existing prompt set:

- Reuse the existing folder.
- Reuse the closest existing file.
- Only create a new file when the user explicitly asks for an additional variant rather than a revision.
