#!/usr/bin/env python3
"""Provider-routed LLM client for workspace scripts."""

from __future__ import annotations

from typing import Any, Callable, Iterable  # noqa: F401 – Callable used in type comments

from archive.tools.lib.llm_common import RetryPolicy
from archive.tools.lib.model_registry import (
    MODEL_ROUTE_ALIASES,
    MODEL_ROUTES,
    env_route,
    get_model_route,
)


SUPPORTED_PROVIDERS = {"anthropic", "deepseek", "gemini", "openai", "siliconflow"}
SUPPORTED_ROUTES = set(MODEL_ROUTES) | set(MODEL_ROUTE_ALIASES)

# ---------------------------------------------------------------------------
# 先搜后整：搜索增强分析入口
# ---------------------------------------------------------------------------

_SEARCH_ANALYSIS_SYSTEM = (
    "你是一个严谨的游戏系统分析助手。\n"
    "以下是通过联网搜索获取的原始资料。请只基于这些资料进行分析。\n"
    "规则：\n"
    '1. 只使用以下资料中的信息，不要补充你自己知道的内容。\n'
    '2. 如果资料中没有覆盖某个方面，请明确标注"资料未覆盖"，不要自行填补。\n'
    '3. 每条事实性陈述必须标注来源（引用搜索结果的编号或 URL）。\n'
    '4. 区分"确认不存在"和"资料未提及"：前者需要依据，后者标注"未确认"。'
)


def search_and_analyze(
    search_queries: list[str],
    analysis_prompt: str,
    *,
    system: str | None = None,
    route: str | None = None,
    model_route: str | None = None,
    provider: str | None = None,
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    search_max_results: int = 5,
    search_depth: str = "basic",
    timeout: int = 300,
    retry_policy: "RetryPolicy | None" = None,
    logger: "Callable[[str], None] | None" = None,
    return_empty_on_error: bool = False,
    extra: dict[str, Any] | None = None,
) -> str:
    """先搜后整：用 Tavily 搜索，再把结果喂给 LLM 分析。

    Args:
        search_queries: 搜索关键词列表，会逐个搜索并合并去重。
        analysis_prompt: 分析指令，搜索结果会作为上下文拼接在前面。
        system: 自定义 system prompt。默认使用内置的"先搜后整"规则。
        其余参数同 chat_text。

    Returns:
        LLM 的分析结果文本。
    """
    from archive.tools.lib.tavily_client import multi_search

    # Step 1: 搜索
    search_results = multi_search(
        search_queries,
        max_results=search_max_results,
        search_depth=search_depth,
    )

    # Step 2: 拼接 prompt
    combined_prompt = (
        f"以下是关于该主题的联网搜索资料：\n\n"
        f"{search_results}\n\n"
        f"---\n\n"
        f"{analysis_prompt}"
    )

    # Step 3: 调用 LLM
    return chat_text(
        combined_prompt,
        system=system or _SEARCH_ANALYSIS_SYSTEM,
        route=route,
        model_route=model_route,
        provider=provider,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        timeout=timeout,
        retry_policy=retry_policy,
        logger=logger,
        return_empty_on_error=return_empty_on_error,
        extra=extra,
    )


def get_provider() -> str:
    raise RuntimeError("LLM_PROVIDER 旧入口已移除，请改用 LLM_ROUTE 或 route=")


def get_route() -> str:
    return env_route()


def _resolve_route(
    *,
    route: str | None = None,
    model_route: str | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> tuple[str | None, str | None]:
    """Resolve route-first config."""
    if provider is not None:
        raise ValueError("provider= 旧入口已移除，请改用 route=")
    requested_route = route or model_route
    if requested_route is None:
        requested_route = get_route() or None

    if requested_route is None:
        raise ValueError("LLM_ROUTE 未设置，请在调用处传 route= 或设置 LLM_ROUTE")

    resolved = get_model_route(requested_route)
    return resolved.provider, model or resolved.model


def _implementation(provider: str | None = None):
    if provider is None:
        raise ValueError("provider 只能由 route/model_registry 解析得到")
    resolved = provider.strip().lower()
    if resolved == "siliconflow":
        from archive.tools.lib import siliconflow_client as impl

        return impl
    if resolved == "deepseek":
        from archive.tools.lib import deepseek_client as impl

        return impl
    if resolved == "openai":
        from archive.tools.lib import openai_client as impl

        return impl
    if resolved == "anthropic":
        from archive.tools.lib import anthropic_client as impl

        return impl
    if resolved == "gemini":
        from archive.tools.lib import gemini_client as impl

        return impl
    raise ValueError(
        f"Unsupported LLM provider={resolved!r}. "
        f"Supported providers: {', '.join(sorted(SUPPORTED_PROVIDERS))}"
    )


def chat(
    messages: Iterable[dict[str, Any]],
    *,
    route: str | None = None,
    model_route: str | None = None,
    provider: str | None = None,
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    stream: bool = False,
    timeout: int = 180,
    retry_policy: RetryPolicy | None = None,
    logger: Callable[[str], None] | None = None,
    return_empty_on_error: bool = False,
    extra: dict[str, Any] | None = None,
) -> str:
    resolved_provider, resolved_model = _resolve_route(
        route=route,
        model_route=model_route,
        provider=provider,
        model=model,
    )
    impl = _implementation(resolved_provider)
    return impl.chat(
        messages,
        model=resolved_model,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=stream,
        timeout=timeout,
        retry_policy=retry_policy,
        logger=logger,
        return_empty_on_error=return_empty_on_error,
        extra=extra,
    )


def chat_with_images(
    prompt: str,
    image_data: list[tuple[str, str]],
    *,
    route: str | None = None,
    model_route: str | None = None,
    provider: str | None = None,
    system: str | None = None,
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    timeout: int = 300,
    retry_policy: "RetryPolicy | None" = None,
    logger: "Callable[[str], None] | None" = None,
    return_empty_on_error: bool = False,
    extra: dict[str, Any] | None = None,
) -> str:
    """带图片的 LLM 调用。image_data: [(base64_str, media_type), ...]。"""
    resolved_provider, resolved_model = _resolve_route(
        route=route,
        model_route=model_route,
        provider=provider,
        model=model,
    )
    impl = _implementation(resolved_provider)
    return impl.chat_with_images(
        prompt,
        image_data,
        system=system,
        model=resolved_model,
        max_tokens=max_tokens,
        temperature=temperature,
        timeout=timeout,
        retry_policy=retry_policy,
        logger=logger,
        return_empty_on_error=return_empty_on_error,
        extra=extra,
    )


def chat_text(
    prompt: str,
    *,
    route: str | None = None,
    model_route: str | None = None,
    provider: str | None = None,
    system: str | None = None,
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    stream: bool = False,
    timeout: int = 180,
    retry_policy: RetryPolicy | None = None,
    logger: Callable[[str], None] | None = None,
    return_empty_on_error: bool = False,
    extra: dict[str, Any] | None = None,
) -> str:
    resolved_provider, resolved_model = _resolve_route(
        route=route,
        model_route=model_route,
        provider=provider,
        model=model,
    )
    impl = _implementation(resolved_provider)
    return impl.chat_text(
        prompt,
        system=system,
        model=resolved_model,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=stream,
        timeout=timeout,
        retry_policy=retry_policy,
        logger=logger,
        return_empty_on_error=return_empty_on_error,
        extra=extra,
    )
