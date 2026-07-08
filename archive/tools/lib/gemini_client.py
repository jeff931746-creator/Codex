#!/usr/bin/env python3
"""Shared Google Gemini / Imagen API client."""

from __future__ import annotations

import json
from typing import Any, Callable, Iterable

from archive.tools.lib.api_client import ApiError, env_value, request_json
from archive.tools.lib.llm_common import RetryPolicy, call_with_retry


class GeminiError(RuntimeError):
    """Raised when Gemini or Imagen requests fail."""


def get_gemini_api_key(required: bool = True) -> str:
    api_key = env_value("GEMINI_API_KEY", "").strip()
    if required and not api_key:
        raise RuntimeError("GEMINI_API_KEY 未设置")
    return api_key


def generate_content(
    model: str,
    *,
    payload: dict[str, Any],
    api_key: str | None = None,
    timeout: int = 300,
) -> dict[str, Any]:
    key = api_key if api_key is not None else get_gemini_api_key()
    try:
        return request_json(
            "gemini",
            f"{model}:generateContent",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": key,
            },
            json_body=payload,
            timeout=timeout,
        )
    except ApiError as exc:
        raise GeminiError(str(exc)) from exc


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
    chunks: list[str] = []
    for candidate in body.get("candidates", []) or []:
        content = candidate.get("content", {}) if isinstance(candidate, dict) else {}
        for part in content.get("parts", []) or []:
            if isinstance(part, dict) and part.get("text"):
                chunks.append(str(part["text"]).strip())
    if chunks:
        return "\n\n".join(chunks).strip()
    raise GeminiError(f"响应无文本内容: {json.dumps(body, ensure_ascii=False)[:800]}")


def _generation_config(
    *,
    max_tokens: int | None = None,
    temperature: float | None = None,
) -> dict[str, Any] | None:
    config: dict[str, Any] = {}
    if max_tokens is not None:
        config["maxOutputTokens"] = max_tokens
    if temperature is not None:
        config["temperature"] = temperature
    return config or None


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
        raise RuntimeError("Gemini model 必须由 route/model_registry 解析后显式传入")
    if stream:
        raise GeminiError("Gemini stream 暂未在统一 client 中封装")
    system_parts: list[str] = []
    contents: list[dict[str, Any]] = []
    for message in messages:
        role = str(message.get("role", "user"))
        text = _message_text(message.get("content", ""))
        if role == "system":
            system_parts.append(text)
        else:
            contents.append({
                "role": "model" if role == "assistant" else "user",
                "parts": [{"text": text}],
            })
    payload: dict[str, Any] = {"contents": contents}
    if system_parts:
        payload["systemInstruction"] = {
            "parts": [{"text": "\n\n".join(system_parts)}],
        }
    generation_config = _generation_config(
        max_tokens=max_tokens,
        temperature=temperature,
    )
    if generation_config:
        payload["generationConfig"] = generation_config
    if extra:
        payload.update(extra)

    def _call() -> str:
        body = generate_content(
            model,
            payload=payload,
            api_key=api_key,
            timeout=timeout,
        )
        return _extract_text(body)

    return call_with_retry(
        _call,
        retry_policy=retry_policy,
        logger=logger,
        return_empty_on_error=return_empty_on_error,
        error_factory=GeminiError,
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
    if not model:
        raise RuntimeError("Gemini model 必须由 route/model_registry 解析后显式传入")
    parts: list[dict[str, Any]] = [{"text": prompt}]
    for base64_data, media_type in image_data:
        parts.append({
            "inline_data": {
                "mime_type": media_type,
                "data": base64_data,
            },
        })
    payload: dict[str, Any] = {
        "contents": [{"role": "user", "parts": parts}],
    }
    if system:
        payload["systemInstruction"] = {"parts": [{"text": system}]}
    generation_config = _generation_config(
        max_tokens=max_tokens,
        temperature=temperature,
    )
    if generation_config:
        payload["generationConfig"] = generation_config
    if extra:
        payload.update(extra)

    def _call() -> str:
        body = generate_content(model, payload=payload, timeout=timeout)
        return _extract_text(body)

    return call_with_retry(
        _call,
        retry_policy=retry_policy,
        logger=logger,
        return_empty_on_error=return_empty_on_error,
        error_factory=GeminiError,
    )


def predict(
    model: str,
    *,
    payload: dict[str, Any],
    api_key: str | None = None,
    timeout: int = 300,
) -> dict[str, Any]:
    key = api_key if api_key is not None else get_gemini_api_key()
    try:
        return request_json(
            "gemini",
            f"{model}:predict",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": key,
            },
            json_body=payload,
            timeout=timeout,
        )
    except ApiError as exc:
        raise GeminiError(str(exc)) from exc
