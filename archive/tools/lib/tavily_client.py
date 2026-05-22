#!/usr/bin/env python3
"""Tavily Search API client for workspace tools.

Tavily provides web search as a service. Free tier: 1000 credits/month.
Basic search = 1 credit, advanced = 2 credits.

Usage:
    from archive.tools.lib.tavily_client import search

    results = search("寻道大千 灵兽系统 攻略")
    for r in results:
        print(r["title"], r["url"])
        print(r["content"][:200])
"""

from __future__ import annotations

import json
from typing import Any

from archive.tools.lib.api_client import ApiError, env_value, request


class TavilyError(RuntimeError):
    """Raised when a Tavily API request fails."""


def get_api_key(required: bool = True) -> str:
    key = env_value("TAVILY_API_KEY", "").strip()
    if required and not key:
        raise RuntimeError(
            "TAVILY_API_KEY 未设置。请在桥接服务 .env 中添加: "
            "TAVILY_API_KEY=tvly-xxxxx"
        )
    return key


def search(
    query: str,
    *,
    search_depth: str = "basic",
    max_results: int = 5,
    topic: str = "general",
    include_answer: bool = False,
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
    api_key: str | None = None,
    timeout: int = 30,
) -> list[dict[str, Any]]:
    """Search the web via Tavily API.

    Args:
        query: Search query string.
        search_depth: "basic" (1 credit) or "advanced" (2 credits).
        max_results: Number of results to return (1-20).
        topic: "general" or "news".
        include_answer: Whether to include AI-generated answer summary.
        include_domains: Only include results from these domains.
        exclude_domains: Exclude results from these domains.
        api_key: Override TAVILY_API_KEY env var.
        timeout: Request timeout in seconds.

    Returns:
        List of result dicts, each containing:
        - title: str
        - url: str
        - content: str (snippet)
        - score: float (relevance score)
    """
    key = api_key or get_api_key()

    payload: dict[str, Any] = {
        "query": query,
        "search_depth": search_depth,
        "max_results": max_results,
        "topic": topic,
        "include_answer": include_answer,
    }
    if include_domains:
        payload["include_domains"] = include_domains
    if exclude_domains:
        payload["exclude_domains"] = exclude_domains

    try:
        resp = request(
            "tavily",
            "search",
            method="POST",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json_body=payload,
            timeout=timeout,
        )
    except ApiError as exc:
        raise TavilyError(str(exc)) from exc

    try:
        data = json.loads(resp.text)
    except json.JSONDecodeError as exc:
        raise TavilyError(f"响应不是合法 JSON: {resp.text[:500]}") from exc

    return data.get("results", [])


def search_text(
    query: str,
    *,
    max_results: int = 5,
    search_depth: str = "basic",
    **kwargs: Any,
) -> str:
    """Search and return results as formatted text block.

    Convenience wrapper for feeding search results into LLM prompts.
    Returns a string with numbered results, each showing title, URL, and content.
    """
    results = search(
        query,
        max_results=max_results,
        search_depth=search_depth,
        **kwargs,
    )
    if not results:
        return f"[搜索无结果] query: {query}"

    parts = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "无标题")
        url = r.get("url", "")
        content = r.get("content", "")
        parts.append(f"[{i}] {title}\n    URL: {url}\n    {content}")
    return "\n\n".join(parts)


def multi_search(
    queries: list[str],
    *,
    max_results: int = 3,
    search_depth: str = "basic",
    **kwargs: Any,
) -> str:
    """Run multiple searches and combine results into one text block.

    Useful for covering multiple dimensions of a topic (e.g., game systems).
    Deduplicates results by URL.
    """
    seen_urls: set[str] = set()
    all_parts: list[str] = []

    for query in queries:
        results = search(
            query,
            max_results=max_results,
            search_depth=search_depth,
            **kwargs,
        )
        for r in results:
            url = r.get("url", "")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            title = r.get("title", "无标题")
            content = r.get("content", "")
            all_parts.append(f"- {title}\n  URL: {url}\n  {content}")

    if not all_parts:
        return f"[搜索无结果] queries: {queries}"

    return "\n\n".join(all_parts)
