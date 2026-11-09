# 飞书群消息日报

Windows、macOS、Linux 使用 `daily_digest.py`。依赖 Python、Node.js、已完成登录的 lark-cli 和 Claude CLI；命令需在 PATH 中，也可用 `LARK_BIN`、`CLAUDE_BIN` 指定实际可执行文件。

```powershell
python daily_digest.py --chat-id YOUR_DESTINATION_CHAT_ID
```

该命令读取当前用户可见群消息，调用 Claude 生成摘要，再以机器人身份发往指定群。目的群必须由 `--chat-id` 或 `BOT_CHAT_ID` 明确指定。默认状态目录为本目录 `.state/`，可用 `--state-dir` 或 `FEISHU_DIGEST_STATE_DIR` 调整。若需续接旧 shell 版本读取进度，将 `--state-dir` 指向其原状态目录。

读取分页失败的群保留原进度；摘要生成或发送失败时不提交新进度。成功发送后保存读取位置。不要同时运行多个实例。原 `daily_digest.sh` 保留为 Unix 旧入口，不自动迁移计划任务或账号认证。本轮未调用外部账号、发送日报或在 Windows 实机运行。
