# 母题归并目录

> 用途:把历史题材库的样本聚合到题材母题,反向支撑 [02-题材母题标准](../../../../reference/部门标准/立项/三位一体框架/current/02-题材母题标准.md)
> 配套:[SCHEMA.md](../SCHEMA.md) / [录入工作流.md](../录入工作流.md)

---

## 目录定位

本目录是**历史题材库 → 三位一体框架题材母题库**的桥梁。

- 主数据(`样本/按媒介/`)按媒介存储单部作品
- 母题归并目录把作品按题材母题(THM-*)聚合,每个母题一份文件
- 母题文件不重复样本数据,只通过 work_id 引用

---

## 生成方式

**本目录的内容由 DeepSeek 跑批任务 2 + 索引脚本自动生成,不手工维护**。

生成流程:

1. DeepSeek 任务 2(`提示词/02_母题归并.md`)自下而上聚类,产出 motif_candidates
2. 人工 review 后分配 THM-{category}-{编号},写入本目录
3. 索引脚本扫描 `样本/按媒介/` 下所有样本,聚合归属作品 + 代表作 + 统计数据

---

## 单个母题文件 SCHEMA

文件名:`THM-{category}-{编号}_{母题中文名}.md`

例:`THM-SUR-001_末世求生.md`

### YAML Frontmatter

```yaml
---
# === 身份 ===
mother_theme_id: THM-SUR-001
mother_theme_name: 末世求生
category: SUR                          # SUR/POW/EXP/HEA/GRO/BRE
status: stable | hypothesis | deprecated

# === SDT 心理需求(从归属作品聚合)===
n_main: N-Comp                         # 多数归属作品的 n_main
n_others: []                           # 母题层副需求(选填)
t_can_carry: [T2, T1]                  # 母题承接的任务态

# === 母题内容 ===
core_emotion: "求生压力 + 紧张感"
core_conflict: "在崩溃世界中保住自己和重要的人"

theme_elements:
  environment: "母题适用的世界观范围(末世废土/核冬天/海底崩溃/奇幻末世)"
  cultural_paradigm: "资源管理 + 生存系统"
  narrative_core: "在崩溃世界中保住自己和重要的人"

# === 评分(母题级聚合,从归属作品中位数取)===
acquisition_score: 5
roi_score: 4
quadrant: 高获量×高ROI

# === 归属作品(索引脚本生成)===
sample_count: 137
representative_works:                   # 5-10 部,由 DeepSeek 任务 2 调用 B 筛选
  - work_id: WORK-ANI-00001
    work_name: 进击的巨人
    rank_score: 9.0
    特殊表达: "巨人压迫 + 立体机动战斗 + 反转世界观"
  - work_id: WORK-TVW-00042
    work_name: 行尸走肉
    rank_score: 8.5
    特殊表达: "丧尸末日 + 人性博弈 + 长篇剧集"
  - ...

# === 三位一体关联 ===
related_motifs: [THM-GRO-002, THM-BRE-001]    # 相似/可融合母题
opposing_motifs: [THM-HEA-001]                # 对立/难融合母题
audience_ids: [AUD-C04, AUD-C01]               # 关联人群簇
playstyle_ids: [PLY-SUR-001, PLY-ACT-002]     # 关联玩法承接

# === 元数据 ===
evidence_level: A
created_by: deepseek-v4-flash + manual-review
created_at: 2026-05-15
last_updated: 2026-05-15
---
```

### 正文区结构

```markdown
## 母题说明

[人类可读的母题特征描述、典型情绪钩子、市场表现、立项参考价值]

## 与相邻母题的边界

- vs THM-GRO-002 弱者逆袭:边界说明
- vs THM-BRE-001 权力博弈:边界说明
- vs THM-HEA-001 田园经营:对立说明

## 归属作品全名单

[由索引脚本自动从样本目录生成,按 acquisition_score + roi_score 综合分排序]

- WORK-ANI-00001 进击的巨人 (9.0)
- WORK-TVW-00042 行尸走肉 (8.5)
- WORK-MVW-00088 我是传奇 (8.0)
- ... (137 条)

## 立项参考

[人工补充,说明该母题在游戏立项中的典型应用、成功/失败案例]
```

---

## 母题状态(status)

| 取值 | 含义 |
|---|---|
| stable | 已经市场验证,归属作品 ≥ 50 部,有清晰边界 |
| hypothesis | 聚类形成但归属作品 < 50,边界待校验 |
| deprecated | 早期定义但后续合并/拆分,保留记录 |

---

## 母题 ID 编号规则

`THM-{category}-{3 位编号}`

- category 从 02-题材母题标准的 6 大类取:SUR / POW / EXP / HEA / GRO / BRE
- 编号在 category 内独立递增(THM-SUR-001 / THM-SUR-002 ...)
- **THM-UNK-001**:未分类母题,作为任务 1 跑批的临时占位,任务 2 后所有作品应离开 UNK
- **编号永不修改**:母题废弃后保留编号,status 改 deprecated

---

## 代表作筛选规则(同 IP 跨媒介专项)

跨媒介同 IP(如《沙丘》小说 + 电影 + 剧集)在代表作筛选时遵循:

| 情形 | 规则 |
|---|---|
| 同 IP 各媒介版本的 N/T/三要素**基本一致** | 只选 1 个进 representative_works(选 `acquisition_score + roi_score` 综合 rank_score 最高的版本);其他版本进归属作品全名单但不占代表作位 |
| 同 IP 各媒介版本的 N/T/三要素**有显著不同**(如小说 T5 vs 电影 T2) | 允许各占 1 个代表作位,但 `特殊表达` 字段必须明确说明媒介差异,且 motif_confidence 各自独立 |
| 同 IP 但被归到**不同母题**(罕见,如小说哲学向 → THM-EXP-XXX,电影动作向 → THM-POW-YYY) | 各母题各自独立挑代表作,**不需互相协调**(但跑批后必须用提示词 03 做"同 IP 多媒介"专项校验) |

判定流程:
1. 先按 `acquisition_score + roi_score` 综合分排序候选代表作
2. 同 IP 多版本时,先按上表规则去重(默认只留 1 个,有显著差异时各保留)
3. 再按"跨媒介覆盖 + 跨年代覆盖 + 母题特征清晰"补足 5-10 部
4. 每个代表作的 `特殊表达` 字段必须能体现"为什么选它而不是同 IP 其他版本"

---

## 与上游 02-题材母题标准的关系

```
本目录(下游)                          02-题材母题标准(上游)
─────────────                          ──────────────────
具体的 137 部作品归属    ─────引用───→  母题字段定义、归并规则
代表作 5-10 部清单       ─────回填───→  theme_examples / representative_games
母题统计数据             ─────支撑───→  evidence_level 升级判据
```

- 02-题材母题标准定义母题字段
- 本目录提供具体样本支撑(historical 题材库 = 样本池)
- 02 标准里的 `theme_examples` / `representative_games` 字段,通过本目录的代表作清单回填

---

## 引用规则

**禁止反向修改**:本目录不创建新的 N / T 枚举值,如发现样本需要超出现有枚举的需求,反向推动 03-玩法承接标准/06-基础维度定义补充,不在本目录自造。

---

## 占位文件说明

- `THM-UNK-001_未分类.md`(临时):任务 1 跑批阶段所有作品都挂在此,任务 2 后逐步迁移走
- 任务 2 后,本目录应有 15-25 个正式母题文件

---

## 索引刷新

`样本/索引/按母题.md` 由脚本扫描本目录 + 样本目录生成,内容为:

```markdown
| 母题 | 归属作品数 | 代表作 Top 3 |
|---|---|---|
| THM-SUR-001 末世求生 | 137 | 进击的巨人 / 行尸走肉 / 我是传奇 |
| THM-POW-001 无双战斗 | 89 | ... |
| ... |
```

任务 2 后每次新增/修改母题文件,索引同步刷新。
