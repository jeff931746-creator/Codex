---
# === 身份 ===
work_id: WORK-MVK-00115
work_name: R2B：返回基地
work_name_alt: []
media_type: MVK
year_first: 2012
year_range: [2012, 2012]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 现代韩国空军基地
cultural_paradigm: 空战+军事救援
narrative_core: 空战救援+兄弟情

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Rel
n_others: [N-Comp]
rel_object: real
t_can_carry: [T4, T2]
core_emotion_note: ""
core_conflict: 空军飞行员在救援任务中对抗敌军，同时维系战友间的生死情谊

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 战争
theme_secondary: [军事行动, 兄弟情]
visual_tags: [战机编队出击, 空中缠斗爆炸, 救援直升机悬停, 基地指挥室紧张调度]


# === 评分(v0 已有)===
acquisition_score: 2

# === 素材与玩法 ===
material_hooks: [战机编队出击, 空中缠斗爆炸, 救援直升机悬停, 基地指挥室紧张调度]
existing_games: []
recommended_playstyles: []
risk_notes: [受众窄, 版权成本中]

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
