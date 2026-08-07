# 付费内容构成 QP 结构说明

MCP 初建可用 `groupBy`；**推荐终态**为 TE UI 保存后的 **eventSplit** 模式。

## 四列指标

```
付费人数          type:0  t_pay_flow A101  真实充值筛选
付费人数占比      type:1  t_pay_flow.A101/t_pay_flow.A101  FORMAT_PERCENT
付费金额          type:0  t_pay_flow A103  金额虚拟属性  真实充值筛选
付费金额占比      type:1  t_pay_flow.金额.A103/t_pay_flow.金额.A103  FORMAT_PERCENT
```

## eventSplit（推荐）

```json
"eventView": {
  "rowSpanType": "unfold",
  "eventSplit": {
    "eventList": [{ "eventName": "t_pay_flow", "eventType": "event" }],
    "groupByPropList": [{
      "columnName": "scene_id@scene_id_cn2",
      "columnDesc": "scene_type_scene_id",
      "selectType": "string",
      "tableType": "0",
      "subTableType": "vprop_dict"
    }]
  }
}
```

`columnName` 为占位示例，需替换为你项目场景二级维度属性的字段名。每个 `events[]` 指标须设置 `"eventSplitIndexes": [0]`。

## 占比公式 customFilters

TE UI 保存后常为：

```json
"customFilters": [
  { "index": 0, "relation": "1", "filts": [] },
  { "index": 1, "relation": null, "filts": [] }
]
```

## 全局筛选

与大盘表相同：全渠道 OR → [templates/or-channel-filts.json](templates/or-channel-filts.json)

## 生成

```bash
node archive/skills/skills/activity-dapan-review/scripts/build_activity_dapan_qp.js \
  --config session.json \
  --out workspace/tmp/activity-dapan-qp
```

输出 `qp-content.json`，作为 `create_report` 的 `analysisQuery` 字符串入参。

## MCP 初版（仅人数+金额，无占比）

`groupBy: [场景二级维度属性]` 模式：两列基础指标，无占比列。用户通常在 TE 补占比列后保存为终态。
