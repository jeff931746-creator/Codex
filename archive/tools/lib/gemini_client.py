#!/usr/bin/env python3
"""Shared Google Gemini / Imagen API client."""

from __future__ import annotations

from typing import Any

from archive.tools.lib.api_client import ApiError, env_value, request_json


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
