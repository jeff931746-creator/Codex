#!/usr/bin/env python3
"""Shared OpenAI Responses API client."""

from __future__ import annotations

import json
from typing import Any, Callable, Iterable

from archive.tools.lib.api_client import ApiError, env_value, request_json
from archive.tools.lib.llm_common import RetryPolicy, call_with_retry


class OpenAIClientError(RuntimeError):
    """Raised when an OpenAI request fails."""


def get_openai_api_key(required: bool = True) -> str:
    api_key = env_value("OPENAI_API_KEY", "").strip()
    if required and not api_key:
        raise RuntimeError("OPENAI_API_KEY 未设置")
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


def _extract_response_text(body: dict[str, Any]) -> str:
    output_text = body.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()
    chunks: list[str] = []
    for item in body.get("output", []) or []:
        for content in item.get("content", []) or []:
            text = content.get("text") if isinstance(content, dict) else None
            if text:
                chunks.append(str(text).strip())
    if chunks:
        return "\n\n".join(chunks).strip()
    raise OpenAIClientError(f"响应无文本内容: {json.dumps(body, ensure_ascii=False)[:800]}")


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
        raise RuntimeError("OpenAI model 必须由 route/model_registry 解析后显式传入")
    if stream:
        raise OpenAIClientError("OpenAI Responses stream 暂未在统一 client 中封装")
    key = api_key if api_key is not None else get_openai_api_key()
    payload: dict[str, Any] = {
        "model": model,
        "input": [
            {
                "role": message.get("role", "user"),
                "content": [{"type": "input_text", "text": _message_text(message.get("content", ""))}],
            }
            for message in messages
        ],
    }
    if max_tokens is not None:
        payload["max_output_tokens"] = max_tokens
    if temperature is not None:
        payload["temperature"] = temperature
    if extra:
        payload.update(extra)

    def _call() -> str:
        try:
            body = request_json(
                "openai",
                "responses",
                method="POST",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                json_body=payload,
                timeout=timeout,
            )
        except ApiError as exc:
            raise OpenAIClientError(str(exc)) from exc
        return _extract_response_text(body)

    return call_with_retry(
        _call,
        retry_policy=retry_policy,
        logger=logger,
        return_empty_on_error=return_empty_on_error,
        error_factory=OpenAIClientError,
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
