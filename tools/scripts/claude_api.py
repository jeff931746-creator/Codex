"""
Claude API 工具函数
用法：
  from tools.claude_api import ask, stream
  或直接运行：python3 tools/claude_api.py "你的问题"
"""

import os
import sys
import anthropic

MODEL = "claude-opus-4-7"
client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_AUTH_TOKEN") or os.getenv("ANTHROPIC_API_KEY"),
    base_url=os.getenv("ANTHROPIC_BASE_URL") or None,
)


def _thinking_config(max_tokens: int) -> dict | None:
    """Return a thinking config that is always below the output token budget."""
    if max_tokens < 2048:
        return None
    return {"type": "adaptive", "budget_tokens": min(8000, max_tokens // 2)}


def _usage_int(value) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def log_usage(usage, label: str) -> None:
    """打印 Claude token 用量日志。"""
    if not usage:
        return

    input_tokens = _usage_int(getattr(usage, "input_tokens", 0))
    output_tokens = _usage_int(getattr(usage, "output_tokens", 0))
    cache_creation_tokens = _usage_int(getattr(usage, "cache_creation_input_tokens", 0))
    cache_read_tokens = _usage_int(getattr(usage, "cache_read_input_tokens", 0))
    print(
        "[usage] anthropic "
        f"label={label} "
        f"model={MODEL} "
        f"input_tokens={input_tokens} "
        f"output_tokens={output_tokens} "
        f"total_tokens={input_tokens + output_tokens} "
        f"cache_creation_input_tokens={cache_creation_tokens} "
        f"cache_read_input_tokens={cache_read_tokens}",
        file=sys.stderr,
    )


def ask(prompt: str, system: str = "", max_tokens: int = 4096) -> str:
    """单次调用，返回完整文本。"""
    messages = [{"role": "user", "content": prompt}]
    params = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    thinking = _thinking_config(max_tokens)
    if thinking:
        params["thinking"] = thinking
    if system:
        params["system"] = [
            {"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}
        ]

    try:
        response = client.messages.create(**params)
    except anthropic.APIError as e:
        print(f"[error] Claude API 调用失败: {e}", file=sys.stderr)
        return ""
    log_usage(response.usage, "claude_api.ask")
    return next((b.text for b in response.content if b.type == "text"), "")


def stream(prompt: str, system: str = "", max_tokens: int = 16000) -> str:
    """流式调用，实时打印输出，返回完整文本。"""
    messages = [{"role": "user", "content": prompt}]
    params = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    thinking = _thinking_config(max_tokens)
    if thinking:
        params["thinking"] = thinking
    if system:
        params["system"] = [
            {"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}
        ]

    chunks = []
    with client.messages.stream(**params) as s:
        for text in s.text_stream:
            print(text, end="", flush=True)
            chunks.append(text)
        final_message = s.get_final_message()
    log_usage(final_message.usage, "claude_api.stream")
    print()
    return "".join(chunks)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 tools/claude_api.py <prompt> [--stream]")
        sys.exit(1)

    prompt = sys.argv[1]
    use_stream = "--stream" in sys.argv

    if not (os.getenv("ANTHROPIC_AUTH_TOKEN") or os.getenv("ANTHROPIC_API_KEY")):
        print("错误: 请先设置 ANTHROPIC_AUTH_TOKEN 或 ANTHROPIC_API_KEY 环境变量")
        sys.exit(1)

    if use_stream:
        stream(prompt)
    else:
        print(ask(prompt))
