# 踩坑与排障

## 活动窗被静默默认化（高危 · 会产错误窗口看板）

**现象**：三张表建成、无报错，但报表时间窗是脚本默认窗口，而非本次活动窗。曾有真实案例因此建出错误窗口的看板，需重建。

**根因**：`build_activity_dapan_qp.js` 内部字段是 **`start` / `end`**；`session.json` 若写成 **`startDate` / `endDate`**，`Object.assign(opts, config)` 只会新增无用键，`opts.start/end` 仍是默认值 → 静默套用默认窗口，无任何报错。

**处理 / 预防**：

| 措施 | 说明 |
|------|------|
| session.json 用 `start` / `end` | 与脚本内部字段一致（脚本已兼容 `startDate/endDate/activityStart/activityEnd` 别名并归一化） |
| 建表前必看脚本回执 `window` | 脚本已在输出打印 `{window:{start,end}, participationScenes}`，与活动窗逐字核对后再 `create_report` |
| 或校验 QP 时间戳 | `eventView.startTime/endTime` 换算回本地日期须等于活动窗；换算：`ms + 8*3600*1000`（按你项目所在时区调整） |
| 误建后 | 无 `update_report`，须新建正确版本；旧表在 TE 手动删除，回执里标注「以新 ID 为准」 |

## 渠道筛选

| 问题 | 处理 |
|------|------|
| 用了 `platform_id` | **禁止**；改用 `platform` 字符串 |
| 三渠道拆三张表 | 用户要全渠道 OR 一张表，见 caliber-checklist |
| OR 筛选 UI 不显示（分布分析） | 后端已生效；分布模型 UI 可能不渲染 `eventView.filts`；可 TE 手动保存或接受不可见 |

## 参与口径

| 问题 | 处理 |
|------|------|
| 用宽泛的场景类型字段筛选，命中数为 0 | 改用更精确的场景维度属性（示例项目中为 `scene_id@scene_id_cn1` 含关键词） |
| 参与人数为 0 | TE 事件明细抽一条参与事件确认场景枚举文案是否与筛选关键词一致 |

## 多事件同表

| 问题 | 处理 |
|------|------|
| 大盘多指标列错位 | `rowSpanType: fold` + `eventUuid` + `uiCommonConfig.stageInfo`；公式用 `customFilters` |
| MCP 返回多行 | TE UI fold 成一行，属正常 |
| 付费率显示 0.07 而非 7% | 公式指标 `format: FORMAT_PERCENT` |

## 付费内容构成

| 问题 | 处理 |
|------|------|
| 只有人数/金额无占比 | 补两列公式 + `eventSplit`；见 qp-template-content.md |
| `query_report_data` 空行 | eventSplit 报表常见；以 TE UI 为准 |
| 各场景人数占比之和 >100% | 同用户可跨场景付费，属正常 |

## 分布分析付费结构

| 问题 | 处理 |
|------|------|
| 只有人数/占比无金额 | 加第二条付费事件 `intervalType: def` |
| 档位不对 | 检查 `quotaIntervalArr` 与 `user_defined` |

## MCP 限制

- 无 `update_report`：改口径须 **新建报表版本**
- `update_dashboard` 仅追加报表，不能删旧卡
- `create_report` 后必须 `get_resource_url`

## 与配置中心 / 活动排期系统对齐

活动窗 / 区服范围应以你项目的活动配置系统为准（如有相关技能）。TE 筛选与配表不一致时并列差异请用户确认。

## 参考报表结构（占位，非真实 ID）

| 用途 | 说明 |
|------|------|
| 大盘汇总终态 | 10 列 fold 结构 |
| 付费结构终态 | 分布分析双事件（人数档位 + 金额档位） |
| 付费内容构成终态 | 含占比 + eventSplit |
| 公式 customFilters 参考 | 见 qp-dapan.json 中付费率/ARPU/ARPPU 写法 |
| 多事件 fold 参考 | 见 qp-dapan.json 整体结构 |
| 分布双事件（金额行）参考 | 见 qp-tier.json |
