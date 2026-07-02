# auto-resume —— 额度受限时无人值守续接任务

额度用完、输入框锁死时，让任务在额度恢复后自动接着跑，不用守在电脑前。
本质是**定时反复重试**：限流期间空跑记日志，额度一恢复下次自动推进。不省额度，省盯屏时间。

## 两种模式

### 1. 会话续接（接 claude 对话历史）

适合：一个对话里交代了大活，干到一半额度没了，想接着干完。

```bash
auto-resume.sh session <标签> <session_id> <工作目录> [间隔分钟=30] [最大次数=48]
```

- `session_id`：会话 ID。查法：`ls -t ~/.claude/projects/<项目目录>/*.jsonl | head -1`，文件名去掉 `.jsonl` 即是。
- `<工作目录>`：该会话所在目录（worktree 会话就填 worktree 路径）。

### 2. memory 任务续接（读 task_<标签>.md）

适合：有明确完成判据的业务任务，状态已存进 `memory/task_<标签>.md`。

```bash
auto-resume.sh start <标签> [间隔分钟=30] [最大次数=48]
```

## 通用命令

```bash
auto-resume.sh status <标签>   # 看试了几次、最近日志
auto-resume.sh stop   <标签>   # 手动停（注销 cron + 清状态）
auto-resume.sh list            # 列出所有在跑的
```

## 三重停止机制（防止无限烧额度）

1. claude 在回复最后单独输出 `TASK_COMPLETE` → 自动注销 cron + 弹通知
2. 累计次数达 `最大次数`（默认 48 = 30 分钟 × 24 小时）→ 自动停 + 通知
3. 手动 `stop`

## 限制与注意

- **不省额度**：每次重试照常扣额度，省的是盯屏时间。
- **只适合机械/可验证的活**：无人监督跑判断密集任务有跑偏风险。默认 prompt 已要求"需要拍板就停下"，但仍建议只放手给批量入库、跑收集、格式归一这类。
- **别和手动操作抢同一会话**：挂上会话续接 cron 后，自己就别再手动打开同一个对话，并发写同一 session 历史会出问题。
- **worktree 会话路径是临时的**：worktree 一旦删除，`--resume` 在该目录找不到会话。长期任务建议在主目录会话里跑。
- 自定义每轮指令：在 `prompts/<标签>.txt` 写自定义 prompt，覆盖默认模板。

## 文件

- `auto-resume.sh` —— 主脚本（入版本）
- `prompts/<标签>.txt` —— 可选的自定义 prompt（入版本）
- `_state/`、`_logs/` —— 运行状态与日志（已 gitignore）
