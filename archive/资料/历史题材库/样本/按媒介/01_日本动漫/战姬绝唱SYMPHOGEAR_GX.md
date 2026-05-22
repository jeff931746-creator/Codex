---
# === 身份 ===
work_id: WORK-ANI-00162
work_name: 战姬绝唱SYMPHOGEAR GX
work_name_alt: []
media_type: ANI
year_first: 2015
year_range: [2015, 2015]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 近未来都市+音乐战斗舞台
cultural_paradigm: 歌姬+机甲+声波战斗体系
narrative_core: 守护世界+音乐力量觉醒

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Comp
n_others: [N-Rel]
rel_object: mixed
t_can_carry: [T2, T4]
core_emotion_note: ""
core_conflict: 歌姬们用歌声和机甲对抗噪音怪物，守护世界与同伴

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 科幻
theme_secondary: [机甲, 末日, 都市]
visual_tags: [机甲变身, 歌声光波特效, 舞台崩塌, 都市夜景]


# === 评分(v0 已有)===
acquisition_score: 3

# === 素材与玩法 ===
material_hooks: [机甲变身战斗, 歌声光波特效, 舞台崩塌场景, 角色受伤牺牲]
existing_games: [战姬绝唱手游]
recommended_playstyles: []
risk_notes: [版权成本高, 受众中等]

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
