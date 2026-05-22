---
# === 身份 ===
work_id: WORK-ANI-00045
work_name: 刀剑神域 Alicization
work_name_alt: []
media_type: ANI
year_first: 2018
year_range: [2018, 2019]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 虚拟世界Underworld
cultural_paradigm: VRMMO+剑术系统
narrative_core: 生死战斗+虚拟现实

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Comp
n_others: [N-Rel]
rel_object: mixed
t_can_carry: [T2, T4]
core_emotion_note: ""
core_conflict: 桐人在虚拟世界Underworld中为生存而战，同时对抗系统与外部势力

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 冒险
theme_secondary: [虚拟现实, 未来战争, 求生, 科幻]
visual_tags: [虚拟世界, 光剑对决, 星舰内部, 机甲, 全息投影]


# === 评分(v0 已有)===
acquisition_score: 4

# === 素材与玩法 ===
material_hooks: [光剑对决, 虚拟世界崩塌, 亚丝娜救援, 桐人双刀流]
existing_games: [刀剑神域：彼岸游境, 刀剑神域：记忆重组]
recommended_playstyles: []
risk_notes: [版权成本极高, 竞品红海]

# === 元数据 ===
source: deepseek-v4-flash + v0-migrate + tags
source_run_id: 2026-05-18-tags-enrich
evidence_level: B
review_status: auto
last_updated: 2026-05-18
# v0_duplicate_count: 3
---

## 迁移备注

本样本由 v0 markdown 表格迁移而来,LLM 阶段尚未补 SDT 三需求 / T 任务态 / core_conflict / material_hooks 重判。
迁移完成后 evidence_level = C,LLM 增量打标后升至 B。
