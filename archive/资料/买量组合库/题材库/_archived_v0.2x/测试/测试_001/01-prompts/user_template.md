# User Prompt 模板

## 任务

对以下题材做一次归类判断。严格按 system prompt 的字段表输出 JSON,不要 markdown 代码块,不要解释。

## 题材输入

```
题材名: __RAW_THEME__
四象限定位: __QUADRANT__
有效获量评分: __ACQUISITION_SCORE__
ROI承接评分: __ROI_SCORE__
玩法承接(参考,不强制): __PLAYSTYLE_HINT__
素材钩子: __MATERIAL_HOOKS__
评审说明: __REVIEW_NOTES__
来源: __SOURCE__
```

## 必须遵守

- 12 个主母题材 + "未归类",选其一作为 primary_motif
- strongest_carrier_relation 必须写循环承接关系,不接受品类名
- 即使主归类清晰也要在 boundary_notes 中说明排除了哪个相邻母题
- commercial_failure_cases 至少 2 项

直接输出 JSON。
