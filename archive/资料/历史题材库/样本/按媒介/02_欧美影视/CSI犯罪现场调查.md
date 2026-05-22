---
# === 身份 ===
work_id: WORK-TVW-00382
work_name: CSI犯罪现场调查
work_name_alt: []
media_type: TVW
year_first: 2000
year_range: [2000, 2000]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 现代拉斯维加斯/犯罪现场
cultural_paradigm: 法证科学+刑侦体系
narrative_core: 案件推理+真相揭露

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Comp
n_others: []
rel_object: null
t_can_carry: [T5, T2]
core_emotion_note: ""
core_conflict: 犯罪现场遗留的线索与罪犯的隐藏真相之间的智力博弈

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 犯罪
theme_secondary: [刑侦, 推理, 悬疑]
visual_tags: [实验室, 犯罪现场, 显微镜下证据, 尸检解剖特写, 枪林弹雨]


# === 评分(v0 已有)===
acquisition_score: 4

# === 素材与玩法 ===
material_hooks: [显微镜下证据, 弹道重建画面, 尸检解剖特写, 犯罪现场全景, 嫌疑人审讯对峙]
existing_games: ["CSI: Crime Scene Investigation"]
recommended_playstyles: []
risk_notes: [版权成本高, 玩法偏单机]

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
