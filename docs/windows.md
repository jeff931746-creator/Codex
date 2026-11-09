# Windows 使用说明

工程支持从任意检出目录定位路径；公共 Hook、技能管理和主要工具已提供 Windows 原生入口，同时保留 macOS 入口。当前本地验证环境为 macOS，Windows 与 Linux 的实际执行结果以新增的跨平台 CI 为准；此次没有运行远程 CI。

## 准备与首次运行

安装 Python 3.10+、Git 和 Node.js 22+，并加入 PATH。服务需要的 cloudflared、Ollama、lark-cli、Codex 或 Claude CLI 按实际使用安装。各分析脚本的 Python 依赖仍按所属工具安装；没有要求把所有工具装入同一个环境。

建议检出到较短路径，如 `C:\work\codex-work`，以减少资料库深层目录遇到旧版工具路径长度限制的机会。Git for Windows 可使用 `git -c core.longpaths=true clone <仓库地址> <目标目录>`；支持长路径不代表所有第三方工具都支持同样长度。中文、空格及 `&` 目录有回归覆盖。Hook 配置生成器会拒绝 Python/工程路径中的 `%`、`!`、双引号和换行，避免运行时 Shell 对路径做变量展开；遇到该提示请换用普通目录。

在工程根目录打开 PowerShell：

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
python -X utf8 tools/windows/bootstrap.py --check
python -X utf8 tools/windows/bootstrap.py --runtime codex
```

生成配置位于 `workspace/tmp/runtime-config/codex-hooks.json`。Claude 使用 `--runtime claude`。按运行时支持的方式合并其中的 `hooks` 字段；生成器不会修改用户全局设置。生成文件绑定当前工程及 Python 的绝对路径，搬迁后重新生成。Hook 收到其他工程的 `cwd` 时跳过，避免影响其他工程。若运行时不支持 Hooks，仍须按工程入场约定手动执行检查。

文件修改前的跨平台安全检查：

```powershell
python tools/workspace-guard/check_paths.py README.md workspace/projects
```

守卫允许当前检出目录及系统临时目录，解析父目录和符号链接后的实际路径。Hook 对常见文件工具、Shell 重定向和 PowerShell 文件命令提取路径；它不是完整 Shell 解释器，不能代替操作系统沙箱。动态拼接或编码的脚本必须先显式检查最终目标路径。

## 原生工具入口

| 功能 | 从工程根目录运行 | 依赖或行为 |
|---|---|---|
| 技能检查 | `python archive/skills/scripts/skill_admin.py audit` | Python 标准库 |
| 技能安装 | `python archive/skills/scripts/skill_admin.py install <目标技能目录>` | Windows 默认复制，无需符号链接权限；源更新后需重新安装 |
| 题材库启动 | `python archive/tools/scripts/workflow_tasks.py build-theme` | SiliconFlow 配置；确认后调用付费 API |
| 检查未提交文件 | `python archive/tools/scripts/workflow_tasks.py check-dirty` | Git |
| 审批推送 | `python archive/tools/scripts/workflow_tasks.py approve-push` | 展示内容，交互确认后 push |
| 飞书桥接 | `node archive/tools/services/feishu-codex-bridge/run.mjs` | 先在该服务目录运行 `npm ci` 并配置 `.env` |
| 临时隧道 | `node archive/tools/services/feishu-codex-bridge/run.mjs quick-tunnel` | cloudflared；运行后会向外提供服务访问 |
| 命名隧道 | `node archive/tools/services/feishu-codex-bridge/run.mjs named-tunnel` | cloudflared 及本地隧道配置 |
| 桌面桥接 | `python archive/tools/services/codex-desktop-bridge/codex_desktop_bridge.py --help` | Codex CLI；查看参数后启动 |
| 任务续接 | `python archive/tools/auto-resume/auto_resume.py --help` | Claude CLI；前台有界重试 |
| 日报 | `python archive/tools/services/feishu-digest/daily_digest.py --help` | 显式配置接收人；实际运行会发送消息 |
| Ollama | `python archive/tools/model-tools/gemma4/ollama_tool.py --help` | 已安装的 Ollama；拉模型需网络和磁盘空间 |
| 飞书凭证 | `python archive/skills/skills/feishu-personal-bot-claude/set_oauth_token.py --help` | 隐藏输入或 stdin，避免凭证进入命令历史 |

Windows 开机登录启动桥接的入口是服务目录内的 `install_task.ps1`，需要主动执行才会注册计划任务；此次改造没有注册或启动任务。参见对应服务 README。

共享 API 配置优先使用进程环境变量，再加载配置文件。可用 `CODEX_RUNTIME_ENV_PATH` 指定文件；默认 Windows 路径为 `%LOCALAPPDATA%\FeishuCodexBridge\bridge\.env`，Linux 使用 `$XDG_DATA_HOME/FeishuCodexBridge/bridge/.env`（未设置时为 `~/.local/share/...`），macOS 保留原 Application Support 路径。服务自身 `.env` 与进程环境优先级见服务 README。配置值按文本读取，不执行 Shell 表达式；没有复制任何现有密钥。

## 平台边界

| 功能 | Windows 处理方式 |
|---|---|
| Gemini 网页发送、Chrome AppleScript 操作 | 原脚本为 macOS 专用；Windows 手动提交提示词或使用已有 API 脚本 |
| launchd 与临时 Ollama.app 安装/清理 | macOS 专用；Windows 使用计划任务入口与已安装 Ollama |
| 每日分支自动合并脚本 | 通过 Git Bash 手动运行；会修改分支和工作树，未纳入自动启用 |
| 飞书机器人 `setup.sh`、`add-bot-to-group.sh` | 需要 Git Bash 和上游 bridge；上游 Windows daemon 未验证 |
| 旧工具别名目录 | 改为普通目录和转发脚本；安装、配置、依赖与新增调用使用 `archive/tools/` 下的规范目录 |

历史文档和历史数据中的原机器路径作为记录保留，不作为运行依赖。资料库 17 个含冒号/星号的文件已改为下划线，并同步索引引用。没有更改资料正文结论。

## 验证

```powershell
python -B -m unittest discover -s tests -v
python -B -m unittest discover -s archive/tools/lib/tests -v
python -B -m unittest discover -s archive/tools/repos/breakdown-worker/tests -v
node --test archive/tools/services/feishu-codex-bridge/tests/launch.test.mjs
```

`.github/workflows/windows-compat.yml` 在 Windows、macOS 和 Ubuntu 上运行这些检查，覆盖目录搬迁、中文空格路径、Hook 拦截、npm 参数完整性和模型输出路径安全。检查不调用付费 API、不发送消息，也不启动长期服务；实际登录、计划任务、隧道及模型运行仍需目标机器配置后验证。

本次检查还发现，现有内容规范检查器会把历史题材索引原有的“三角关系”“师生关系”“夫妻关系”等分类标题识别为分析标签，也会把旧 README 中的配置文件名识别为示例文本。这些问题在改造前已存在；没有为清除提示而修改历史分类或放宽检查规则。
