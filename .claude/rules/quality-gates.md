# 质量门禁

LLM 事实性信息处理规则和 Git 卫生规范。

## LLM 事实性信息处理

### 核心原则

**先搜后整，不能反过来。** 事实性判断必须有可追溯来源支撑，不用 LLM 通识填补事实空缺。

### 事实性 vs 分析性

需联网验证（事实性）：产品功能/参数/市场表现/发行信息/公司背景/时间点后事件

不需联网（分析性）：基于已确认事实的逻辑推导、设计模式识别、If-Then 结论提炼、已有数据结构化整理

### 执行规则

**用 LLM API 分析时**：先 WebSearch 收集素材 → 素材作为上下文喂 LLM → 要求标注来源。Prompt 必须含："只使用以上资料，不要补充你自己知道的内容。资料未覆盖的标注'资料未覆盖'。"

**Claude 自身分析时**：有 WebSearch → 先搜再答；无 WebSearch → 明确告知"基于训练数据，未经联网验证"。

### 来源标注

| 来源 | 标注 | 可用于事实判断 |
|---|---|---|
| 第一手游玩 | "第一手：实际游玩" | 是 |
| 联网搜索 | "搜索：{URL/来源}" | 是 |
| 用户提供 | "用户提供" | 是 |
| LLM 通识 | "LLM通识（未验证）" | 否 |
| 推断 | "推断：基于{已确认事实}" | 须说明依据 |

禁止：无具体来源的"玩家攻略"、无 URL 的"官方介绍"、"第一手游玩反馈"（LLM 不能游玩）。

## Git 卫生

### 原则

工作流资产入版本，生成产物入 .gitignore，每天 commit，不堆积超 24 小时未提交改动。

### 入版本判断

1. `.gitignore` 命中 → 不入
2. `archive/` / `reference/` / `workspace/projects/` 下工作流文本 → 入
3. `.claude/rules/` / `.claude/hooks/` / `.claude/references/` → 入
4. `.claude/worktrees/` → 不入
5. 脚本产物（`_数据/` / `_logs/` / `_raw/`）→ 不入
6. 非交付物二进制大文件 → 评估 LFS 或 ignore

`.gitignore` 是入版本规则的唯一真相。

### Commit 节奏

每天结束前 commit。未追踪文件即时分流：`git add` 或加 `.gitignore`。

### Worktree 协议

启动前：主目录 git status 干净 → git pull → 再建 worktree。worktree 完成后 PR/merge 回主分支。发现 worktree 缺文件时回主目录 commit + push，不手动 cp。
