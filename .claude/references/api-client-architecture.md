# API 调用统一底层规则

所有外部 API 调用必须通过统一 API 管理层，不得在业务脚本中直接拼写 endpoint、key、鉴权 header、重试、stream 解析或响应解析逻辑。

## Python

- 通用 HTTP / provider base URL 统一放在 `archive/tools/lib/api_client.py`
- LLM 公共逻辑统一放在 `archive/tools/lib/llm_common.py`
- LLM 业务入口统一使用 `archive/tools/lib/llm_client.py`
- provider 特有逻辑放在对应 client,如 `siliconflow_client.py`、`deepseek_client.py`

## Node

- 通用 HTTP / provider base URL 统一放在 `archive/tools/lib/api-client.mjs`
- provider 特有逻辑放在对应 client,如 `siliconflow-client.mjs`、`deepseek-client.mjs`

## 新增 API 时的工作流

1. 先在统一 provider / base URL 层登记
2. 再新增或扩展 provider client
3. 业务脚本只调用统一 client
4. provider 切换优先通过 `.env`,例如 `LLM_PROVIDER=deepseek`
5. 不允许在业务脚本中新增散落的 API 请求实现

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
export LLM_PROVIDER=deepseek         # 或 siliconflow / gemini,按任务定
# DEEPSEEK_MODEL / SILICONFLOW_MODEL 可选覆盖
python3 业务脚本.py
```

调用方式(业务脚本里只需要这一行):

```python
from archive.tools.lib.llm_client import chat_text
result = chat_text(prompt, system=system_prompt, max_tokens=2000)
```

provider 选型默认:

| 任务类型 | 默认 provider | 默认模型 | 说明 |
|---|---|---|---|
| 深度分析 / 拆解 / 分类判断 | `deepseek` | `deepseek-v4-pro` | 推理质量优先 |
| 快速批量收集 / 列表归类 | `deepseek` | `deepseek-v4-flash` | 速度成本优先 |
| 大批量摘要 / 长文本 | `siliconflow` | `Pro/zai-org/GLM-5.1` | 上下文长 |
| 多模态 / 视觉 | `gemini` | `gemini-2.5-pro` | 图像支持 |
| 联网搜索（先搜后整） | `tavily` | — | 1000 免费 credits/月，basic=1，advanced=2 |

不要把 key 放到业务 `.env`、不要复制到项目目录、不要在脚本里写 fallback 默认值。如果桥接服务 `.env` 缺 key,补到桥接服务那一份,而不是另开一份。

## Key 加载失败的诊断顺序

如果 `chat_text` 抛 `xxx_API_KEY 未设置`,按顺序检查:

1. `echo $DEEPSEEK_API_KEY`(或对应 provider 的 key)是否为空 → 没加载 `.env`
2. 桥接服务 `.env` 是否存在且包含目标 key
3. `LLM_PROVIDER` 是否设置正确 → 默认会走 siliconflow
4. 是否在子 shell 里跑(`bash -c`、`nohup`)→ 子 shell 不继承父 shell 的 export

## 失败模式

| 失败模式 | 表现 | 对策 |
|---|---|---|
| 业务脚本直接拼 endpoint | 出现 `requests.post("https://api.xxx/...")` 或 `fetch("https://...")` | 移到对应 provider client,业务脚本只 import 统一入口 |
| 业务脚本自己写重试循环 | 出现 `for attempt in range(N): try: ... except` | 复用 `llm_common.RetryPolicy` + `call_with_retry` |
| 业务脚本自己解析 stream | 出现散落的 `data: [DONE]` / `data:` 处理 | 复用 `llm_common.parse_stream` |
| provider 切换要改业务脚本代码 | 切 DeepSeek 要 grep 替换 import | 业务脚本统一走 `llm_client`,切换只改 `.env` |
| 新增同类 provider 没登记 base URL | base URL 散落在多处 | 在 `api_client.py` 的 `API_BASE_URLS` 登记 |

## 先搜后整入口

`llm_client.search_and_analyze()` 是"先搜后整"的一站式入口：

```python
from archive.tools.lib.llm_client import search_and_analyze

result = search_and_analyze(
    search_queries=["寻道大千 灵兽系统", "寻道大千 PVP斗法"],
    analysis_prompt="请基于以上资料，列出该游戏的所有战斗相关系统。",
    provider="deepseek",
)
```

流程：Tavily 搜索 → 结果作为上下文 → DeepSeek 分析。搜索结果只存在于 DeepSeek 的一次性上下文中，不占用 Claude 的长期上下文。

## 相关文件

- `archive/tools/lib/api_client.py` — 底层 HTTP + provider base URL 登记
- `archive/tools/lib/llm_common.py` — RetryPolicy / call_with_retry / extract_chat_content / parse_stream
- `archive/tools/lib/llm_client.py` — LLM 统一入口,按 `LLM_PROVIDER` 路由 + `search_and_analyze` 先搜后整入口
- `archive/tools/lib/tavily_client.py` — Tavily 搜索 API 客户端
- `archive/tools/lib/siliconflow_client.py` — SiliconFlow provider 实现
- `archive/tools/lib/deepseek_client.py` — DeepSeek 官方 provider 实现
