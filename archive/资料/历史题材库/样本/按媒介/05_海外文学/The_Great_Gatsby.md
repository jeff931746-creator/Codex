---
# === 身份 ===
work_id: WORK-LIT-00403
work_name: The Great Gatsby
work_name_alt: []
media_type: LIT
year_first: 1925
year_range: [1925, 1925]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 1920年代美国爵士时代
cultural_paradigm: 上流社会+美国梦幻灭
narrative_core: 爱情与阶级幻灭

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Rel
n_others: [N-Comp]
rel_object: real
t_can_carry: [T4, T5]
core_emotion_note: ""
core_conflict: 盖茨比试图通过财富赢回旧爱，却无法跨越阶级鸿沟

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 都市
theme_secondary: [恋爱, 阶级压迫, 悲剧]
visual_tags: [都市夜景, 复古豪车, 豪宅, 派对狂欢, 绿色灯塔]


# === 评分(v0 已有)===
acquisition_score: 3

# === 素材与玩法 ===
material_hooks: [东卵西卵豪宅, 长岛派对狂欢, 绿色灯塔, 纽约天际线, 复古豪车]
existing_games: []
recommended_playstyles: []
risk_notes: [受众窄, 付费浅]

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
