# API 调用统一底层规则

所有外部 API 调用必须通过统一 API 管理层，不得在业务脚本中直接拼写 endpoint、key、鉴权 header、重试、stream 解析或响应解析逻辑。

## Python

- 通用 HTTP / provider base URL 统一放在 `archive/tools/lib/api_client.py`
- LLM 公共逻辑统一放在 `archive/tools/lib/llm_common.py`
- 模型入口、provider、模型 ID、key env 的对应关系统一放在 `archive/tools/lib/model_registry.py`
- LLM 业务入口统一使用 `archive/tools/lib/llm_client.py`
- provider 特有逻辑放在对应 client,如 `siliconflow_client.py`、`deepseek_client.py`

## Node

- 通用 HTTP / provider base URL 统一放在 `archive/tools/lib/api-client.mjs`
- provider 特有逻辑放在对应 client,如 `siliconflow-client.mjs`、`deepseek-client.mjs`

## 新增 API 时的工作流

1. 先在统一 provider / base URL 层登记
2. 再新增或扩展 provider client
3. 业务脚本只调用统一 client
4. 模型入口切换优先通过 route,例如 `LLM_ROUTE=DeepSeek_Official_Pro`
5. 不允许在业务脚本中新增散落的 API 请求实现

## 模型入口 Route

route 是业务脚本选择模型的推荐入口。一个 route 必须同时说明：

- 调用哪个 provider / 站点
- 使用哪个模型 ID
- 读取哪个 key env
- 读取哪个 base URL env

route 调用名必须是稳定入口名，不绑定具体模型版本号。具体模型版本只写在 registry 的 `model` 字段中；如果服务商升级模型 ID，只改 registry，不改业务脚本调用名。

同一个模型家族出现在不同站点时，必须登记为不同 route。例如 DeepSeek 官方和 SiliconFlow 上的 DeepSeek 不是同一个入口：

| Route | Provider / 站点 | 模型 ID | Key env | 说明 |
|---|---|---|---|---|
| `DeepSeek_Official_Pro` | `deepseek` | `deepseek-v4-pro` | `DEEPSEEK_API_KEY` | 官方 DeepSeek，质量优先 |
| `DeepSeek_Official_Flash` | `deepseek` | `deepseek-v4-flash` | `DEEPSEEK_API_KEY` | 官方 DeepSeek，快速批量 |
| `SiliconFlow_DeepSeek_Flash` | `siliconflow` | `deepseek-ai/DeepSeek-V4-Flash` | `SILICONFLOW_API_KEY` | SiliconFlow 上的 DeepSeek |
| `SiliconFlow_GLM` | `siliconflow` | `Pro/zai-org/GLM-5.1` | `SILICONFLOW_API_KEY` | SiliconFlow 上的 GLM |
| `SiliconFlow_Kimi` | `siliconflow` | `moonshotai/Kimi-K2.7-Code` | `SILICONFLOW_API_KEY` | SiliconFlow 上的 Kimi,用于中文表达复核 |
| `SiliconFlow_Qwen` | `siliconflow` | `Qwen/Qwen2.5-72B-Instruct` | `SILICONFLOW_API_KEY` | SiliconFlow 上的 Qwen,用于低推理成本收集 |
| `OpenAI_GPT_Mini` | `openai` | `gpt-5-mini` | `OPENAI_API_KEY` | OpenAI 官方入口 |
| `Anthropic_Claude_Haiku` | `anthropic` | `claude-3-5-haiku-latest` | `ANTHROPIC_API_KEY` | Anthropic 官方轻量入口 |
| `Anthropic_Claude_Opus` | `anthropic` | `claude-opus-4-7` | `ANTHROPIC_API_KEY` | Anthropic 官方高强度文本入口 |
| `Google_Gemini_Pro` | `gemini` | `gemini-2.5-pro` | `GEMINI_API_KEY` | Google Gemini 入口 |

route 的唯一登记来源是 `archive/tools/lib/model_registry.py`，Node 侧镜像为 `archive/tools/lib/model-registry.mjs`。如果服务商的模型 ID 变化，改 registry，不在 `.env` 里加模型字段。历史版本化 route 可保留为 alias，但业务脚本和文档示例必须使用稳定调用名。

强制规则：业务脚本必须显式传入 `route=` / `model_route=`，或在启动环境中设置 `LLM_ROUTE`。不要再使用 `LLM_PROVIDER` 或 `*_MODEL` 控制模型选择。

## Key 加载与启动协议

所有需要 API key 的脚本启动前必须从桥接服务 runtime `.env` 加载,不允许在业务脚本里 hard-code key,也不允许把 key 写入业务 `.env`。

桥接服务 runtime `.env` 路径：

```
$HOME/Library/Application Support/FeishuCodexBridge/bridge/.env
```

启动协议(三步):

```bash
set -a
source "$HOME/Library/Application Support/FeishuCodexBridge/bridge/.env"
set +a
export LLM_ROUTE=DeepSeek_Official_Pro
python3 业务脚本.py
```

调用方式(业务脚本里只需要这一行):

```python
from archive.tools.lib.llm_client import chat_text
result = chat_text(prompt, system=system_prompt, max_tokens=2000)
```

需要指定入口时，在调用处显式写 route:

```python
from archive.tools.lib.llm_client import chat_text

result = chat_text(
    prompt,
    system=system_prompt,
    route="SiliconFlow_DeepSeek_Flash",
    max_tokens=2000,
)
```

route 选型默认:

| 任务类型 | 默认 route | Provider / 站点 | 说明 |
|---|---|---|---|
| 深度分析 / 拆解 / 分类判断 | `DeepSeek_Official_Pro` | DeepSeek 官方 | 推理质量优先 |
| 快速批量收集 / 列表归类 | `DeepSeek_Official_Flash` | DeepSeek 官方 | 速度成本优先 |
| DeepSeek 走 SiliconFlow | `SiliconFlow_DeepSeek_Flash` | SiliconFlow | 和官方入口分开管理 key 与模型 ID |
| 大批量摘要 / 长文本 | `SiliconFlow_GLM` | SiliconFlow | 上下文长 |
| 中文表达复核 | `SiliconFlow_Kimi` | SiliconFlow | 只做中文措辞质量复核 |
| 低推理成本收集 | `SiliconFlow_Qwen` | SiliconFlow | 批量列举、列表收集 |
| 多模态 / 视觉 | `Google_Gemini_Pro` | Gemini | 图像支持 |
| 联网搜索（先搜后整） | 暂走 provider client | Tavily | 1000 免费 credits/月，basic=1，advanced=2 |

不要把 key 放到业务 `.env`、不要复制到项目目录、不要在脚本里写 fallback 默认值。如果桥接服务 `.env` 缺 key,补到桥接服务那一份,而不是另开一份。

## Key 加载失败的诊断顺序

如果 `chat_text` 抛 `xxx_API_KEY 未设置`,按顺序检查:

1. `LLM_ROUTE` 是否指向目标入口,例如 `DeepSeek_Official_Pro` 或 `SiliconFlow_DeepSeek_Flash`
2. 用 `python3 archive/tools/scripts/list_llm_routes.py` 看 route 对应 key env 是否为 `configured`
3. 桥接服务 `.env` 是否存在且包含目标 key
4. 是否在子 shell 里跑(`bash -c`、`nohup`)→ 子 shell 不继承父 shell 的 export

## 失败模式

| 失败模式 | 表现 | 对策 |
|---|---|---|
| 业务脚本直接拼 endpoint | 出现 `requests.post("https://api.xxx/...")` 或 `fetch("https://...")` | 移到对应 provider client,业务脚本只 import 统一入口 |
| 模型家族和供应站点混在一起 | `deepseek` 有时读官方 key,有时读 SiliconFlow key | 在 `model_registry.py` 登记成不同 route,业务脚本选择 route |
| 业务脚本自己写重试循环 | 出现 `for attempt in range(N): try: ... except` | 复用 `llm_common.RetryPolicy` + `call_with_retry` |
| 业务脚本自己解析 stream | 出现散落的 `data: [DONE]` / `data:` 处理 | 复用 `llm_common.parse_stream` |
| provider 切换要改业务脚本代码 | 切 DeepSeek 要 grep 替换 import | 业务脚本统一走 `llm_client`,切换 route |
| 新增同类 provider 没登记 base URL | base URL 散落在多处 | 在 `api_client.py` 的 `API_BASE_URLS` 登记 |

## 先搜后整入口

`llm_client.search_and_analyze()` 是"先搜后整"的一站式入口：

```python
from archive.tools.lib.llm_client import search_and_analyze

result = search_and_analyze(
    search_queries=["寻道大千 灵兽系统", "寻道大千 PVP斗法"],
    analysis_prompt="请基于以上资料，列出该游戏的所有战斗相关系统。",
    route="DeepSeek_Official_Pro",
)
```

流程：Tavily 搜索 → 结果作为上下文 → DeepSeek 分析。搜索结果只存在于 DeepSeek 的一次性上下文中，不占用 Claude 的长期上下文。

## 相关文件

- `archive/tools/lib/api_client.py` — 底层 HTTP + provider base URL 登记
- `archive/tools/lib/llm_common.py` — RetryPolicy / call_with_retry / extract_chat_content / parse_stream
- `archive/tools/lib/model_registry.py` — LLM route / provider / model / key env 登记
- `archive/tools/lib/llm_client.py` — LLM 统一入口,按 `LLM_ROUTE` / `route=` 路由
- `archive/tools/scripts/list_llm_routes.py` — 安全列出 route 与 key env 是否配置,不打印 key 值
- `archive/tools/lib/tavily_client.py` — Tavily 搜索 API 客户端
- `archive/tools/lib/siliconflow_client.py` — SiliconFlow provider 实现
- `archive/tools/lib/deepseek_client.py` — DeepSeek 官方 provider 实现
