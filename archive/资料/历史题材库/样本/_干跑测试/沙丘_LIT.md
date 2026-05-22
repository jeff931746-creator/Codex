---
work_id: TBD
work_name: 沙丘_LIT
work_name_alt: [Dune (Frank Herbert)]
media_type: LIT
year_first: 1965
year_range: [1965, 1985]
season_count: 6

environment: "远未来星际帝国 + 香料沙漠星球阿拉吉斯"
cultural_paradigm: "贵族封建 + 宗教预言 + 沙漠生态"
narrative_core: "弥赛亚式的英雄崛起与宿命的代价"

n_main: N-Comp
n_others: [N-Rel]
rel_object: mixed
t_can_carry: [T5, T2]
core_emotion_note: "认知胜任为主(读者破解庞大世界观与政治阴谋),变强叙事为辅(保罗成长);N-Rel mixed 因为同时含贵族家族纽带(virtual)与现实读者社群讨论(real)"
core_conflict: "贵族家族复仇 + 个人对抗预言宿命"

mother_theme_id: THM-UNK-001
secondary_motif_ids: []
motif_confidence: low

acquisition_score: 5
roi_score: 4
quadrant: TBD

material_hooks: [沙虫骑乘, 沙漠帝国, 预言弥赛亚, 香料经济]
existing_games: [Dune II, Dune Spice Wars, Dune Awakening]
recommended_playstyles: []
risk_notes: [世界观庞大需长解释, 老 IP 年轻用户认知低, 文化壁垒]

source: human-dryrun
source_run_id: 2026-05-15-dryrun01
evidence_level: B
review_status: auto
last_updated: 2026-05-15
---

## 干跑测试备注

- 测试点:跨媒介同 IP(沙丘有小说/电影/剧集/游戏) + 媒介归类 + 文件命名后缀
- ⚠️ **判定卡壳 1**:小说归 LIT,但沙丘还有 2021/2024 两部电影、Sci-Fi 频道剧集和多款游戏。同 IP 跨媒介怎么处理?
  - 当前 SCHEMA 规则:同名不同媒介加后缀 → `沙丘_LIT.md` / `沙丘_MVW.md` 各一份
  - 各份的字段会有差异(2021 电影更突出视觉冲击,小说更突出哲学/政治深度)
  - **暴露规范问题**:跨媒介 IP 是否应该有"IP 主档 + 媒介变体"双层结构? 当前 SCHEMA 把它们当成独立作品,可能导致同 IP 在不同样本里 N/T 判定不一致(参考提示词 03 交叉校验)
  - **改进建议**:在 SCHEMA §2 文件命名 加一句:"跨媒介同 IP 时,各媒介独立条目,但需在 work_name_alt 互相引用(便于交叉校验),并在 core_emotion_note 注明媒介差异"
- ⚠️ **判定卡壳 2**:rel_object 是 virtual / real / mixed?
  - 角色都是虚构 → virtual
  - 但沙丘读者社群讨论极活跃,部分粘性来自社群归属 → real?
  - **判 mixed**,但这判定是否过度解读? 作品本身没有引导读者社交,只是事后社群自发形成
  - **修正**:应判 virtual,理由是 SCHEMA 的 rel_object 指"作品提供的关系对象",不指"读者周边社交"
  - 这是 DeepSeek 跑批时容易犯的"过度解读"错误,需要在提示词 01 里加一句:**"rel_object 只看作品内提供的关系对象,不计读者社群"**

## 修正后字段

```yaml
n_others: []                # 删掉 N-Rel,沙丘核心是认知胜任,关系驱动弱
rel_object: null            # 对应修正
```

- **暴露规范问题**:本样本的 n_others / rel_object 我自己判错了两次,说明这两个字段的判定门槛比想象中高。需要在提示词 01 里增加更多"反例提醒"
