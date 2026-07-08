#!/usr/bin/env python3
"""Shared Anthropic Messages API client."""

from __future__ import annotations

import json
from typing import Any, Callable, Iterable

from archive.tools.lib.api_client import ApiError, env_value, request_json
from archive.tools.lib.llm_common import RetryPolicy, call_with_retry


class AnthropicClientError(RuntimeError):
    """Raised when an Anthropic request fails."""


def get_anthropic_api_key(required: bool = True) -> str:
    api_key = env_value("ANTHROPIC_API_KEY", "").strip()
    if required and not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY 未设置")
    return api_key


def _message_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("content") or ""))
            else:
                parts.append(str(item))
        return "\n".join(part for part in parts if part)
    return str(content)


def _extract_text(body: dict[str, Any]) -> str:
    chunks = [
        str(item.get("text", "")).strip()
        for item in body.get("content", []) or []
        if isinstance(item, dict) and item.get("type") == "text" and item.get("text")
    ]
    if chunks:
        return "\n\n".join(chunks).strip()
    raise AnthropicClientError(f"响应无文本内容: {json.dumps(body, ensure_ascii=False)[:800]}")


def chat(
    messages: Iterable[dict[str, Any]],
    *,
    model: str | None = None,
    api_key: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    stream: bool = False,
    timeout: int = 180,
    retry_policy: RetryPolicy | None = None,
    logger: Callable[[str], None] | None = None,
    return_empty_on_error: bool = False,
    extra: dict[str, Any] | None = None,
) -> str:
    if not model:
        raise RuntimeError("Anthropic model 必须由 route/model_registry 解析后显式传入")
    if stream:
        raise AnthropicClientError("Anthropic stream 暂未在统一 client 中封装")
    key = api_key if api_key is not None else get_anthropic_api_key()
    system_parts: list[str] = []
    api_messages: list[dict[str, str]] = []
    for message in messages:
        role = str(message.get("role", "user"))
        text = _message_text(message.get("content", ""))
        if role == "system":
            system_parts.append(text)
        else:
            api_messages.append({
                "role": "assistant" if role == "assistant" else "user",
                "content": text,
            })
    payload: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens or 1024,
        "messages": api_messages,
    }
    if system_parts:
        payload["system"] = "\n\n".join(system_parts)
    if temperature is not None:
        payload["temperature"] = temperature
    if extra:
        payload.update(extra)

    def _call() -> str:
        try:
            body = request_json(
                "anthropic",
                "messages",
                method="POST",
                headers={
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json_body=payload,
                timeout=timeout,
            )
        except ApiError as exc:
            raise AnthropicClientError(str(exc)) from exc
        return _extract_text(body)

    return call_with_retry(
        _call,
        retry_policy=retry_policy,
        logger=logger,
        return_empty_on_error=return_empty_on_error,
        error_factory=AnthropicClientError,
    )


def chat_text(
    prompt: str,
    *,
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
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return chat(
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
