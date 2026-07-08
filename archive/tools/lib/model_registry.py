#!/usr/bin/env python3
"""Central model route registry for workspace LLM calls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from archive.tools.lib.api_client import env_value


@dataclass(frozen=True)
class ModelRoute:
    """A concrete model entrypoint: provider site, model id, and managed key."""

    route: str
    provider: str
    model: str
    key_env: str
    base_url_env: str
    description: str = ""


MODEL_ROUTES: dict[str, ModelRoute] = {
    "DeepSeek_Official_Pro": ModelRoute(
        route="DeepSeek_Official_Pro",
        provider="deepseek",
        model="deepseek-v4-pro",
        key_env="DEEPSEEK_API_KEY",
        base_url_env="DEEPSEEK_BASE_URL",
        description="DeepSeek 官方入口，适合质量优先的分析任务。",
    ),
    "DeepSeek_Official_Flash": ModelRoute(
        route="DeepSeek_Official_Flash",
        provider="deepseek",
        model="deepseek-v4-flash",
        key_env="DEEPSEEK_API_KEY",
        base_url_env="DEEPSEEK_BASE_URL",
        description="DeepSeek 官方入口，适合快速批量任务。",
    ),
    "SiliconFlow_DeepSeek_Flash": ModelRoute(
        route="SiliconFlow_DeepSeek_Flash",
        provider="siliconflow",
        model="deepseek-ai/DeepSeek-V4-Flash",
        key_env="SILICONFLOW_API_KEY",
        base_url_env="SILICONFLOW_BASE_URL",
        description="SiliconFlow 上的 DeepSeek 模型，和官方入口分开管理。",
    ),
    "SiliconFlow_GLM": ModelRoute(
        route="SiliconFlow_GLM",
        provider="siliconflow",
        model="Pro/zai-org/GLM-5.1",
        key_env="SILICONFLOW_API_KEY",
        base_url_env="SILICONFLOW_BASE_URL",
        description="SiliconFlow 上的 GLM，适合长文本中文摘要。",
    ),
    "SiliconFlow_Kimi": ModelRoute(
        route="SiliconFlow_Kimi",
        provider="siliconflow",
        model="moonshotai/Kimi-K2.7-Code",
        key_env="SILICONFLOW_API_KEY",
        base_url_env="SILICONFLOW_BASE_URL",
        description="SiliconFlow 上的 Kimi，用于中文表达复核。",
    ),
    "SiliconFlow_Qwen": ModelRoute(
        route="SiliconFlow_Qwen",
        provider="siliconflow",
        model="Qwen/Qwen2.5-72B-Instruct",
        key_env="SILICONFLOW_API_KEY",
        base_url_env="SILICONFLOW_BASE_URL",
        description="SiliconFlow 上的 Qwen2.5 72B，用于低推理成本收集任务。",
    ),
    "OpenAI_GPT_Mini": ModelRoute(
        route="OpenAI_GPT_Mini",
        provider="openai",
        model="gpt-5-mini",
        key_env="OPENAI_API_KEY",
        base_url_env="OPENAI_BASE_URL",
        description="OpenAI 官方入口，适合飞书桥接的轻量回复。",
    ),
    "Anthropic_Claude_Haiku": ModelRoute(
        route="Anthropic_Claude_Haiku",
        provider="anthropic",
        model="claude-3-5-haiku-latest",
        key_env="ANTHROPIC_API_KEY",
        base_url_env="ANTHROPIC_BASE_URL",
        description="Anthropic 官方入口，适合飞书桥接的轻量回复。",
    ),
    "Anthropic_Claude_Opus": ModelRoute(
        route="Anthropic_Claude_Opus",
        provider="anthropic",
        model="claude-opus-4-7",
        key_env="ANTHROPIC_API_KEY",
        base_url_env="ANTHROPIC_BASE_URL",
        description="Anthropic 官方入口，适合高强度文本任务。",
    ),
    "Google_Gemini_Pro": ModelRoute(
        route="Google_Gemini_Pro",
        provider="gemini",
        model="gemini-2.5-pro",
        key_env="GEMINI_API_KEY",
        base_url_env="GEMINI_BASE_URL",
        description="Google Gemini 入口，适合长上下文或多模态任务。",
    ),
}


MODEL_ROUTE_ALIASES: dict[str, str] = {
    "deepseek_official_pro": "DeepSeek_Official_Pro",
    "deepseek-official-pro": "DeepSeek_Official_Pro",
    "deepseek-official": "DeepSeek_Official_Pro",
    "deepseek-v4-pro": "DeepSeek_Official_Pro",
    "deepseek.official.v4-pro": "DeepSeek_Official_Pro",
    "deepseek_official_flash": "DeepSeek_Official_Flash",
    "deepseek-official-flash": "DeepSeek_Official_Flash",
    "deepseek-flash": "DeepSeek_Official_Flash",
    "deepseek.official.v4-flash": "DeepSeek_Official_Flash",
    "siliconflow_deepseek_flash": "SiliconFlow_DeepSeek_Flash",
    "siliconflow-deepseek-flash": "SiliconFlow_DeepSeek_Flash",
    "deepseek-sf": "SiliconFlow_DeepSeek_Flash",
    "deepseek.siliconflow.v4-flash": "SiliconFlow_DeepSeek_Flash",
    "siliconflow_glm": "SiliconFlow_GLM",
    "siliconflow-glm": "SiliconFlow_GLM",
    "glm": "SiliconFlow_GLM",
    "glm-5.1": "SiliconFlow_GLM",
    "glm.siliconflow.5.1": "SiliconFlow_GLM",
    "siliconflow_kimi": "SiliconFlow_Kimi",
    "siliconflow-kimi": "SiliconFlow_Kimi",
    "kimi": "SiliconFlow_Kimi",
    "siliconflow_qwen": "SiliconFlow_Qwen",
    "siliconflow-qwen": "SiliconFlow_Qwen",
    "qwen": "SiliconFlow_Qwen",
    "qwen-72b": "SiliconFlow_Qwen",
    "qwen.siliconflow.qwen2.5-72b": "SiliconFlow_Qwen",
    "openai_gpt_mini": "OpenAI_GPT_Mini",
    "openai-gpt-mini": "OpenAI_GPT_Mini",
    "openai": "OpenAI_GPT_Mini",
    "gpt-mini": "OpenAI_GPT_Mini",
    "gpt-5-mini": "OpenAI_GPT_Mini",
    "openai.official.gpt-5-mini": "OpenAI_GPT_Mini",
    "anthropic_claude_haiku": "Anthropic_Claude_Haiku",
    "anthropic-claude-haiku": "Anthropic_Claude_Haiku",
    "anthropic": "Anthropic_Claude_Haiku",
    "claude-haiku": "Anthropic_Claude_Haiku",
    "anthropic.official.claude-3.5-haiku": "Anthropic_Claude_Haiku",
    "anthropic_claude_opus": "Anthropic_Claude_Opus",
    "anthropic-claude-opus": "Anthropic_Claude_Opus",
    "claude-opus": "Anthropic_Claude_Opus",
    "anthropic.official.claude-opus-4.7": "Anthropic_Claude_Opus",
    "google_gemini_pro": "Google_Gemini_Pro",
    "google-gemini-pro": "Google_Gemini_Pro",
    "gemini": "Google_Gemini_Pro",
    "gemini-pro": "Google_Gemini_Pro",
    "gemini-2.5-pro": "Google_Gemini_Pro",
    "gemini.google.2.5-pro": "Google_Gemini_Pro",
}


def canonical_route_name(route: str) -> str:
    """Return the canonical route id for a route or alias."""
    requested = route.strip()
    if requested in MODEL_ROUTES:
        return requested
    normalized = requested.lower()
    return MODEL_ROUTE_ALIASES.get(normalized, normalized)


def env_route() -> str:
    """Return the route requested by the current environment, if any."""
    return env_value("LLM_ROUTE", "").strip()


def get_model_route(route: str) -> ModelRoute:
    """Resolve a route id or alias to a concrete model route."""
    canonical = canonical_route_name(route)
    try:
        return MODEL_ROUTES[canonical]
    except KeyError as exc:
        supported = sorted([*MODEL_ROUTES, *MODEL_ROUTE_ALIASES])
        raise ValueError(
            f"Unsupported LLM_ROUTE={route!r}. Supported routes: {', '.join(supported)}"
        ) from exc


def iter_model_routes() -> Iterable[ModelRoute]:
    """Iterate canonical model routes in stable order."""
    for route in sorted(MODEL_ROUTES):
        yield MODEL_ROUTES[route]


def key_is_configured(route: ModelRoute) -> bool:
    """Check whether a route's managed key is present without exposing the value."""
    return bool(env_value(route.key_env, "").strip())
