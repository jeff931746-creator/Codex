# Git Hygiene

本规则定义工作目录的 Git 卫生约定，目的是让 git 状态成为唯一真相源，避免主目录长期堆积未提交改动导致 worktree 看不到工作流资产。

## 一句话原则

```text
工作流资产入版本，生成产物入 .gitignore，每天 commit，不在工作目录里堆积超过 24 小时的未提交改动。
```

## 入版本规则（由 .gitignore 兜底）

判断一个文件是否入版本，按以下顺序：

1. **路径在 `.gitignore` 命中** → 不入版本，不需要再判断
2. **路径在 `archive/`、`reference/`、`workspace/projects/` 下，且是 `.md` / `.py` / `.sh` / `.yaml` / `.json` 等工作流文本** → 入版本
3. **路径在 `.claude/rules/`、`.claude/hooks/`、`.claude/agents/` 下** → 入版本（这些是 Claude Code 工作流配置）
4. **路径在 `.claude/worktrees/` 下** → 不入版本（worktree 是 git worktree 机制创建的，本身已独立追踪）
5. **路径在 `archive/tools/scripts/*_数据/`、`_logs/`、`_raw/`、`_去重前备份/` 这类子目录下** → 不入版本（脚本产物）
6. **二进制大文件（图片、视频、压缩包、PDF、docx 等），且不是项目交付物** → 评估是否需要 Git LFS 或直接 ignore；不要直接塞进版本

判断不了的情况：单独问，不要默认入版本，也不要默认 ignore。

## .gitignore 是主数据

入版本规则的唯一真相是根目录 `.gitignore`。本规则文件只解释 why 和工作流约定，不维护文件名清单。

需要新增忽略规则时：
- 改 `.gitignore` 而不是改本文件
- 改完用 `git check-ignore -v <路径>` 验证规则命中
- 优先用具体路径或具体后缀模式，不加 `*.md`、`*` 这种宽通配（避免误伤未来的工作流文件）

## Commit 节奏

- **每天结束前 commit**：当天的所有改动当天 commit，即使是"草稿状态"，也用 WIP commit 兜底
- **不堆积**：主目录不允许有超过 24 小时的 modified 文件
- **未追踪文件即时分流**：发现一个新文件，立即决定是 `git add` 还是加 `.gitignore`；不允许长期处于 "untracked" 状态

## Worktree 工作流

每次启动 worktree 前：

1. 主目录 `git status` 必须干净（或只剩明确不入版本的 untracked）
2. 主目录 `git pull` 同步远端
3. 再用 `git worktree add` 或 `EnterWorktree` 创建新 worktree
4. worktree 完成后通过 PR / merge 回主分支

如果发现 worktree 里看不到主目录的某个文件：
- 不要从主目录手动 `cp` 复制（这只是临时绕过，会让两端再次发散）
- 回主目录把这个文件 `git add` + commit，然后在 worktree `git pull` 同步

## 失败模式与对策

| 失败模式 | 表现 | 对策 |
|---|---|---|
| 工作流资产从未 commit | worktree 看不到主目录新建的 `.md` 文件 | 主目录立即 `git add` + commit，worktree pull |
| 脚本产物堆积 | 主目录 `git status` 出现成百上千个 untracked 数据文件 | 加 `.gitignore`，必要时把已追踪的产物 `git rm --cached` |
| 多个 worktree 同时改 main 同一文件 | merge 时反复冲突 | 同一文件不应在多个 worktree 并行修改；先合并一个再开下一个 |
| 主目录长期 dirty | worktree 启动条件不满足，被迫绕过 | 每天结束前 commit 兜底，必要时用 `git stash` 暂存 |

## 例外

- 临时排查问题的本地脚本：放 `/tmp/`（已在 `.gitignore`）
- 用户私人草稿不打算分享：放 `workspace/playground/`（按需 ignore）
- 大型本地参考资料（如《立项白皮书》原文）：按现行做法 ignore，不入远端

## 相关文件

- `.gitignore`（根目录）：入版本规则的唯一真相
- `CLAUDE.md`（项目级）：资料导航表中索引本文件
- `.claude/rules/workflow-chain.md`：工作流层级架构，理解 `archive/` 和 `reference/` 的边界
