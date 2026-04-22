# Feishu Codex Bridge

一个最小可用的自建桥接服务：

- 飞书机器人把消息推给本地服务
- 本地服务把消息送进你本地的 Codex/OpenClaw 会话
- 会话回复再发回飞书

这套方案是“自建桥接”，不是 Codex 官方飞书机器人集成。

This bridge is expected to be operated under the root workspace session protocol in [`/Users/mt/Documents/Codex/CLAUDE.md`](/Users/mt/Documents/Codex/CLAUDE.md).

## 适合什么场景

- 你想在飞书里和 AI 聊天
- 你想让飞书消息进入本地 OpenClaw / Codex 工作流
- 你愿意自己维护一个本地或云端服务
- 你接受使用飞书开放平台应用

## 当前实现范围

- 支持飞书 `im.message.receive_v1`
- 支持 URL 验证
- 支持文本消息
- 支持识别飞书 `docx` 文档链接并读取纯文本正文
- 支持本地 Codex Desktop 会话回放与续写
- 可选支持 OpenAI Responses API
- 可选支持 SiliconFlow OpenAI 兼容接口
- 可选支持 Anthropic Messages API
- 不依赖第三方 npm 包

## 当前不包含

- 飞书消息加密解密
- 多轮会话记忆持久化
- 文件/图片处理
- 工具调用审批流
- 复杂权限系统

如果你后面要把它升级成更像 OpenClaw/Codex 的工作流，这个骨架可以继续扩展。

## 目录

- [server.mjs](/Users/mt/Documents/Codex/tools/feishu-codex-bridge/server.mjs)
- [package.json](/Users/mt/Documents/Codex/tools/feishu-codex-bridge/package.json)
- [.env.example](/Users/mt/Documents/Codex/tools/feishu-codex-bridge/.env.example)
- [run_named_tunnel.sh](/Users/mt/Documents/Codex/tools/feishu-codex-bridge/run_named_tunnel.sh)
- [run_quick_tunnel.sh](/Users/mt/Documents/Codex/tools/feishu-codex-bridge/run_quick_tunnel.sh)
- [install_launchd.sh](/Users/mt/Documents/Codex/tools/feishu-codex-bridge/install_launchd.sh)
- [cloudflared/config.example.yml](/Users/mt/Documents/Codex/tools/feishu-codex-bridge/cloudflared/config.example.yml)

## 1. 准备环境变量

复制一份环境变量：

```bash
cp .env.example .env
```

填入：

- `HOST=127.0.0.1`
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `FEISHU_USER_AUTH_APP_ID`
- `FEISHU_USER_AUTH_APP_SECRET`
- `FEISHU_EVENT_MODE`
- `FEISHU_READ_ACCESS_MODE`
- `FEISHU_BACKEND`

可选：

- `FEISHU_VERIFICATION_TOKEN`
- `FEISHU_SESSION_MAP`
- `FEISHU_REPLY_MODE`
- `FEISHU_DIGEST_ENABLED`
- `FEISHU_DIGEST_HOUR`
- `FEISHU_DIGEST_MINUTE`
- `FEISHU_DIGEST_PREFIX`
- `FEISHU_DIGEST_MAX_MESSAGES`
- `FEISHU_DIGEST_TARGET_CHAT_ID`
- `FEISHU_CROSS_CHAT_MAX_CHATS`
- `FEISHU_CROSS_CHAT_MAX_MESSAGES_PER_CHAT`
- `FEISHU_CROSS_CHAT_MAX_TOTAL_MESSAGES`
- `FEISHU_CROSS_CHAT_CONCURRENCY`
- `FEISHU_USER_AUTH_REDIRECT_URI`
- `FEISHU_USER_AUTH_SCOPE`
- `FEISHU_USER_TOKEN_FILE`
- `CODEX_SESSION_TARGET`
- `CODEX_PYTHON_BIN`
- `CODEX_DESKTOP_BRIDGE_SCRIPT`
- `CODEX_BRIDGE_WORKDIR`
- `FEISHU_STATE_FILE`
- `OPENAI_MODEL`
- `SILICONFLOW_API_KEY`
- `SILICONFLOW_MODEL`
- `SILICONFLOW_BASE_URL`
- `ANTHROPIC_MODEL`
- `SYSTEM_PROMPT`

后端说明：

- `FEISHU_BACKEND=codex`：默认值；把飞书消息送进本地 Codex/OpenClaw 会话
- `FEISHU_BACKEND=openai`：强制使用 OpenAI
- `FEISHU_BACKEND=siliconflow`：强制使用硅基流动的 OpenAI 兼容接口
- `FEISHU_BACKEND=anthropic`：强制使用 Claude

事件接入模式：

- `FEISHU_EVENT_MODE=webhook`：默认值；通过 `POST /feishu/events` 接收飞书推送
- `FEISHU_EVENT_MODE=long_connection`：通过飞书官方长连接收事件，不需要公网回调 URL
- `FEISHU_EVENT_MODE=auto`：优先启动长连接，同时保留 webhook 入口做兜底

读取身份模式：

- `FEISHU_READ_ACCESS_MODE=tenant`：默认值；按机器人/应用身份读取群列表和群消息
- `FEISHU_READ_ACCESS_MODE=user`：按你个人授权后的 `user_access_token` 读取群列表和群消息
- `FEISHU_USER_AUTH_APP_ID` / `FEISHU_USER_AUTH_APP_SECRET`：可选；如果你打算把“机器人收发消息”和“个人账号授权读群”拆成两个飞书应用，这里填专门用于新版终端用户授权的 Web 应用凭证；留空时默认复用 `FEISHU_APP_ID` / `FEISHU_APP_SECRET`
- `FEISHU_USER_AUTH_REDIRECT_URI`：本地 OAuth 回调地址，默认是 `http://127.0.0.1:3000/feishu/auth/callback`
- `FEISHU_USER_AUTH_SCOPE`：新版飞书 OAuth 授权时显式申请的 user scopes，默认会带上跨群总结所需的 `im:chat:readonly im:message:readonly im:message.group_msg:get_as_user`
- `FEISHU_USER_TOKEN_FILE`：留空时，默认把用户 token 状态写到 bridge 目录下的 `.state/user-access-token.json`

回复模式：

- `FEISHU_REPLY_MODE=reply`：收到消息后立刻回消息
- `FEISHU_REPLY_MODE=summary_only`：只记录消息，不立刻回消息

纪要模式：

- `FEISHU_DIGEST_ENABLED=1`：开启自动群纪要
- `FEISHU_DIGEST_HOUR=9`：每天几点执行自动纪要
- `FEISHU_DIGEST_MINUTE=0`：每天第几分钟执行自动纪要
- `FEISHU_DIGEST_PREFIX=【自动纪要】`：自动纪要发到群里的开头标识
- `FEISHU_DIGEST_MAX_MESSAGES=120`：每次纪要最多取多少条最近消息
- `FEISHU_DIGEST_TARGET_CHAT_ID`：纪要统一发送到这个专属群，留空则不会发送纪要
- `FEISHU_CROSS_CHAT_MAX_CHATS=30`：跨群汇总时，最多扫描多少个机器人可见群
- `FEISHU_CROSS_CHAT_MAX_MESSAGES_PER_CHAT=25`：跨群汇总时，每个群最多带多少条原始消息进模型
- `FEISHU_CROSS_CHAT_MAX_TOTAL_MESSAGES=240`：跨群汇总时，总共最多带多少条消息，避免上下文过长
- `FEISHU_CROSS_CHAT_CONCURRENCY=6`：跨群汇总时，并发拉取多少个群的历史消息；群很多时可以适当调高，但过高会更容易撞上飞书限流
- `FEISHU_RUN_INDICATOR=1`：在 `summary_only` 模式下，收到消息后给原消息加一个表态
- `FEISHU_RUN_INDICATOR_EMOJI_TYPE=WINK`：表态类型，默认用眨眼，最接近“稍等”的语气
- `FEISHU_BOT_OPEN_ID`：可选，机器人自己的 `open_id`，填了以后能精确识别 @ 机器人
- `FEISHU_OWNER_OPEN_ID`：可选，你自己的 `open_id`，填了以后你发消息会直接回复，其他人仍然需要 @ 机器人

跨群汇总说明：

- 当你发类似“总结今天所有未读的群聊记录”时，bridge 会尝试扫描机器人可见的所有群，而不再只总结当前群
- 由于飞书没有直接提供“你个人客户端未读红点”给机器人读取，这里的“未读”采用近似口径：
  - 优先取各群“上次自动纪要之后”的新消息
  - 从未做过纪要的群，则取今天的消息
- 如果群太多或消息太长，bridge 会按上面的三个上限做裁剪，并在汇总时提示这是裁剪后的结果

如果你切到 `FEISHU_READ_ACCESS_MODE=user`：

- 跨群汇总会改为扫描“你个人账号可见”的群，而不是“机器人所在”的群
- 这不要求机器人进每一个被扫描的群
- 但仍然不保证等于飞书客户端的“未读红点”；当前 bridge 依然采用“未处理消息”的近似口径

如果你要让机器人自动读取飞书文档正文，还需要给应用补文档读取权限，并把文档分享给机器人可访问的范围。
当前这版默认只支持 `docx` 文档链接，格式通常长这样：

```text
https://xxx.feishu.cn/docx/AbCdEfGhIjKlMnOpQrStUvWx
```

支持读正文后，机器人会先拉取文档纯文本，再结合你的原消息一起做审阅或总结。

四分类规则：

- `重要工作内容`：只保留会影响交付、审批、排期、依赖、风险和决策的内容；没有明确执行价值就不要放进去
- `日常工作进度`：只保留 routine 进展、阶段状态、已完成/进行中/待开始
- `讨论/闲聊`：只保留与工作相关但未形成动作的讨论，内容要极度压缩
- `摸鱼`：只保留明显无关工作的内容，且必须短，不扩写

路由说明：

- `FEISHU_SESSION_MAP` 是一个 JSON 对象，用来按 `chat_id` 或 `sender open_id` 绑定不同会话
- 键支持 `chat:<chat_id>`、`sender:<open_id>`，也支持直接写裸 `chat_id` 或 `open_id`
- 值是 `codex_desktop_bridge.py select --target ...` 能识别的会话名或 session id

示例：

```bash
FEISHU_SESSION_MAP={"chat:oc_123":"产品群","sender:ou_456":"个人工作流"}
```

如果你选择 `codex`，先在本地选定一个可恢复的 Codex 会话：

```bash
python3 /Users/mt/Documents/Codex/tools/codex-desktop-bridge/codex_desktop_bridge.py list
python3 /Users/mt/Documents/Codex/tools/codex-desktop-bridge/codex_desktop_bridge.py select --target "会话名或 session id"
```

状态持久化：

- `FEISHU_STATE_FILE` 留空时，会默认把群消息缓存写到 bridge 目录下的 `.state/chat-state.json`
- 这个文件会保存最近收到的群消息和纪要游标，避免 bridge 重启后纪要丢上下文
- `FEISHU_USER_TOKEN_FILE` 留空时，会默认把用户授权得到的 `user_access_token` / `refresh_token` 写到 `.state/user-access-token.json`

## 2. 启动服务

Node 18+ 即可：

```bash
sh ./run.sh
```

健康检查：

```bash
curl http://127.0.0.1:3000/health
```

如果你启用了 `FEISHU_READ_ACCESS_MODE=user`，还可以看授权状态：

```bash
curl http://127.0.0.1:3000/feishu/auth/status
curl http://127.0.0.1:3000/feishu/auth/start
```

`/feishu/auth/start` 会返回一个飞书新版 OAuth 授权 URL。浏览器打开后，授权成功会跳回 `FEISHU_USER_AUTH_REDIRECT_URI`，bridge 会自动换取并保存 `user_access_token`。

如果你之前已经授权过一次，但 bridge 里拿到的 token 仍然是历史版本（通常以 `u-` 开头），跨群读取群历史会被飞书拒绝。此时需要：

- 升级到新版 `/authorize` 授权入口
- 确认 `FEISHU_USER_AUTH_SCOPE` 包含跨群总结需要的 user scopes
- 如果当前机器人应用仍然只会签发历史版 token，改用单独的 Web 应用填到 `FEISHU_USER_AUTH_APP_ID` / `FEISHU_USER_AUTH_APP_SECRET`
- 再重新授权一次

如果你没有配置 `FEISHU_USER_AUTH_APP_ID` / `FEISHU_USER_AUTH_APP_SECRET`，bridge 现在会直接提示“当前机器人应用只会签发历史版 token，需要单独的 Web 应用或切回 tenant 模式”，不会再无限重复拉你去授权。

## 3. 飞书开放平台配置

你需要创建一个飞书自建应用，并配置：

- 机器人能力
- 事件订阅
- 事件：`im.message.receive_v1`

如果你使用 `FEISHU_EVENT_MODE=long_connection` 或 `auto`，优先推荐在飞书后台选择：

- `使用长连接接收事件`

这条路径不需要公网回调 URL，但要求 bridge 正在运行，飞书后台才能保存成功。

如果你坚持使用 `webhook` 模式，上线前还要确认这几项：

- 你的桥接服务有一个飞书可访问的公网地址
- 事件回调 URL 能访问到 `POST /feishu/events`
- 如果服务跑在本机，通常还需要反向代理或内网穿透
- 如果你启用了 Verification Token，飞书后台和 `.env` 里的值必须一致

如果你使用 webhook 模式，把事件回调 URL 指向：

```text
http://你的服务地址:3000/feishu/events
```

如果服务在本机，`localhost` 和 `127.0.0.1` 只对本机可见，飞书无法直接回调到它们。

如果飞书要求校验 token，就把同一个值写进：

- 飞书后台的 Verification Token
- `.env` 里的 `FEISHU_VERIFICATION_TOKEN`

## 3.1 选一种接入方式

推荐顺序：

1. `long_connection`
1. `webhook + named tunnel / 固定域名`
1. `webhook + quick tunnel` 仅联调

你需要让飞书能访问到这个服务的公网入口。常见只有三种：

1. 直接部署到一台公网机器
1. 本机跑服务，再用反向代理或内网穿透转出去
1. 先只在内网联调，飞书后台先不填回调，等公网地址准备好再切

如果你现在只有这台 Mac，本机地址一般长这样：

```text
http://127.0.0.1:3002/feishu/events
```

这个地址只能本机自己访问，飞书不能直接打进来。你需要把它映射成一个公网可访问地址，然后在飞书后台填：

```text
https://你的公网域名/feishu/events
```

如果你已经有反向代理，核心就是把外部的 `/feishu/events` 转到本机 `127.0.0.1:3002/feishu/events`。

如果你打算用内网穿透，先让穿透工具把本地 `3002` 端口暴露出去，再把穿透后的公网地址填到飞书回调里。

### Feishu long connection

如果你不想再依赖公网回调，最稳的是直接改成长连接：

1. `.env` 里设：

```bash
FEISHU_EVENT_MODE=long_connection
```

2. 保持 bridge 运行：

```bash
sh ./run.sh
```

3. 飞书后台进入 `事件与回调`：

- 选择 `使用长连接接收事件`
- 添加事件 `im.message.receive_v1`
- 保存后发布应用版本

4. 本地检查：

```bash
curl http://127.0.0.1:3002/health
```

你会看到：

- `requestedEventMode=long_connection`
- `eventMode=long_connection`

如果 `requestedEventMode` 是 `long_connection`，但 `eventMode` 仍然是 `webhook`，说明长连接没有成功启动，先看 `longConnection.lastError`。

### Cloudflared quick tunnel

如果你只是想先跑通联调，最省事的是用 quick tunnel：

```bash
cloudflared tunnel --url http://127.0.0.1:3002
```

启动后它会打印一个临时公网地址，形如：

```text
https://xxxx.trycloudflare.com
```

把这个地址填到飞书事件订阅的回调 URL，路径固定为：

```text
https://xxxx.trycloudflare.com/feishu/events
```

注意：

- 这个地址是临时的，重启后可能会变
- 适合开发联调，不适合长期生产
- 长期使用建议改成你自己的 Cloudflare named tunnel 或固定域名

如果你只是想先减少“桥服务自己挂掉”的概率，也可以把 quick tunnel 交给 `launchd` 托管：

```bash
sh ./install_launchd.sh quick-tunnel
```

但要注意：它只是自动拉起，不会让 URL 变固定。

### Cloudflared named tunnel

长期要稳定，建议直接换成 named tunnel。这样飞书后台只需要填一次固定回调地址。

1. 登录 Cloudflare：

```bash
cloudflared tunnel login
```

2. 创建一条 tunnel：

```bash
cloudflared tunnel create feishu-codex
```

3. 复制模板配置并填入 tunnel id、credentials 文件和固定 hostname：

```bash
cp cloudflared/config.example.yml cloudflared/config.yml
```

模板文件在：

- [cloudflared/config.example.yml](/Users/mt/Documents/Codex/tools/feishu-codex-bridge/cloudflared/config.example.yml)

4. 给 tunnel 绑定固定域名：

```bash
cloudflared tunnel route dns feishu-codex feishu-codex.example.com
```

5. 本地启动 named tunnel：

```bash
sh ./run_named_tunnel.sh
```

6. 飞书事件订阅回调 URL 填：

```text
https://feishu-codex.example.com/feishu/events
```

7. 本地验证：

```bash
curl https://feishu-codex.example.com/feishu/events?challenge=test123
```

如果你想长期跑在这台 Mac 上，建议把 bridge 和 named tunnel 都交给 `launchd`：

```bash
sh ./install_launchd.sh bridge
sh ./install_launchd.sh named-tunnel
```

对应模板：

- [launchd/com.mt.feishu-codex-bridge.plist](/Users/mt/Documents/Codex/tools/feishu-codex-bridge/launchd/com.mt.feishu-codex-bridge.plist)
- [launchd/com.mt.feishu-codex-cloudflared.plist](/Users/mt/Documents/Codex/tools/feishu-codex-bridge/launchd/com.mt.feishu-codex-cloudflared.plist)
- [launchd/com.mt.feishu-codex-quick-tunnel.plist](/Users/mt/Documents/Codex/tools/feishu-codex-bridge/launchd/com.mt.feishu-codex-quick-tunnel.plist)

注意：这套 `launchd` 安装脚本会把运行时文件同步到 `~/Library/Application Support/FeishuCodexBridge/bridge/`，然后让系统从那里启动。这样可以绕开 macOS 对 `Documents/` 目录的后台访问限制，避免出现“agent 已加载但脚本打不开”的假启动状态。

## 4. 消息流

本地 Codex 模式：

```text
Feishu -> /feishu/events -> codex_desktop_bridge.py send -> codex exec resume -> Feishu
```

OpenAI 模式：

```text
Feishu -> /feishu/events -> OpenAI Responses API -> Feishu
```

SiliconFlow 模式：

```text
Feishu -> /feishu/events -> SiliconFlow /v1/chat/completions -> Feishu
```

Claude 模式：

```text
Feishu -> /feishu/events -> Anthropic Messages API -> Feishu
```

如果你把 `FEISHU_REPLY_MODE` 设成 `summary_only`，消息会先进入本地缓冲，不会立刻回复。
但有两个例外：`FEISHU_OWNER_OPEN_ID` 对应的本人消息，或群里明确 `@机器人`，仍然会直接回复。
如果同时开启 `FEISHU_RUN_INDICATOR=1`，机器人会直接给原消息加表态，让你知道它在线并已接收消息。
表态会尽量对所有能识别到 `chat_id` 和 `message_id` 的消息尝试添加，不再要求必须是文本。
如果消息里 @ 了机器人，或 `FEISHU_BOT_OPEN_ID` 匹配到机器人本人，机器人会直接回复正文而不是只加表态。
如果同时开启 `FEISHU_DIGEST_ENABLED=1`，服务会每天按 `FEISHU_DIGEST_HOUR:FEISHU_DIGEST_MINUTE` 把每个群最近收到的消息整理成一条自动纪要，然后统一发到 `FEISHU_DIGEST_TARGET_CHAT_ID` 指定的专属群。
如果这个值留空，纪要会生成但不会发送，以免误发回原群。
纪要输出默认按四类分组，且每类都遵守上面的约束。

手动检查：

```text
GET /digest
POST /digest/run
```

`GET /digest` 会返回当前每个群缓存了多少条消息，`POST /digest/run` 会立刻执行一次纪要。

现在这条缓存也会落盘，所以 bridge 重启后，纪要不会因为进程重启而把已收到的群消息全部丢掉。

## 5. 稳定运行建议

如果你不想再遇到“昨天还好好的，今天突然不回了”，至少要同时满足这三件事：

1. 优先使用 `long_connection`；如果必须用 webhook，再上固定公网入口
2. 使用进程托管：把 bridge 和 tunnel 都交给 `launchd`
3. 使用正确回复策略：如果你希望“发了就回”，把 `FEISHU_REPLY_MODE` 改成 `reply`

快速对照：

- 最稳：`FEISHU_EVENT_MODE=long_connection` + `sh ./install_launchd.sh bridge`
- 只想联调：`sh ./run.sh` + `cloudflared tunnel --url http://127.0.0.1:3002`
- 想减少本机进程挂掉：`sh ./install_launchd.sh bridge`
- 想稳定对外地址：named tunnel
- 想开机自动恢复：`launchd + named tunnel`

## 6. 故障优先排查

1. 先看本地桥还在不在：

```bash
curl http://127.0.0.1:3002/health
```

2. 再看飞书消息有没有进桥：

```bash
curl http://127.0.0.1:3002/debug/latest-chat
```

3. 如果本地健康但没有聊天记录：

- `eventMode=webhook` 时，问题几乎一定在“飞书后台回调 URL / tunnel / 应用发布”
- `eventMode=long_connection` 时，优先检查飞书后台有没有真的保存成长连接模式，以及应用版本是否已发布

4. 如果聊天记录进来了但没回消息，优先检查：

- `FEISHU_REPLY_MODE` 是否是 `summary_only`
- 你是不是本人账号发的消息
- 你有没有在群里 `@机器人`

5. 如果你刚换了公网地址，记得去飞书后台更新事件订阅 URL，并重新发布应用版本。

## 7. 下一步怎么升级

如果你想把它做得更像真正的 Codex/Agent，可以继续加：

1. 会话记忆存储
2. 审批流
3. 白名单用户控制
4. 文件处理
5. 工具调用
6. 接更完整的本地 OpenClaw Gateway，而不是只靠当前会话桥接

## 8. 只接本地会话的最小配置

`.env` 里最少填这些：

```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=your_feishu_app_secret
FEISHU_BACKEND=codex
CODEX_SESSION_TARGET=
CODEX_PYTHON_BIN=python3
CODEX_DESKTOP_BRIDGE_SCRIPT=/Users/mt/Documents/Codex/tools/codex-desktop-bridge/codex_desktop_bridge.py
```

启动后访问：

```bash
curl http://127.0.0.1:3000/health
```

会返回当前实际使用的 `backend`，以及选中的会话或模型。

## 9. 使用硅基流动

如果你想直接走硅基流动，把 `.env` 改成：

```bash
FEISHU_BACKEND=siliconflow
SILICONFLOW_API_KEY=sk-...
SILICONFLOW_MODEL=deepseek-ai/DeepSeek-V3
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
```

注意：

- `SILICONFLOW_BASE_URL` 要保留末尾的 `/v1`
- `SILICONFLOW_MODEL` 需要填硅基流动模型广场里的完整模型名
- 这条路径会走 OpenAI 兼容的 `chat/completions`

## 10. 重要说明

严格说，这不是“飞书页面里嵌了 OpenClaw”。

这是一个**自建飞书机器人桥接服务**，默认把消息转进本地 Codex Desktop 会话。
如果你后面想把它升级成真正的 OpenClaw Gateway，下一步就是把 `codex_desktop_bridge.py` 再替换成你自己的 gateway API。
