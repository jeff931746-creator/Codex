#!/usr/bin/env python3
"""把当前 shell 的 Claude 认证变量写进 ~/.claude/settings.json 的 env。

为什么需要：lark-channel-bridge 由 launchd 作为后台 daemon 启动，daemon
不读 ~/.zshrc，所以 daemon 里的 claude 拿不到 ANTHROPIC_AUTH_TOKEN，调 API
会返回 401。settings.json 的 env 是 Claude Code 官方配置位，任何方式启动的
claude 都会读它，于是 daemon 里的 claude 也能认证。

必须在登录 shell 下运行才能读到变量，例如：
    zsh -ic 'python3 inject_env.py'
"""
import os, json, shutil

KEYS = [
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_MODEL",
    "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL",
    "CLAUDE_CODE_SUBAGENT_MODEL",
]

p = os.path.expanduser("~/.claude/settings.json")
if os.path.exists(p):
    shutil.copy(p, p + ".bak")
    with open(p) as f:
        d = json.load(f)
else:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    d = {}

env = d.get("env", {})
added, missing = [], []
for k in KEYS:
    v = os.environ.get(k)
    if v:
        env[k] = v
        added.append(k)
    else:
        missing.append(k)
d["env"] = env

with open(p, "w") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

# 只打印键名，绝不打印值
print("已写入 settings.json env 键:", added)
if missing:
    print("当前 shell 未取到（已跳过）:", missing)
print("备份:", p + ".bak")
