#!/usr/bin/env python3
"""Shared SiliconFlow API client for workspace tools."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable, Iterable

from archive.tools.lib.api_client import API_BASE_URLS, ApiError, env_value, request
from archive.tools.lib.llm_common import (
    RetryPolicy,
    call_with_retry,
    extract_chat_content,
    parse_stream,
)


DEFAULT_BASE_URL = API_BASE_URLS["siliconflow"]
class SiliconFlowError(RuntimeError):
    """Raised when the SiliconFlow request fails or returns invalid data."""


def ensure_repo_import_path(current_file: str | Path) -> None:
    """Allow scripts under archive/tools/** to import archive.tools.lib."""
    path = Path(current_file).resolve()
    for parent in [path.parent, *path.parents]:
        if (parent / "archive" / "tools" / "lib").is_dir():
            root = str(parent)
            if root not in sys.path:
                sys.path.insert(0, root)
            return


def get_api_key(required: bool = True) -> str:
    api_key = env_value("SILICONFLOW_API_KEY", "").strip()
    if required and not api_key:
        raise RuntimeError("SILICONFLOW_API_KEY 未设置")
    return api_key


def get_base_url() -> str:
    return env_value("SILICONFLOW_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def get_model() -> str:
    raise RuntimeError("SiliconFlow model 必须由 route/model_registry 解析后显式传入")


def _request_json(
    payload: dict[str, Any],
    *,
    api_key: str,
    base_url: str,
    timeout: int,
    stream: bool,
) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    try:
        response = request(
            "siliconflow",
            "chat/completions",
            method="POST",
            headers=headers,
            json_body=payload,
            timeout=timeout,
            url=f"{base_url.rstrip('/')}/chat/completions",
        )
        if stream:
            return parse_stream(response.text)
        body = json.loads(response.text)
    except ApiError as exc:
        raise SiliconFlowError(str(exc)) from exc
    except Exception as exc:
        raise SiliconFlowError(str(exc)) from exc

    try:
        return extract_chat_content(body)
    except ValueError as exc:
        raise SiliconFlowError(str(exc)) from exc


def chat(
    messages: Iterable[dict[str, str]],
    *,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    max_tokens: int | None = 4096,
    temperature: float | None = 0.3,
    timeout: int = 180,
    stream: bool = False,
    retry_policy: RetryPolicy | None = None,
    logger: Callable[[str], None] | None = None,
    return_empty_on_error: bool = False,
    extra: dict[str, Any] | None = None,
) -> str:
    resolved_key = api_key if api_key is not None else get_api_key(required=True)
    resolved_base_url = base_url or get_base_url()
    resolved_model = model or get_model()

    payload: dict[str, Any] = {
        "model": resolved_model,
        "messages": list(messages),
    }
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    if temperature is not None:
        payload["temperature"] = temperature
    if stream:
        payload["stream"] = True
    if extra:
        payload.update(extra)

    return call_with_retry(
        lambda: _request_json(
            payload,
            api_key=resolved_key,
            base_url=resolved_base_url,
            timeout=timeout,
            stream=stream,
        ),
        retry_policy=retry_policy,
        logger=logger,
        return_empty_on_error=return_empty_on_error,
        error_factory=SiliconFlowError,
    )


def chat_text(
    prompt: str,
    *,
    system: str | None = None,
    model: str | None = None,
    max_tokens: int | None = 4096,
    temperature: float | None = 0.3,
    timeout: int = 180,
    stream: bool = False,
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
        timeout=timeout,
        stream=stream,
        retry_policy=retry_policy,
        logger=logger,
        return_empty_on_error=return_empty_on_error,
        extra=extra,
    )
