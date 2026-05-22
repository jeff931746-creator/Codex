---
# === 身份 ===
work_id: WORK-ANI-00102
work_name: Fate/Apocrypha
work_name_alt: []
media_type: ANI
year_first: 2017
year_range: [2017, 2017]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 架空现代圣杯战争
cultural_paradigm: 英灵召唤+宝具对决
narrative_core: 阵营对抗与背叛

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Rel
n_others: [N-Comp]
rel_object: mixed
t_can_carry: [T4, T2]
core_emotion_note: ""
core_conflict: 红黑两大阵营为争夺圣杯展开对决，内部背叛与信任交织

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 奇幻
theme_secondary: [神话, 战争, 冒险]
visual_tags: [古堡, 魔法阵, 武器对决, 奇幻瑰丽]


# === 评分(v0 已有)===
acquisition_score: 4

# === 素材与玩法 ===
material_hooks: [英灵宝具对轰, 红黑阵营对峙, 贞德圣旗飘扬, 齐格飞龙化]
existing_games: [Fate/Grand Order, Fate/EXTELLA]
recommended_playstyles: []
risk_notes: [版权成本极高, 红海]

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
