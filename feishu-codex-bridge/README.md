# Feishu Codex Bridge

一个最小可用的自建桥接服务：

- 飞书机器人把消息推给本地服务
- 本地服务调用 OpenAI 或 Claude 模型
- 模型回复再发回飞书

这套方案是“自建桥接”，不是 Codex 官方飞书机器人集成。

## 适合什么场景

- 你想在飞书里和 AI 聊天
- 你愿意自己维护一个本地或云端服务
- 你接受使用飞书开放平台应用

## 当前实现范围

- 支持飞书 `im.message.receive_v1`
- 支持 URL 验证
- 支持文本消息
- 支持 OpenAI Responses API
- 支持 Anthropic Messages API
- 不依赖第三方 npm 包

## 当前不包含

- 飞书消息加密解密
- 多轮会话记忆持久化
- 文件/图片处理
- 工具调用审批流
- 复杂权限系统

如果你后面要把它升级成更像 OpenClaw/Codex 的工作流，这个骨架可以继续扩展。

## 目录

- [server.mjs](/Users/mt/Documents/Codex/feishu-codex-bridge/server.mjs)
- [package.json](/Users/mt/Documents/Codex/feishu-codex-bridge/package.json)
- [.env.example](/Users/mt/Documents/Codex/feishu-codex-bridge/.env.example)

## 1. 准备环境变量

复制一份环境变量：

```bash
cp .env.example .env
```

填入：

- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `MODEL_PROVIDER`
- `OPENAI_API_KEY` 或 `ANTHROPIC_API_KEY`

可选：

- `FEISHU_VERIFICATION_TOKEN`
- `OPENAI_MODEL`
- `ANTHROPIC_MODEL`
- `SYSTEM_PROMPT`

提供方说明：

- `MODEL_PROVIDER=auto`：默认值；如果配置了 `ANTHROPIC_API_KEY`，优先走 Claude，否则走 OpenAI
- `MODEL_PROVIDER=openai`：强制使用 OpenAI
- `MODEL_PROVIDER=anthropic`：强制使用 Claude

## 2. 启动服务

Node 18+ 即可：

```bash
export $(grep -v '^#' .env | xargs)
npm start
```

健康检查：

```bash
curl http://127.0.0.1:3000/health
```

## 3. 飞书开放平台配置

你需要创建一个飞书自建应用，并配置：

- 机器人能力
- 事件订阅
- 事件：`im.message.receive_v1`

如果你使用 webhook 模式，把事件回调 URL 指向：

```text
http://你的服务地址:3000/feishu/events
```

如果飞书要求校验 token，就把同一个值写进：

- 飞书后台的 Verification Token
- `.env` 里的 `FEISHU_VERIFICATION_TOKEN`

## 4. 消息流

OpenAI 模式：

```text
Feishu -> /feishu/events -> OpenAI Responses API -> Feishu
```

Claude 模式：

```text
Feishu -> /feishu/events -> Anthropic Messages API -> Feishu
```

## 5. 下一步怎么升级

如果你想把它做得更像真正的 Codex/Agent，可以继续加：

1. 会话记忆存储
2. 审批流
3. 白名单用户控制
4. 文件处理
5. 工具调用
6. 接本地 OpenClaw Gateway，而不是直接调 OpenAI

## 6. 用 Claude 的最小配置

`.env` 里最少填这些：

```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=your_feishu_app_secret
MODEL_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-haiku-latest
```

启动后访问：

```bash
curl http://127.0.0.1:3000/health
```

会返回当前实际使用的 `provider` 和 `model`。

## 7. 重要说明

严格说，这不是“Codex 官方直接接飞书”。

这是一个**自建飞书机器人桥接服务**，底层目前可以调用 OpenAI 或 Claude。  
如果你想更接近你现在这套本地工作流，后面我可以继续帮你把它改成：

- 飞书 -> 本地桥接服务 -> OpenClaw Gateway

这样飞书前台，背后就更像你现在在用的那套 agent 体系了。
