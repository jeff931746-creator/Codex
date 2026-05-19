#!/usr/bin/env python3
"""Provider-routed LLM client for workspace scripts."""

from __future__ import annotations

import os
from typing import Any, Callable, Iterable

from archive.tools.lib.llm_common import RetryPolicy


SUPPORTED_PROVIDERS = {"siliconflow", "deepseek"}


def get_provider() -> str:
    return os.environ.get("LLM_PROVIDER", "siliconflow").strip().lower() or "siliconflow"


def _implementation(provider: str | None = None):
    resolved = (provider or get_provider()).strip().lower()
    if resolved == "siliconflow":
        from archive.tools.lib import siliconflow_client as impl

        return impl
    if resolved == "deepseek":
        from archive.tools.lib import deepseek_client as impl

        return impl
    raise ValueError(
        f"Unsupported LLM_PROVIDER={resolved!r}. "
        f"Supported providers: {', '.join(sorted(SUPPORTED_PROVIDERS))}"
    )


def chat(
    messages: Iterable[dict[str, Any]],
    *,
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
    impl = _implementation(provider)
    return impl.chat(
        messages,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=stream,
        timeout=timeout,
        retry_policy=retry_policy,
        logger=logger,
        return_empty_on_error=return_empty_on_error,
        extra=extra,
    )


def chat_text(
    prompt: str,
    *,
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
    impl = _implementation(provider)
    return impl.chat_text(
        prompt,
        system=system,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=stream,
        timeout=timeout,
        retry_policy=retry_policy,
        logger=logger,
        return_empty_on_error=return_empty_on_error,
        extra=extra,
    )
