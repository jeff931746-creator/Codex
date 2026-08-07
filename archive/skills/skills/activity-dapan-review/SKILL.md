---
name: activity-dapan-review
description: >-
  活动大盘数据复盘：在 TE 建三张标准表（大盘汇总/付费结构/付费内容构成）并挂看板。
  用户说「活动复盘」「活动大盘」「建复盘看板」「针对xx活动做数据复盘」、
  给出活动窗+参与场景+渠道区服、或 /activity-dapan-review 时使用。
  依赖 user-te-mcp-analysis 建表；区服可先 /activity-config-query。
---

# 活动大盘数据复盘

在 ThinkingEngine（TE）按固定模板创建 **三张复盘报表 + 看板**。

> **通用模板说明**：本技能来自某手游项目的活动复盘实践沉淀，已脱敏泛化。渠道名、`projectId`、`entityId`、报表/看板 ID 等均为占位示例，**首次接入需按你的项目替换**（见下方「接入前必改」）。

**执行层**：引导澄清 → Read `references/` → 生成 QP → TE MCP `create_report` × 3 → `create_dashboard` → 验证 → 回传链接。

## 接入前必改

| 占位 | 出现位置 | 替换为 |
|------|----------|--------|
| `projectId: 999999` | 各 `references/templates/*.json`、脚本默认值 | 你的 TE 项目 `projectId`（`list_projects` 查） |
| `entityId: 888888` | QP 模板中 `taIdMeasure.entityId` | 你项目「user」主实体的 entityId（`list_entities` 查，勿直接沿用示例值） |
| `channel_a` / `channel_b` / `channel_c` | 渠道 OR 筛选模板、脚本默认 `channels[]` | 你项目的用户属性 `platform` 取值（渠道包名/标识） |
| 区服 `area_id` 范围 | 同上 | 你项目各渠道的实际区服范围 |
| 示例活动名 / 示例场景关键词 | onboarding、templates | 实际活动名 + `scene_id@scene_id_cn1` 场景关键词 |

若你的埋点表名（`t_login`/`t_pay_flow`/`t_goods_flow`）、字段名（`login_way`/`pay_type_id`/`scene_id@scene_id_cn1`/`#vp@cost_yuan`）与示例不同，需按本项目埋点协议整体调整口径，而非只换筛选值。

## 渐进披露

| 需求 | 读取 |
|------|------|
| **口径清单（模板权威）** | [references/caliber-checklist.md](references/caliber-checklist.md) |
| 引导提问 / 用户指令模板 | [references/onboarding-questions.md](references/onboarding-questions.md) |
| MCP 建表步骤 | [references/mcp-workflow.md](references/mcp-workflow.md) |
| 踩坑与排障 | [references/lessons-and-troubleshooting.md](references/lessons-and-troubleshooting.md) |
| 付费内容构成结构 | [references/qp-template-content.md](references/qp-template-content.md) |
| QP JSON 模板 | [references/templates/](references/templates/) |

## 触发与别名

- `/activity-dapan-review`
- **活动复盘**、**活动大盘**、**活动数据复盘**、**建活动复盘看板**、**针对 xx 活动复盘**

## 交付物（固定三张表）

| # | 报表 | TE modelType | 路由 |
|---|------|--------------|------|
| 1 | 大盘汇总（10 项指标） | `event` | `/tga/event/` |
| 2 | 付费结构（人数/占比/金额） | `distribution` | `/tga/scatter/` |
| 3 | 付费内容构成（四列含占比） | `event` | `/tga/event/` |

+ **看板**挂载三张表 + 可选口径说明 note

模板结构与占位示例见 [caliber-checklist.md](references/caliber-checklist.md)。

## 与其他技能边界

| 技能 | 关系 |
|------|------|
| **activity-config-query** | 上游（可选）：查活动窗、开放区服；本技能消费其结果填 OR 筛选。若未一起打包，可省略此步，直接由用户提供渠道区服范围 |
| **th-bi-analytics-assistant** | 通用分析；本技能是「三张表建看板」专用 playbook |
| **te-report-playwright-export** | 下游（可选）：从已建报表导出 CSV |

## 引导式提问（未齐禁止建表）

必填：**活动名称、活动窗口、参与场景关键词、渠道+区服（全渠道 OR）**。

详见 [onboarding-questions.md](references/onboarding-questions.md)。缺项用 **AskQuestion**；禁止默认时间窗或静默单渠道。

## 主流程

```
1. 解析用户输入 → 对照 onboarding-questions 检查必填项
2. Read caliber-checklist.md + lessons-and-troubleshooting.md
3. 生成 session 参数（活动窗、场景、channels；均按「接入前必改」替换为本项目值）
4. 运行 scripts/build_activity_dapan_qp.js --config <session> --out <tmp>
   或手工改 references/templates/*.json
5. Read mcp-workflow.md → create_report × 3 → create_dashboard
6. query_report_data 抽检 + get_resource_url（每张报表 + 看板，强制）
7. 可选：create_or_update_dashboard_note 写口径说明
8. 回执（见下）
```

## QP 生成脚本

```bash
node archive/skills/skills/activity-dapan-review/scripts/build_activity_dapan_qp.js \
  --config session.json \
  --out workspace/tmp/activity-dapan-qp
```

`session.json` 字段见 [caliber-checklist.md](references/caliber-checklist.md)「可变参数」；至少需覆盖 `projectId`、`channels[]`、`start`/`end`、`participationScenes`。

## 执行红线

1. **禁止** `platform_id` 筛选；用 `platform` + `area_id` OR。
2. 参与口径用 **`scene_id@scene_id_cn1`**（或你项目对应字段），不用近似字段替代。
3. 活跃人数筛选须与你项目「有效登录」口径对齐（示例用 `login_way = 2`）。
4. 付费率 / 参与率 / 占比列：**`FORMAT_PERCENT`**。
5. 公式指标筛选写 **`customFilters`**，不写顶层 `filts`。
6. 未齐必填参数 → 禁止 `create_report`。
7. 默认 **不** `git commit`；写入范围以你所在仓库策略为准。
8. 每张 `create_report` / `create_dashboard` 后必须 **`get_resource_url`**。
9. `projectId`/`entityId`/渠道名等示例占位值**禁止直接用于生产**，必须先替换。

## 建表后回执

同一轮须输出：

1. 看板链接 + 三张报表链接（Markdown 可点击）
2. 活动窗、参与场景、渠道 OR 摘要
3. 新建 reportId / dashboardId
4. 抽检数值（大盘付费人数、结构合计、内容主场景一行）
5. 已知限制（分布分析筛选 UI、MCP 多行 fold 等）一句

## 首轮话术

> 活动大盘复盘就绪。请确认 **活动名称、活动窗口、参与场景关键词、三渠道区服范围**，以及你项目的 **TE projectId**。
> 首次使用本技能请先按 SKILL.md「接入前必改」替换占位值。齐套后我会建 **大盘汇总 + 付费结构 + 付费内容构成** 三张表并挂看板。
