#!/usr/bin/env python3
"""Shared API configuration and HTTP helpers for workspace tools."""

from __future__ import annotations

import gzip
import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

try:
    import certifi
except ImportError:  # pragma: no cover - system Python fallback
    certifi = None


API_BASE_URLS = {
    "siliconflow": "https://api.siliconflow.cn/v1",
    "deepseek": "https://api.deepseek.com",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/models",
    "itunes": "https://itunes.apple.com",
    "steam_store": "https://store.steampowered.com",
    "duckduckgo_html": "https://html.duckduckgo.com",
}


class ApiError(RuntimeError):
    """Raised when a managed API request fails."""


@dataclass(frozen=True)
class ApiResponse:
    status: int
    headers: Any
    text: str

    def json(self) -> Any:
        if not self.text:
            return {}
        return json.loads(self.text)


def ssl_context() -> ssl.SSLContext:
    if certifi is not None:
        return ssl.create_default_context(cafile=certifi.where())
    return ssl.create_default_context()


def api_url(provider: str, path: str = "", query: dict[str, Any] | None = None) -> str:
    if provider not in API_BASE_URLS:
        raise KeyError(f"Unknown API provider: {provider}")
    base = API_BASE_URLS[provider].rstrip("/")
    if path:
        url = f"{base}/{path.lstrip('/')}"
    else:
        url = base
    if query:
        url = f"{url}?{urllib.parse.urlencode(query)}"
    return url


def request(
    provider: str,
    path: str = "",
    *,
    method: str = "GET",
    query: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    json_body: Any | None = None,
    data: bytes | None = None,
    timeout: int = 60,
    url: str | None = None,
) -> ApiResponse:
    target_url = url or api_url(provider, path, query)
    body = data
    request_headers = dict(headers or {})
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")

    req = urllib.request.Request(
        target_url,
        data=body,
        headers=request_headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_context()) as resp:
            return ApiResponse(
                status=resp.status,
                headers=resp.headers,
                text=resp.read().decode("utf-8", errors="ignore"),
            )
    except urllib.error.HTTPError as exc:
        raw_detail = exc.read()
        if exc.headers.get("Content-Encoding", "").lower() == "gzip":
            try:
                raw_detail = gzip.decompress(raw_detail)
            except OSError:
                pass
        detail = raw_detail.decode("utf-8", "ignore")
        raise ApiError(f"{provider} HTTP {exc.code}: {detail[:800]}") from exc
    except urllib.error.URLError as exc:
        raise ApiError(f"{provider} network error: {exc}") from exc


def request_json(provider: str, path: str = "", **kwargs: Any) -> Any:
    return request(provider, path, **kwargs).json()
