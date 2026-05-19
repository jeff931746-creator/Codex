#!/usr/bin/env python3
"""Shared LLM helpers for provider clients."""

from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class RetryPolicy:
    retries: int = 3
    base_delay: float = 2.0
    long_retry_after_attempt: int | None = None
    long_delay_range: tuple[int, int] = (300, 600)

    def delay_for(self, attempt: int) -> float:
        if (
            self.long_retry_after_attempt is not None
            and attempt >= self.long_retry_after_attempt
        ):
            return float(random.randint(*self.long_delay_range))
        return self.base_delay * attempt


def call_with_retry(
    fn: Callable[[], str],
    *,
    retry_policy: RetryPolicy | None = None,
    logger: Callable[[str], None] | None = None,
    return_empty_on_error: bool = False,
    error_factory: Callable[[str], Exception] = RuntimeError,
) -> str:
    attempts = retry_policy.retries if retry_policy else 1
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except Exception as exc:
            last_error = exc
            if logger:
                logger(f"LLM 调用失败 (attempt {attempt}/{attempts}): {exc}")
            if retry_policy and attempt < attempts:
                delay = retry_policy.delay_for(attempt)
                if logger:
                    logger(f"  等待 {int(delay)}s 后重试...")
                time.sleep(delay)

    if return_empty_on_error:
        return ""
    raise error_factory(str(last_error) if last_error else "LLM request failed")


def extract_chat_content(body: dict[str, Any]) -> str:
    try:
        message = body["choices"][0]["message"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError(f"响应结构异常: {json.dumps(body, ensure_ascii=False)[:800]}") from exc

    content = message.get("content") or message.get("reasoning_content") or ""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        return "\n\n".join(
            str(item.get("text", "")).strip()
            for item in content
            if isinstance(item, dict) and item.get("text")
        ).strip()
    raise ValueError(f"响应内容异常: {json.dumps(body, ensure_ascii=False)[:800]}")


def parse_stream(text: str) -> str:
    chunks: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line == "data: [DONE]" or not line.startswith("data: "):
            continue
        try:
            obj = json.loads(line[6:])
            delta = obj["choices"][0]["delta"].get("content", "")
        except Exception:
            continue
        if delta:
            chunks.append(delta)
    return "".join(chunks).strip()
