import { envValue } from "./api-client.mjs";

export const MODEL_ROUTES = {
  DeepSeek_Official_Pro: {
    route: "DeepSeek_Official_Pro",
    provider: "deepseek",
    model: "deepseek-v4-pro",
    keyEnv: "DEEPSEEK_API_KEY",
    baseUrlEnv: "DEEPSEEK_BASE_URL",
    description: "DeepSeek 官方入口，适合质量优先的分析任务。"
  },
  DeepSeek_Official_Flash: {
    route: "DeepSeek_Official_Flash",
    provider: "deepseek",
    model: "deepseek-v4-flash",
    keyEnv: "DEEPSEEK_API_KEY",
    baseUrlEnv: "DEEPSEEK_BASE_URL",
    description: "DeepSeek 官方入口，适合快速批量任务。"
  },
  SiliconFlow_DeepSeek_Flash: {
    route: "SiliconFlow_DeepSeek_Flash",
    provider: "siliconflow",
    model: "deepseek-ai/DeepSeek-V4-Flash",
    keyEnv: "SILICONFLOW_API_KEY",
    baseUrlEnv: "SILICONFLOW_BASE_URL",
    description: "SiliconFlow 上的 DeepSeek 模型，和官方入口分开管理。"
  },
  SiliconFlow_GLM: {
    route: "SiliconFlow_GLM",
    provider: "siliconflow",
    model: "Pro/zai-org/GLM-5.1",
    keyEnv: "SILICONFLOW_API_KEY",
    baseUrlEnv: "SILICONFLOW_BASE_URL",
    description: "SiliconFlow 上的 GLM，适合长文本中文摘要。"
  },
  SiliconFlow_Kimi: {
    route: "SiliconFlow_Kimi",
    provider: "siliconflow",
    model: "moonshotai/Kimi-K2.7-Code",
    keyEnv: "SILICONFLOW_API_KEY",
    baseUrlEnv: "SILICONFLOW_BASE_URL",
    description: "SiliconFlow 上的 Kimi，用于中文表达复核。"
  },
  SiliconFlow_Qwen: {
    route: "SiliconFlow_Qwen",
    provider: "siliconflow",
    model: "Qwen/Qwen2.5-72B-Instruct",
    keyEnv: "SILICONFLOW_API_KEY",
    baseUrlEnv: "SILICONFLOW_BASE_URL",
    description: "SiliconFlow 上的 Qwen2.5 72B，用于低推理成本收集任务。"
  },
  OpenAI_GPT_Mini: {
    route: "OpenAI_GPT_Mini",
    provider: "openai",
    model: "gpt-5-mini",
    keyEnv: "OPENAI_API_KEY",
    baseUrlEnv: "OPENAI_BASE_URL",
    description: "OpenAI 官方入口，适合飞书桥接的轻量回复。"
  },
  Anthropic_Claude_Haiku: {
    route: "Anthropic_Claude_Haiku",
    provider: "anthropic",
    model: "claude-3-5-haiku-latest",
    keyEnv: "ANTHROPIC_API_KEY",
    baseUrlEnv: "ANTHROPIC_BASE_URL",
    description: "Anthropic 官方入口，适合飞书桥接的轻量回复。"
  },
  Anthropic_Claude_Opus: {
    route: "Anthropic_Claude_Opus",
    provider: "anthropic",
    model: "claude-opus-4-7",
    keyEnv: "ANTHROPIC_API_KEY",
    baseUrlEnv: "ANTHROPIC_BASE_URL",
    description: "Anthropic 官方入口，适合高强度文本任务。"
  },
  Google_Gemini_Pro: {
    route: "Google_Gemini_Pro",
    provider: "gemini",
    model: "gemini-2.5-pro",
    keyEnv: "GEMINI_API_KEY",
    baseUrlEnv: "GEMINI_BASE_URL",
    description: "Google Gemini 入口，适合长上下文或多模态任务。"
  }
};

export const MODEL_ROUTE_ALIASES = {
  deepseek_official_pro: "DeepSeek_Official_Pro",
  "deepseek-official-pro": "DeepSeek_Official_Pro",
  "deepseek-official": "DeepSeek_Official_Pro",
  "deepseek-v4-pro": "DeepSeek_Official_Pro",
  "deepseek.official.v4-pro": "DeepSeek_Official_Pro",
  deepseek_official_flash: "DeepSeek_Official_Flash",
  "deepseek-official-flash": "DeepSeek_Official_Flash",
  "deepseek-flash": "DeepSeek_Official_Flash",
  "deepseek.official.v4-flash": "DeepSeek_Official_Flash",
  siliconflow_deepseek_flash: "SiliconFlow_DeepSeek_Flash",
  "siliconflow-deepseek-flash": "SiliconFlow_DeepSeek_Flash",
  "deepseek-sf": "SiliconFlow_DeepSeek_Flash",
  "deepseek.siliconflow.v4-flash": "SiliconFlow_DeepSeek_Flash",
  siliconflow_glm: "SiliconFlow_GLM",
  "siliconflow-glm": "SiliconFlow_GLM",
  glm: "SiliconFlow_GLM",
  "glm-5.1": "SiliconFlow_GLM",
  "glm.siliconflow.5.1": "SiliconFlow_GLM",
  siliconflow_kimi: "SiliconFlow_Kimi",
  "siliconflow-kimi": "SiliconFlow_Kimi",
  kimi: "SiliconFlow_Kimi",
  siliconflow_qwen: "SiliconFlow_Qwen",
  "siliconflow-qwen": "SiliconFlow_Qwen",
  qwen: "SiliconFlow_Qwen",
  "qwen-72b": "SiliconFlow_Qwen",
  "qwen.siliconflow.qwen2.5-72b": "SiliconFlow_Qwen",
  openai_gpt_mini: "OpenAI_GPT_Mini",
  "openai-gpt-mini": "OpenAI_GPT_Mini",
  openai: "OpenAI_GPT_Mini",
  "gpt-mini": "OpenAI_GPT_Mini",
  "gpt-5-mini": "OpenAI_GPT_Mini",
  "openai.official.gpt-5-mini": "OpenAI_GPT_Mini",
  anthropic_claude_haiku: "Anthropic_Claude_Haiku",
  "anthropic-claude-haiku": "Anthropic_Claude_Haiku",
  anthropic: "Anthropic_Claude_Haiku",
  "claude-haiku": "Anthropic_Claude_Haiku",
  "anthropic.official.claude-3.5-haiku": "Anthropic_Claude_Haiku",
  anthropic_claude_opus: "Anthropic_Claude_Opus",
  "anthropic-claude-opus": "Anthropic_Claude_Opus",
  "claude-opus": "Anthropic_Claude_Opus",
  "anthropic.official.claude-opus-4.7": "Anthropic_Claude_Opus",
  google_gemini_pro: "Google_Gemini_Pro",
  "google-gemini-pro": "Google_Gemini_Pro",
  gemini: "Google_Gemini_Pro",
  "gemini-pro": "Google_Gemini_Pro",
  "gemini-2.5-pro": "Google_Gemini_Pro",
  "gemini.google.2.5-pro": "Google_Gemini_Pro"
};

export function canonicalRouteName(route) {
  const requested = String(route || "").trim();
  if (MODEL_ROUTES[requested]) {
    return requested;
  }
  const normalized = requested.toLowerCase();
  return MODEL_ROUTE_ALIASES[normalized] || normalized;
}

export function envRoute(env = process.env) {
  return envValue("LLM_ROUTE", "", env).trim();
}

export function getModelRoute(route) {
  const canonical = canonicalRouteName(route);
  const resolved = MODEL_ROUTES[canonical];
  if (resolved) {
    return resolved;
  }
  const supported = Object.keys({ ...MODEL_ROUTES, ...MODEL_ROUTE_ALIASES }).sort();
  throw new Error(`Unsupported LLM_ROUTE=${JSON.stringify(route)}. Supported routes: ${supported.join(", ")}`);
}
