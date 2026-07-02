---
name: feishu-personal-bot-claude
description: 把飞书（Lark）个人版自建应用机器人接入 Claude Code，实现群内 @机器人 自动回复，并把机器人加进已有群。触发场景：(1) 要让飞书/Lark 机器人接 Claude 或 AI 自动回复；(2) 飞书 bot 接入本地 claude / lark-channel-bridge 配置；(3) 飞书机器人进群、加白名单、调不通 401 或权限问题排查。仅限飞书「个人版」自建应用；企业版另有正常的群机器人入口。
---

# feishu-personal-bot-claude

把飞书个人版自建应用机器人接入本机 Claude Code（经 `lark-channel-bridge` 长连接 daemon），群里 @机器人 即用 Claude 回复。整套含一个一键向导脚本，人工步骤（后台配置、授权）会暂停等待。

## 适用 / 不适用

- 适用：飞书**个人版**账号，想要自己的 AI 机器人在群里答话；要把机器人加进已有群。
- 不适用：企业版（企业版群设置里有正常「群机器人」入口，直接加即可，不必走本流程）。

## 前置依赖

`node`/`npx`、`python3`、`claude` CLI（已登录、能正常对话）、`lark-cli`。可选 `expect`（把 secret 存进 bridge 加密 keystore；没有则用 `--app-secret` 启动，同样可用）。

## 一键接入（推荐）

```bash
bash setup.sh
```

向导覆盖：前置检查 → 引导后台配置（含权限导入）→ 配 lark-cli profile → 修 401 → 起 bridge daemon → 设管理员/白名单。跑完群里 @机器人 即可回复。脚本只自动化命令行步骤，**后台网页操作和凭证输入需你本人完成**。

加机器人进已有群：

```bash
bash add-bot-to-group.sh
```

---

## 分步详解（向导背后做了什么 / 手动执行时照这个来）

约定：默认 `PROFILE=personal`，机器人 App ID 记作 `cli_xxx`。

### Step 1【人工】开发者后台 https://open.feishu.cn/app

1. 创建企业自建应用 → 添加「机器人」能力。
2. **权限管理 → 导入** → 上传本目录 `permissions.json`。**一次性批量开通，免逐个勾选**——逐个勾最容易漏项导致调不通，这是同事踩过的坑。
   - 最小必需子集（懒得用全量时）：tenant 端 `im:message` `im:message:send_as_bot` `im:message.group_at_msg.include_bot:readonly` `im:message.p2p_msg:readonly` `im:chat` `im:chat:readonly` `im:resource`；user 端（仅"加机器人进已有群"需要）`im:chat` `im:chat:read` `im:chat.members:write_only`。
3. 事件与回调 → 订阅方式 = **「使用长连接接收事件」**（这样本机无需公网）。
4. 事件订阅 → 添加 **`im.message.receive_v1`**。
5. 要进外部群 / 和朋友的群：开启**「对外共享能力」**（需个人实名认证）。个人版里你和朋友的群都算外部群，不开则机器人进不去。
6. 版本管理 → 创建版本并发布（个人版免审核自动通过，但**必须发版**才生效）。
7. 凭证与基础信息 → 复制 App ID / App Secret。

### Step 2【自动】配 lark-cli profile

```bash
printf '%s' "<APP_SECRET>" | lark-cli config init --app-id cli_xxx --app-secret-stdin --name personal --brand feishu
# 验证（返回 identity:bot + API 业务错误 = 凭证有效已到 API 层）
lark-cli im chats get --chat-id oc_probe --as bot --profile personal --json
```

### Step 3【自动】修 401（关键）

bridge 由 launchd 当后台 daemon 启动，**不读 `~/.zshrc`**，daemon 里的 claude 拿不到 `ANTHROPIC_AUTH_TOKEN` → 调 API 返回 `401 Invalid credentials`。把认证写进 `~/.claude/settings.json` 的 `env`（claude 不管谁启动都读它）：

```bash
zsh -ic 'python3 inject_env.py'   # 必须登录 shell 才读得到变量
```

### Step 4【自动】起 bridge daemon

```bash
# 可选：secret 存进加密 keystore（需 expect 提供伪终端，secrets set 强制交互）
# 启动 daemon（首次 bootstrap profile 必须给 --app-secret，之后落入加密配置）
npx -y lark-channel-bridge@latest start --profile personal --agent claude \
  --app-id cli_xxx --app-secret "<APP_SECRET>" --workspace <dir> --skip-check-lark-cli
npx -y lark-channel-bridge@latest ps    # 确认进程在跑
```

### Step 5【自动】设管理员 + 白名单

bridge 默认不在任意群响应。`~/.lark-channel/config.json` 的 `profiles.personal.access`：
- `admins`：管理员 open_id 列表，在内者可在群里发 `/invite group` 加白名单；
- `allowedChats`：群白名单；
- `requireMentionInGroup`：群里是否需 @。

把自己 open_id 加进 `admins`、目标群 chat_id 加进 `allowedChats`，然后 `restart --profile personal`。

### Step 6 加机器人进「已有群」（见 add-bot-to-group.sh）

个人版客户端**没有**「加机器人」入口（含外部联系人的群不显示）。绕过办法＝用**你的用户身份**经 API 加（接口要求调用者在群内，你在群里所以可行）：

```bash
lark-cli auth login --scope "im:chat im:chat:read" --no-wait --json --profile personal   # split-flow 授权
lark-cli im +chat-list --as user --profile personal --json        # 列群拿 chat_id（群在 data.chats；勿用 --page-all）
lark-cli im chat.members create --as user --profile personal \
  --chat-id <oc_…> --member-id-type app_id --data '{"id_list":["cli_xxx"]}' --succeed-type 1
```
加完把该群加进白名单（Step 5）。

## 排错速查

| 现象 | 原因 | 处理 |
|---|---|---|
| 机器人回 `401 Invalid authentication credentials` | daemon 没继承 shell 认证 | 跑 Step 3，`restart` |
| 机器人回「当前群尚未加入响应列表」 | 群不在白名单 | Step 5 加 `allowedChats`，或管理员在群发 `/invite group` |
| `/invite group` 提示无权限 | 你不在 `admins` | Step 5 把 open_id 加进 `admins` |
| 启动报「非交互模式缺少 App Secret」 | 首次 bootstrap 必须显式给 secret | 启动带 `--app-secret`（keystore 预存的不用于首次 bootstrap）|
| 列群空 | 用了 `--page-all`（个人版返回空），或字段读错 | 去掉 `--page-all`，读 `data.chats` |
| 客户端找不到「加机器人」入口 | 个人版含外部联系人的群无此入口 | 用 Step 6 的 user 身份 API |
| 加机器人进外部群被拒 | 应用没开对外共享 | Step 1.5 开启对外共享能力 |

## 管理命令

```bash
npx -y lark-channel-bridge@latest status              # 服务状态
npx -y lark-channel-bridge@latest ps                  # 运行中的进程
npx -y lark-channel-bridge@latest restart --profile personal
npx -y lark-channel-bridge@latest stop --profile personal
```

## 安全

- App Secret 不写进任何提交/明文文件；用 stdin 或 `--app-secret "$(读文件)"` 注入，用后删文件。
- 重置 Secret 后同步两处：lark-cli（`config init --app-secret-stdin --name personal`）与 bridge keystore（`secrets set --app-id`）。
- 详细背景、踩坑记录见记忆 `reference_lark_cli_profiles`（本 skill 是操作流程的真相源，背景知识以记忆为准）。
