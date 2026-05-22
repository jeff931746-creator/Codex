---
# === 身份 ===
work_id: WORK-TVW-00038
work_name: X战警：背水一战
work_name_alt: []
media_type: TVW
year_first: 2006
year_range: [2006, 2006]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 现代都市+变种人世界
cultural_paradigm: 变种人超能力体系
narrative_core: 终极抉择+阵营对抗

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Rel
n_others: [N-Comp]
rel_object: real
t_can_carry: [T4, T2]
core_emotion_note: ""
core_conflict: 变种人阵营分裂，凤凰女失控威胁世界，X战警面临终极抉择

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 科幻
theme_secondary: [灾难, 战争]
visual_tags: [超能力对决, 变种人, 凤凰女黑化, 大规模混战, 现代都市]


# === 评分(v0 已有)===
acquisition_score: 4

# === 素材与玩法 ===
material_hooks: [变种人超能力对决, 凤凰女黑化爆发, X教授与万磁王对峙, 大规模阵营混战, 变种人命运转折]
existing_games: [《X战警》系列游戏]
recommended_playstyles: []
risk_notes: [版权成本高, 红海竞争]

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
