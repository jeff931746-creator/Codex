---
# === 身份 ===
work_id: WORK-ANI-00058
work_name: 鬼灭之刃 无限列车篇 TV版
work_name_alt: []
media_type: ANI
year_first: 2021
year_range: [2021, 2021]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 日本大正时代
cultural_paradigm: 剑士武道+鬼怪文化
narrative_core: 热血战斗+守护

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Comp
n_others: [N-Rel]
rel_object: virtual
t_can_carry: [T2, T3]
core_emotion_note: ""
core_conflict: 鬼杀队剑士对抗上弦之鬼，守护列车上的无辜乘客

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 冒险
theme_secondary: [奇幻, 恐怖, 历史, 友情]
visual_tags: [日轮刀斩鬼特效, 炎之呼吸华丽连击, 猗窝座血鬼术压迫, 炭治郎火之神乐, 列车鬼怪吞噬场景]


# === 评分(v0 已有)===
acquisition_score: 5

# === 素材与玩法 ===
material_hooks: [日轮刀斩鬼特效, 炎之呼吸华丽连击, 猗窝座血鬼术压迫, 炭治郎火之神乐, 列车鬼怪吞噬场景]
existing_games: [鬼灭之刃 火之神血风谭]
recommended_playstyles: []
risk_notes: [红海, 版权成本极高]

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
