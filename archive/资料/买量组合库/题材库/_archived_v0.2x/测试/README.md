# 题材库测试目录

## 用途

存放题材母题候选库的盲归类测试运行结果。每一轮测试一个子目录 `测试_NNN/`，按时间顺序递增编号，永不复用。

## 目录约定

```
题材库/
  _draft/                    # 候选库与测试矩阵草稿(每版独立文件)
  测试/                       # 测试运行目录(本目录)
    测试_001/                  # 第一轮测试(2026-05-14)
      01-prompts/             # system prompt + 用户 prompt 模板
      02-samples/             # 60 条样本(30 正例 + 18 混淆 + 12 盲选)
      03-results/             # 每条样本的归类结果(JSON,一题一文件)
      04-reports/             # 覆盖率报告、混淆表、反证日志、聚类报告
    测试_002/                  # 第二轮测试(扩库或复测)
      ...
  题材索引.md                  # 正式入库索引(只列 BOUNDARY_VALID 之后的母题)
```

## 命名规则

- `测试_NNN/` 三位数字，从 001 开始递增
- 每轮独立目录，结果不覆盖、不删除，便于横向对比
- 子目录固定 4 个：`01-prompts/`、`02-samples/`、`03-results/`、`04-reports/`
- 不在测试目录里放草稿；草稿落 `_draft/`

## 输入与产物对应

| 输入(由测试启动者准备) | 产物(由测试完成后填充) |
|---|---|
| `01-prompts/system.md` | `04-reports/覆盖率报告_测试NNN.md` |
| `01-prompts/user_template.md` | `04-reports/边界混淆表_测试NNN.md` |
| `02-samples/{group}.json` | `04-reports/反证日志_测试NNN.md` |
| `_draft/母题材候选库_v0.X.X.md` | `04-reports/无主归类聚类_测试NNN.md` |
| `_draft/母题材测试审核矩阵_v0.X.X.md` | `03-results/*.json`(每条样本) |

## 启动条件

启动一轮测试前，必须满足:

1. 候选库已冻结(对应版本号已写入 `_draft/`)
2. 测试矩阵已冻结(对应版本号已写入 `_draft/`)
3. 本轮 `测试_NNN/01-prompts/` 与 `02-samples/` 已完整准备
4. API key 与 provider 走 `.claude/rules/api-client-architecture.md` 协议

## 收尾约定

测试完成后:

- `04-reports/` 必填四份(覆盖率、混淆、反证、聚类)
- 候选库若需调整，写入新版本 `_draft/母题材候选库_v0.X.X.md`，不改 `测试_NNN/`
- 不向正式 `题材索引.md` 写任何 `THM-*`，除非达到 `BOUNDARY_VALID`
