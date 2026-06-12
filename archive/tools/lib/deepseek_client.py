#!/usr/bin/env python3
"""Shared DeepSeek official API client."""

from __future__ import annotations

import json
from typing import Any, Callable, Iterable

from archive.tools.lib.api_client import ApiError, env_value, request
from archive.tools.lib.llm_common import (
    RetryPolicy,
    call_with_retry,
    extract_chat_content,
    parse_stream,
)


DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-pro"


class DeepSeekError(RuntimeError):
    """Raised when the DeepSeek official API request fails."""


def get_deepseek_api_key(required: bool = True) -> str:
    api_key = env_value("DEEPSEEK_API_KEY", "").strip()
    if required and not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY 未设置")
    return api_key


def get_deepseek_model(default: str = DEFAULT_DEEPSEEK_MODEL) -> str:
    return env_value("DEEPSEEK_MODEL", default)


def chat(
    messages: Iterable[dict[str, Any]],
    *,
    model: str | None = None,
    api_key: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    thinking: dict[str, Any] | None = None,
    stream: bool = False,
    timeout: int = 300,
    extra: dict[str, Any] | None = None,
    retry_policy: RetryPolicy | None = None,
    logger: Callable[[str], None] | None = None,
    return_empty_on_error: bool = False,
) -> str:
    key = api_key if api_key is not None else get_deepseek_api_key()
    payload = build_chat_payload(
        messages,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        thinking=thinking,
        stream=stream,
        extra=extra,
    )
    if stream:
        payload["stream"] = True

    return call_with_retry(
        lambda: _request_chat(payload, api_key=key, stream=stream, timeout=timeout),
        retry_policy=retry_policy,
        logger=logger,
        return_empty_on_error=return_empty_on_error,
        error_factory=DeepSeekError,
    )


def _request_chat(
    payload: dict[str, Any],
    *,
    api_key: str,
    stream: bool,
    timeout: int,
) -> str:
    try:
        response = request(
            "deepseek",
            "chat/completions",
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json_body=payload,
            timeout=timeout,
        )
    except ApiError as exc:
        raise DeepSeekError(str(exc)) from exc

    if stream:
        return parse_stream(response.text)
    try:
        return extract_chat_content(json.loads(response.text))
    except json.JSONDecodeError as exc:
        raise DeepSeekError(f"响应不是合法 JSON: {response.text[:800]}") from exc
    except ValueError as exc:
        raise DeepSeekError(str(exc)) from exc


def build_chat_payload(
    messages: Iterable[dict[str, Any]],
    *,
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    thinking: dict[str, Any] | None = None,
    stream: bool = False,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model or get_deepseek_model(),
        "messages": list(messages),
    }
    if stream:
        payload["stream"] = True
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    if temperature is not None:
        payload["temperature"] = temperature
    if thinking is not None:
        payload["thinking"] = thinking
    if extra:
        payload.update(extra)
    return payload


def chat_with_images(
    prompt: str,
    image_data: list[tuple[str, str]],
    *,
    system: str | None = None,
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    timeout: int = 300,
    retry_policy: RetryPolicy | None = None,
    logger: Callable[[str], None] | None = None,
    return_empty_on_error: bool = False,
    extra: dict[str, Any] | None = None,
) -> str:
    """发送带图片的 prompt 到 DeepSeek Vision。

    Args:
        prompt: 文本指令。
        image_data: [(base64_str, media_type), ...] 列表。
            media_type 如 "image/jpeg"、"image/png"。
    """
    messages: list[dict[str, Any]] = []
    if system:
        messages.append({"role": "system", "content": system})

    content: list[dict[str, Any]] = []
    for b64, mime in image_data:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{b64}"},
        })
    content.append({"type": "text", "text": prompt})
    messages.append({"role": "user", "content": content})

    return chat(
        messages,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        thinking={"type": "disabled"},
        timeout=timeout,
        retry_policy=retry_policy,
        logger=logger,
        return_empty_on_error=return_empty_on_error,
        extra=extra,
    )


def chat_text(
    prompt: str,
    *,
    system: str | None = None,
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    thinking: dict[str, Any] | None = None,
    stream: bool = False,
    timeout: int = 300,
    retry_policy: RetryPolicy | None = None,
    logger: Callable[[str], None] | None = None,
    return_empty_on_error: bool = False,
    extra: dict[str, Any] | None = None,
) -> str:
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resolved_thinking = thinking if thinking is not None else {"type": "disabled"}
    return chat(
        messages,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        thinking=resolved_thinking,
        stream=stream,
        timeout=timeout,
        retry_policy=retry_policy,
        logger=logger,
        return_empty_on_error=return_empty_on_error,
        extra=extra,
    )
