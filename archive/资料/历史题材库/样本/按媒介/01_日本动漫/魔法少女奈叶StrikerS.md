---
# === 身份 ===
work_id: WORK-ANI-00239
work_name: 魔法少女奈叶StrikerS
work_name_alt: []
media_type: ANI
year_first: 2006
year_range: [2006, 2009]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 近未来科幻都市
cultural_paradigm: 魔法科技+军事组织
narrative_core: 团队作战与成长守护

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Rel
n_others: [N-Comp]
rel_object: mixed
t_can_carry: [T4, T2]
core_emotion_note: ""
core_conflict: 时空管理局特殊部队对抗非法魔法组织，守护和平与同伴

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 奇幻
theme_secondary: [魔法, 科幻, 校园, 友情]
visual_tags: [魔法阵, 空中战, 科技魔法装备, 都市夜景]


# === 评分(v0 已有)===
acquisition_score: 3

# === 素材与玩法 ===
material_hooks: [魔法少女变身, 空中魔法战, 团队合体技, 科技魔法装备]
existing_games: [魔法少女奈叶 王牌空战, 魔法少女奈叶 命运齿轮]
recommended_playstyles: []
risk_notes: [版权成本中, 受众偏核心]

# === 元数据 ===
source: deepseek-v4-flash + v0-migrate + tags
source_run_id: 2026-05-18-tags-enrich
evidence_level: B
review_status: auto
last_updated: 2026-05-18
# v0_duplicate_count: 2
---

## 迁移备注

本样本由 v0 markdown 表格迁移而来,LLM 阶段尚未补 SDT 三需求 / T 任务态 / core_conflict / material_hooks 重判。
迁移完成后 evidence_level = C,LLM 增量打标后升至 B。
