---
# === 身份 ===
work_id: WORK-LIT-00314
work_name: The Devil Wears Prada
work_name_alt: []
media_type: LIT
year_first: 2003
year_range: [2003, 2003]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 2000年代纽约时尚界
cultural_paradigm: 职场权力+时尚行业
narrative_core: 助理对抗时尚女魔头老板

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Rel
n_others: [N-Comp]
rel_object: real
t_can_carry: [T4, T2]
core_emotion_note: ""
core_conflict: 助理在时尚女魔头的高压下挣扎求生并争夺职场地位

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 职场
theme_secondary: [都市, 成长, 阶级压迫, 时尚]
visual_tags: [都市繁华, 摩天楼, 高级时装特写, 时尚秀场]


# === 评分(v0 已有)===
acquisition_score: 4

# === 素材与玩法 ===
material_hooks: [米兰达的冷酷眼神, 时尚秀场华丽场景, 助理的狼狈奔跑, 高级时装特写]
existing_games: []
recommended_playstyles: []
risk_notes: [版权成本, 玩法深度有限]

# === 元数据 ===
source: deepseek-v4-flash + v0-migrate + tags
source_run_id: 2026-05-18-tags-enrich
evidence_level: B
review_status: auto
last_updated: 2026-05-18
---

## 迁移备注

本样本由 v0 markdown 表格迁移而来,LLM 阶段尚未补 SDT 三需求 / T 任务态 / core_conflict / material_hooks 重判。
迁移完成后 evidence_level = C,LLM 增量打标后升至 B。
