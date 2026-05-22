---
# === 身份 ===
work_id: WORK-ANI-00015
work_name: "Fate/stay night [Unlimited Blade Works]"
work_name_alt: []
media_type: ANI
year_first: 2014
year_range: [2014, 2015]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 现代日本都市/圣杯战争
cultural_paradigm: 英灵召唤+魔术体系
narrative_core: 圣杯战争+信念对决

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Comp
n_others: [N-Rel]
rel_object: mixed
t_can_carry: [T2, T5]
core_emotion_note: ""
core_conflict: 魔术师与英灵争夺圣杯，信念碰撞与自我超越

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 奇幻
theme_secondary: [神话, 都市, 冒险, 战争]
visual_tags: [魔法阵, 武器对决, 古堡, 都市夜景, 英灵宝具解放]


# === 评分(v0 已有)===
acquisition_score: 4

# === 素材与玩法 ===
material_hooks: [英灵宝具解放, Saber誓约剑, 无限剑制展开, 凛的魔术礼装, 红A双刀对决]
existing_games: [《Fate/Grand Order》等]
recommended_playstyles: []
risk_notes: [版权成本极高, 红海]

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
