---
# === 身份 ===
work_id: WORK-TVW-00380
work_name: "CSI: 犯罪现场调查"
work_name_alt: []
media_type: TVW
year_first: 2000
year_range: [2000, 2002]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 现代拉斯维加斯法证世界
cultural_paradigm: 法医学+刑侦推理
narrative_core: 科学破案还原真相

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Comp
n_others: []
rel_object: null
t_can_carry: [T5, T2]
core_emotion_note: ""
core_conflict: 法证团队用科学证据对抗罪犯，还原每起案件真相

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 犯罪
theme_secondary: [刑侦, 推理, 悬疑, 警务]
visual_tags: [实验室, 犯罪现场, 显微镜证据, 审讯室, 都市夜景]


# === 评分(v0 已有)===
acquisition_score: 4

# === 素材与玩法 ===
material_hooks: [犯罪现场勘查, 显微镜下证据, 血迹弹道分析, 实验室科技感, 审讯室对峙]
existing_games: []
recommended_playstyles: []
risk_notes: [红海, 版权成本高]

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
