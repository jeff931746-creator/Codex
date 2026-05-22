---
# === 身份 ===
mother_theme_id: THM-UNK-001
mother_theme_name: 未分类(临时占位)
category: UNK
status: hypothesis

# === SDT 心理需求(占位母题不归并)===
n_main: null
n_others: []
t_can_carry: []

# === 母题内容(占位)===
core_emotion: "未分类,任务 2 母题归并后所有作品应离开本占位"
core_conflict: "占位母题,无统一冲突结构"

theme_elements:
  environment: "无"
  cultural_paradigm: "无"
  narrative_core: "无"

# === 评分(占位)===
acquisition_score: 0
roi_score: 0
quadrant: 未知

# === 归属作品 ===
sample_count: 0
representative_works: []

# === 三位一体关联(占位)===
related_motifs: []
opposing_motifs: []
audience_ids: []
playstyle_ids: []

# === 元数据 ===
evidence_level: D
created_by: schema-init
created_at: 2026-05-15
last_updated: 2026-05-15
---

## 占位母题说明

本文件是历史题材库的**临时占位母题**。

### 用途

- 任务 1(单作品打标)跑批阶段,所有样本的 `mother_theme_id` 默认指向 `THM-UNK-001`
- 让 SCHEMA §5 第 6 项"母题引用合法性"质量门禁可以通过(否则首轮跑批所有样本都会失败)
- 任务 2(母题归并)完成后,所有样本应迁移到正式 THM-* 母题,本占位下应回到 `sample_count: 0`

### 规则

- **不要把作品永久挂在 THM-UNK-001 下**;任务 2 后还在 UNK 下的作品需要单独人工处理
- 本文件 `status: hypothesis`,永远不升级为 `stable`
- 本文件不参与 `母题归并` 的代表作筛选、不进入索引的"按母题"统计前列
- 本文件不会被废弃,长期保留作为新增作品(任务 4 新作品补录)的默认归属

### 任务 2 完成后的复检

任务 2 完成后,运行索引脚本检查:

```
若 THM-UNK-001 的 sample_count > 0
  → 列出所有仍归属 UNK 的样本
  → 走 04_失败复检.md 流程或人工 review
  → 全部归到正式母题后,sample_count 应回到 0
```
