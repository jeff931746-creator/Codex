# MCP 建表工作流

执行前 Read：`user-te-mcp-analysis` 工具 schema（`create_report`、`create_dashboard`、`query_report_data`、`get_resource_url`）。
看板说明可选：`user-te-mcp-analysis-extend` · `create_or_update_dashboard_note`。

## 流程

```
1. 引导澄清 → Read caliber-checklist.md + onboarding-questions.md
2. 生成 QP
   a. 优先：node scripts/build_activity_dapan_qp.js --config session.json --out <tmp>
   b. 或：复制 references/templates/*.json 并替换活动窗/场景/渠道/projectId/entityId
3. query_adhoc 预检（可选）：三张 QP 各跑一次，确认无报错
4. create_report × 3
   - 大盘汇总：modelType=event
   - 付费结构：modelType=distribution
   - 付费内容构成：modelType=event
5. create_dashboard（或 create_report.dashboardIds 挂已有看板）
6. update_dashboard 追加其余报表（MCP 仅 append，不能删旧报表）
7. create_or_update_dashboard_note：口径摘要 + 报表 ID 链接
8. query_report_data 验证 + get_resource_url × 4
9. 回执（见 SKILL.md）
```

## create_report 参数示例（占位值）

```json
{
  "projectId": 999999,
  "reportName": "示例活动复盘-大盘汇总",
  "modelType": "event",
  "description": "活动窗… 全渠道OR…",
  "dashboardIds": [111111],
  "analysisQuery": "<stringified JSON from qp-dapan.json>"
}
```

`analysisQuery` 必须是 **字符串**（JSON.stringify 整个 QP 对象）。`projectId`、`dashboardIds` 为占位示例，接入时替换为你项目真实值。

## 报表命名约定

| 表 | 建议名称 |
|----|----------|
| 大盘 | `{活动名}复盘-大盘汇总` |
| 结构 | `{活动名}复盘-付费结构-全渠道` |
| 内容 | `{活动名}复盘-付费内容构成-全渠道` |

## 看板

```json
{
  "projectId": 999999,
  "dashboardName": "示例活动复盘 20260627-0703",
  "initialReportId": 111112,
  "noteTitle": "口径说明",
  "noteContent": "活动窗… 推荐报表 ID…"
}
```

其余两张表通过 `create_report.dashboardIds` 或 `update_dashboard` 追加。

## 验证要点

| 表 | 检查项 |
|----|--------|
| 大盘 | 10 列；付费率/参与率为 %；活跃筛选生效 |
| 结构 | 3 行（用户数/占比/金额）；付费用户合计与大盘付费人数一致 |
| 内容 | 4 列含占比；场景拆分有主活动场景行 |

MCP `query_report_data` 对多事件 fold / eventSplit 可能返回多行或空行，**以 TE UI 为准**。

## 完成后

每张报表、看板均须 `get_resource_url`，链接直接输出给用户（非代码块）。
