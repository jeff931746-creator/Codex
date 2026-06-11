# 任务流程与委派规则

统一的任务分类、gate 定义、Plan 要求、委派规则和 Hook 触发表。

## 全局规则

- 每个新任务先分类流程强度：`quick`（直接执行）/ `standard`（极简 plan）/ `strict`（完整 plan）
- `standard` 和 `strict` 必须指定 task type，先 plan 再执行；`strict` 不得跳过 plan
- gate 按序完成，未完成不得推进；阻断时停在当前 gate、rewind 或重新 plan
- 任务变类型时停下，通过 plan 选择新 flow
- 子 agent 继承有范围的 task type 和 gate，不得跳 gate
- 任务方向实质变化时重新 plan

每个活跃任务追踪：flow intensity · task type · current gate · completed gates · next gate · blocked on

## Plan 要求

`plan` 是 standard/strict 任务的强制第一步。每个 plan 必须：
1. 概述预期方式
2. 点名可能改动的文件/系统/行为
3. 说明非显然的权衡或风险
4. 等待用户批准后再执行

`doc-change` 和 `implementation` plan 必须包含 **gate 执行序列小节**，无此小节视为不合格。

`knowledge-asset` plan 必须显式列出：已搜索的同类现有资产（路径列表）、已读取的 README 和规则文件（路径 + 摘要）、已检查的自动化脚本入口（路径列表）。缺少任一项视为不合格。

### 触发词路由

含以下词语时默认 `knowledge-asset` + `strict`：`标准` / `规范` / `流程` / `体系` / `框架` / `方法论` / `沉淀` / `长期管理` / `长期演进`，以及知识资产类库（`知识库` / `机制库` / `题材库` / `方法论库` / `人群库` / `竞品库` / `买量组合库` / `复盘库` / `建立XX库` / `维护XX库`）。

不触发：`代码库` / `依赖库` / `库函数` / `标准库`；用户明确说"不需要长期维护"的单次收集。

## Flow Types

### analysis

用于：研究、比较、综合、理论构建、决策支持

Gates：`intake` → `plan` → `evidence` → `synthesis` → `review` → `delivery`

- `evidence`：结论有足够支撑材料；**外部产品/游戏/市场的事实性声明必须有 WebSearch 结果支撑**
- `synthesis`：答案已组织且可辅助决策
- `review`：弱声明和缺失证据已标出

### doc-change

用于：规则编辑、README 更新、模板变更、设计文档

Gates：`intake` → `plan` → `target-inspection` → `edit` → `self-review` → `validation` → `delivery`

- `target-inspection`：受影响文件和当前内容已知；**需求 GDD 必须确认已读 `reference/部门标准/策划/gdd/GDD写作标准.md`**
- `edit`：文本变更已应用
- `self-review`：措辞冲突、范围偏移、逻辑覆盖已检查；**需求 GDD 的 self-review 必须走 `gdd-review` Skill，不可内联**
- `validation`：相关资产的本地检查已运行

### implementation

用于：代码变更、脚本变更、生成工作产物

Gates：`intake` → `plan` → `context-inspection` → `implementation` → `validation` → `review` → `delivery`

- `context-inspection`：相关文件和约束已理解
- `implementation`：范围内变更已应用
- `validation`：测试或等效验证已运行
- `review`：主要风险、回归和遗漏已识别

### review

用于：代码审查、文档审查、QA、评分、验证

Gates：`intake` → `plan` → `standard-check` → `target-inspection` → `findings` → `cross-check` → `delivery`

- `standard-check`：已在 `reference/部门标准/`（worktree 和主仓库 `/Users/mt/Documents/Codex/reference/` 都检查）定位到适用标准；无标准时向用户报告缺口并等待指示
- `target-inspection`：被审查对象已完整识别
- `findings`：基于已确认标准产出了具体问题或无问题结论
- `cross-check`：发现项与证据已关联

### collection

用于：产品收集、结构化导入、批量归一化

Gates：`intake` → `plan` → `schema-check` → `collection` → `normalization` → `validation` → `delivery`

- `schema-check`：目标字段和格式已固定
- `collection`：源数据已收集
- `normalization`：数据已映射到目标结构
- `validation`：明显缺口、重复和格式错误已检查

### knowledge-asset

用于：标准、知识库、方法论、长期工作流——任何需跨会话演进和复用的产物

Gates：`intake` → `plan` → `governance-design` → `target-inspection` → `edit` → `validation` → `delivery`

- `governance-design`：以下 5 字段全部给出具体路径/列表（yes/no 或抽象原则不合格）：

| # | 字段 | 合格形式 |
|---|---|---|
| 1 | 长期复用影响 | 列出 `archive/`、`reference/`、`archive/skills/`、`archive/tools/` 下受影响路径；若无声明 `无,产物只落 workspace/` |
| 2 | 触及的规则/目录/Skill/脚本 | 列出具体路径 |
| 3 | 记忆/archive/reference 写入 | 目标目录 + 写入时机 |
| 4 | 已扫描的同类资产 | 已读路径列表（空列表 = 未完成） |
| 5 | 主数据所有权 | 唯一真相源路径 + 派生文件刷新方式 |

- `target-inspection`：governance-design 第 4 项资产已实际读取
- `edit`：范围内变更已应用
- `validation`：记忆、README、相关规则的引用一致性已检查

## Scope 变更与纠错

任务实质变化时：停下 → 重新 plan → 决定是否换 flow type → 从正确 gate 重启。

分类错误 rewind 到 intake。触发条件：用户指出分类错误、产物缺主数据所有权/生命周期/集成关系、实际产出长期资产但跑的是 doc-change/implementation。已产出物降为 draft。

## 委派规则

主 agent 拥有 plan、gate 转换和最终交付。子 agent 处理有边界的重工作。

### 所有权边界

**主 agent 独占**：任务级 plan、gate 完成判定、gate 转换、用户审批、最终整合答案、flow type 切换

**子 agent 不得拥有**：任务级 plan、gate 转换审批、全任务完成声明、scope 变更、review 评审维度定义（必须由主 agent 提供标准）

### 何时委派

任一条件即委派：读 ≥3 文件但不编辑、产生大量中间输出、工作是验证/评分/起草、可并行为独立问题、重复性提取/归一化、主线程已有足够上下文做综合但没空间保留探索细节。

### 套娃禁止

委派前自检：**我对这个问题有结论了吗？** 有 → 本地完成；无 → 给子 agent 开放问题，prompt 不预埋方向。"有结论 + 委托验证" = 套娃，无条件禁止。

**主 agent 本轮写过/改过的设计文档**，审核必须走子 agent。豁免：全新 session 且本轮未参与写作。

### Review 委派的 Standard-First 要求

委派 `findings` gate 前，主 agent 必须：
1. 在 `reference/部门标准/` 定位适用标准（worktree + 主仓库两个路径）
2. 将标准内容或精确路径写入子 agent prompt
3. 明确指示子 agent 按提供的标准评审，不得自定义维度

无标准时停在 standard-check gate，向用户报告缺口，等待指示后再推进。

### 子 agent 合约

每次委派包含：精确问题、相关文件路径、task type + 当前 gate、输出格式（≤300 tokens 摘要 / bullet / JSON）。

| 场景 | 模型 |
|---|---|
| 一般委派 | 继承主 agent（不传 model） |
| 快速提取/格式归一/简单校验 | `haiku` |
| 超长推理链/高置信度判断 | `opus`（仅在明确需要时） |

子 agent 结果不足：留在当前 gate，窄化问题重新委派或本地解决。多个子 agent 矛盾：主 agent 比对证据后整合发布。

### 上下文预算

主线程只保留：task type、当前/已完成/下一 gate、approved plan、已确认结论、用户可见风险。探索笔记、逐文件读取日志、推测分支一律委派。

## Hook 触发表

| 条件 | 动作 |
|---|---|
| 新任务或范围实质变化 | plan |
| 任务未分类 | 分类 |
| 请求含触发词（标准/流程/体系/框架/方法论/沉淀/长期管理，知识资产类库） | `knowledge-asset` + `strict`，进入 governance-design |
| knowledge-asset plan 缺 3 项扫描清单 | 拒绝 plan |
| doc-change / implementation plan 缺 gate 序列 | 拒绝 plan |
| doc-change 目标是设计文档，edit 前未读 GDD 标准 | 阻断 edit |
| doc-change 产出设计文档但 self-review 未交子 agent | 阻断交付 |
| 分类中途发现错误 | rewind 到 intake，已产出降 draft |
| 当前 gate 未完成 | 停在当前 gate |
| 上下文 >30% | compact |
| 上下文 >60% 或失败分支 ≥3 | clear |
| 同一问题连续失败 ≥3 | rewind |
| 目标偏移成新任务 | rewind |
| 读密集/噪声大/仅验证 | subagent |
| 编辑后涉及共享资产 | 本地验证 + Git review |
