# 活动大盘复盘 · 口径清单（通用模板）

活动复盘三张表的标准口径模板，脱敏自真实项目案例。**渠道名、`projectId`、`entityId`、报表/看板 ID 均为占位示例**，新项目接入时按本清单替换**项目参数、活动窗、场景关键词、渠道区服**即可。

## 示例结构（占位值，非真实数据）

| 资源 | 说明 |
|------|------|
| 看板 | 示例看板（挂三张报表） |
| 大盘汇总 | 示例报表 A |
| 付费结构 | 示例报表 B |
| 付费内容构成 | 示例报表 C |

---

## 全局约定（三张表共用）

### 渠道 + 区服（全渠道 OR，不拆表）

**禁止**使用 `platform_id` 筛选。用用户属性 **`platform`** + **`area_id`**：

| 渠道（占位示例） | `platform`（占位） | `area_id` 范围（占位） |
|------|------------|----------------|
| 渠道 A | `channel_a` | 按实际填写 |
| 渠道 B | `channel_b` | 按实际填写 |
| 渠道 C | `channel_c` | 按实际填写 |

> 接入时：把上表换成你项目真实的 `platform` 取值和各渠道区服范围；渠道数量不限于 3 个。

TE 全局筛选结构（`eventView.filts`）：

```
(platform=channel_a AND area_id∈[minA,maxA])
OR (platform=channel_b AND area_id∈[minB,maxB])
OR (platform=channel_c AND area_id∈[minC,maxC])
```

- 每组内 `relation: "1"`（AND），组间顶层 `relation: "0"`（OR）
- 每组 `filterType: "COMPOUND"`
- 叶子节点须带 `columnDesc`（`平台(注册时)`、`区服id`）以便事件分析 UI 展示

模板 JSON：[templates/or-channel-filts.json](templates/or-channel-filts.json)

### 用户去重

统一 TE **用户**（`#user_id` / 触发用户数），不用 `customer_id`（若你项目字段名不同，按你的用户主键调整）。

### 金额与付费类型

| 用途 | 条件 |
|------|------|
| 金额字段 | 虚拟属性 `#vp@cost_yuan`（或你项目对应的付费金额虚拟属性） |
| 真实充值 | `t_pay_flow` · `pay_type_id = 2`（示例值，需核对你项目枚举） |
| 代金券充值 | `t_pay_flow` · `pay_type_id = 7`（示例值，需核对你项目枚举） |

### 活跃与参与

| 指标 | 事件 | 筛选 |
|------|------|------|
| 活动期间活跃人数 | `t_login` | 示例：**`login_way = 2`**（需核对你项目「有效登录」枚举） |
| 活动参与人数 | `t_goods_flow` | **`scene_id@scene_id_cn1` 含**活动场景关键词（示例：如「示例场景」） |

> 参与口径建议走场景维度属性（示例中为 `scene_id@scene_id_cn1`），而非笼统的场景类型字段；具体字段名以你项目埋点协议为准，接入前用 TE 事件明细验证枚举文案。

### 时间窗

- 粒度：**合计**（`timeParticleSize: T5`）
- 起止：活动窗含首尾（与配表活动排期对齐后写入 `startTime` / `endTime` 毫秒时间戳）

---

## 表 1：大盘汇总（事件分析）

**模型**：`modelType: event` · URL `/tga/event/`

### 列序（10 项，固定）

| # | 列名 | 类型 | 说明 |
|---|------|------|------|
| 1 | 活动期间活跃人数 | 基础 | `t_login` A101 · 活跃筛选 |
| 2 | 活动期间付费人数 | 基础 | `t_pay_flow` A101 · 真实充值筛选 |
| 3 | 活动期间总收入 | 基础 | `t_pay_flow` A103 · 金额虚拟属性 · 真实充值筛选 |
| 4 | 活动期间付费率 | 公式 | `t_pay_flow.A101 / t_login.A101` · **`FORMAT_PERCENT`** |
| 5 | 活动期间 ARPU | 公式 | `t_pay_flow.金额.A103 / t_login.A101` |
| 6 | 活动期间 ARPPU | 公式 | `t_pay_flow.金额.A103 / t_pay_flow.A101` |
| 7 | 活动参与人数 | 基础 | `t_goods_flow` A101 · 场景筛选 |
| 8 | 活动参与率 | 公式 | `t_goods_flow.A101 / t_login.A101` · **`FORMAT_PERCENT`** |
| 9 | 代金券总付费金额（元） | 基础 | `t_pay_flow` A103 · 代金券充值筛选 |
| 10 | 代金券总付费人数 | 基础 | `t_pay_flow` A101 · 代金券充值筛选 |

### 公式指标写法

- `type: 1` · `customEvent` 写公式字符串
- 事件级筛选放在 **`customFilters`**（不要写在公式顶层 `filts`）
- 付费率 / 参与率分母侧 `t_login` 须带活跃筛选
- 参与率分子侧 `t_goods_flow` 须带场景筛选
- `rowSpanType: "fold"` + 每指标 `eventUuid` + `uiCommonConfig.stageInfo`

QP 模板：[templates/qp-dapan.json](templates/qp-dapan.json)

---

## 表 2：付费结构（分布分析）

**模型**：`modelType: distribution` · URL `/tga/scatter/`

| 行 | 事件配置 |
|----|----------|
| 用户数 / 占比 | `t_pay_flow` · 金额虚拟属性 A103 · `intervalType: user_defined` · `quotaIntervalArr` 自定义档位 |
| 各档金额 | 同上第二条事件 · `intervalType: def` |
| 事件筛选 | 真实充值筛选 |
| 全局筛选 | 全渠道 OR（同上） |

QP 模板：[templates/qp-tier.json](templates/qp-tier.json)

**已知限制**：MCP 写入的全局 OR 筛选在分布分析 **UI 筛选栏可能不显示**，但查询已生效。需在 TE 手动保存一次或接受「筛选不可见」。

---

## 表 3：付费内容构成（事件分析 + 场景拆分）

**模型**：`modelType: event` · URL `/tga/event/`

| 列 | 说明 |
|----|------|
| 付费人数 | `t_pay_flow` A101 · 真实充值筛选 |
| 付费人数占比 | 公式 `t_pay_flow.A101 / t_pay_flow.A101` · **`FORMAT_PERCENT`** |
| 付费金额 | `t_pay_flow` A103 · 金额虚拟属性 · 真实充值筛选 |
| 付费金额占比 | 公式 `t_pay_flow.金额.A103 / t_pay_flow.金额.A103` · **`FORMAT_PERCENT`** |

### 拆分维度

- 推荐 **`eventSplit`** + 场景二级维度（示例 `scene_id@scene_id_cn2`，需按你项目埋点调整）
- 备选：`groupBy: [场景二级维度]`（MCP 初版，无占比列）

占比公式须挂 `eventSplitIndexes: [0]`，与拆分维度对齐。

结构说明：[qp-template-content.md](qp-template-content.md)
生成脚本：`scripts/build_activity_dapan_qp.js` → `qp-content.json`

---

## 可变参数（每次活动 / 每个项目替换）

| 参数 | 示例（占位） |
|------|------|
| `projectId` | `999999`（**必须**替换为你的 TE `projectId`） |
| `activityName` | 示例活动 |
| `startDate` / `endDate` | 2026-06-27 ~ 2026-07-03 |
| `participationScenes` | `["示例场景"]` → 场景关键词字段含 |
| `channels[]` | platform + area 范围（渠道数量与命名按你项目实际情况） |
| `tierIntervals` | 默认 `[1,7,101,1001,10001,50001]`，按你项目付费分层习惯调整 |
| `dashboardName` | `{活动名}复盘 {YYYYMMDD}-{MMDD}` |

---

## 与配表 / TE 的边界

| 来源 | 用途 |
|------|------|
| 活动配置查询（如有，各项目自建） | 活动窗、开放区服范围（配置中心事实） |
| 本技能 | TE 三张复盘表 + 看板 |
| 团队知识库 | 指标长期口径（用户要求时再沉淀） |

如你的配置中心有独立的渠道/平台 ID（数字编码），需先建立与 TE `platform` 字符串的映射关系，再套用本模板。
