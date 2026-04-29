#!/usr/bin/env python3
"""
资料搜集脚本 —— 完全在 Python 进程内完成，不经过 Claude。

用法:
    python3 collect.py --game "游戏名"

流程:
    1. DuckDuckGo HTML 搜索（无需 API key）× 2 个查询
    2. urllib 抓取前 2-3 个结果页，strip HTML，截取前 6000 chars/页
    3. 拼成原始文本（最多 15,000 chars）
    4. 调 SiliconFlow 小模型摘要，输出 ≤ 2000 字结构化资料
    5. 写入 inputs/<游戏名>/网络资料.md

退出码:
    0 = 成功（文件已写入）
    1 = 失败（无法获取任何资料）
"""
import argparse
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CTX = ssl.create_default_context()

ROOT = Path(__file__).resolve().parent

# ---------- 配置 ----------

SUMMARY_MODEL = None  # 在 main() 里从环境变量读取
MAX_RAW_CHARS = 15_000             # 送给摘要模型的原始文本上限
MAX_PER_PAGE = 6_000               # 每页抓取字符上限
MAX_FALLBACK_CHARS = 3_000         # 摘要失败时直接写入的原始文本上限
FETCH_TIMEOUT = 15                 # 页面抓取超时（秒）
SUMMARY_TIMEOUT = 300              # 摘要 API 超时（秒）

SUMMARY_SYSTEM = "你是游戏资料整理员，擅长提炼游戏机制信息。"
SUMMARY_PROMPT = """把下面的网页原始文本整理成结构化游戏介绍，包含以下内容（如有）：
- 核心玩法（一句话）
- 主要系统：战斗/养成/资源循环/构筑
- 付费与变现方式
- 平台与发行商
- 玩家评价中提到的设计亮点或问题

输出 ≤ 2000 字，只保留对游戏机制分析有用的信息，忽略广告、导航和无关内容。

网页原始文本：
{raw}"""

# ---------- utils ----------

def load_env():
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def strip_html(html: str) -> str:
    """去除 HTML 标签，压缩空白，保留可读文本。"""
    # 去掉 script / style 块
    html = re.sub(r'<(script|style)[^>]*>.*?</(script|style)>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
    # 去掉所有标签
    text = re.sub(r'<[^>]+>', ' ', html)
    # 压缩空白
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fetch_page(url: str) -> str:
    """抓取单个页面，返回纯文本（失败返回空字符串）。"""
    # 对 URL 中的非 ASCII 字符做编码，避免 UnicodeEncodeError
    parsed = urllib.parse.urlparse(url)
    safe_path = urllib.parse.quote(parsed.path, safe="/:@!$&'()*+,;=")
    url = urllib.parse.urlunparse(parsed._replace(path=safe_path))

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT, context=_SSL_CTX) as resp:
            # 只读 content-type 为 text 的页面
            ct = resp.headers.get("Content-Type", "")
            if "text" not in ct and "html" not in ct:
                return ""
            raw = resp.read(300_000).decode("utf-8", errors="ignore")
            return strip_html(raw)
    except Exception as e:
        print(f"[fetch] 跳过 {url[:60]}… ({type(e).__name__})", flush=True)
        return ""


def search_duckduckgo(query: str, max_results: int = 3) -> list[str]:
    """
    用 DuckDuckGo HTML 搜索，返回结果 URL 列表。
    不需要 API key。
    """
    search_url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    try:
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT, context=_SSL_CTX) as resp:
            html = resp.read(500_000).decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[search] DuckDuckGo 搜索失败: {e}", flush=True)
        return []

    # DDG HTML 结果格式：<a class="result__a" href="//duckduckgo.com/l/?uddg=<encoded_url>">
    raw_hrefs = re.findall(r'class="result__a"[^>]+href="([^"]+)"', html)
    clean = []
    for href in raw_hrefs:
        # 解码 DDG 重定向链接，提取真实 URL
        if href.startswith("//"):
            href = "https:" + href
        parsed = urllib.parse.urlparse(href)
        params = urllib.parse.parse_qs(parsed.query)
        if "uddg" in params:
            real_url = urllib.parse.unquote(params["uddg"][0])
        else:
            real_url = href
        if not real_url.startswith("http"):
            continue
        clean.append(real_url)
        if len(clean) >= max_results:
            break
    print(f"[search] 「{query[:40]}」→ {len(clean)} 个结果", flush=True)
    return clean


def call_siliconflow_summary(raw_text: str, model: str) -> str:
    """
    调 SiliconFlow 模型做摘要。
    失败时返回空字符串（调用方决定降级策略）。
    """
    api_key = os.environ.get("SILICONFLOW_API_KEY", "").strip()
    base_url = os.environ.get("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
    if not api_key:
        print("[summary] SILICONFLOW_API_KEY 未设置，跳过摘要", flush=True)
        return ""

    # 截断原始文本
    truncated = raw_text[:MAX_RAW_CHARS]
    user_msg = SUMMARY_PROMPT.format(raw=truncated)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SUMMARY_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
        "stream": True,  # 流式防止慢模型超时
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(f"{base_url}/chat/completions", data=data, headers=headers)

    print(f"[summary] 发送 ~{len(truncated):,} chars 给 {model}…", flush=True)
    chunks = []
    try:
        with urllib.request.urlopen(req, timeout=SUMMARY_TIMEOUT, context=_SSL_CTX) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8").strip()
                if not line or line == "data: [DONE]":
                    continue
                if line.startswith("data: "):
                    try:
                        obj = json.loads(line[6:])
                        delta = obj["choices"][0]["delta"].get("content", "")
                        if delta:
                            chunks.append(delta)
                    except Exception:
                        pass
        content = "".join(chunks)
        print(f"[summary] 完成，输出 {len(content):,} chars", flush=True)
        return content
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", "ignore")
        print(f"[summary] HTTP {e.code}: {err[:200]}", flush=True)
        return ""
    except Exception as e:
        print(f"[summary] 摘要失败: {e}", flush=True)
        return ""


# ---------- main ----------

def main():
    load_env()
    summary_model = os.environ.get("SILICONFLOW_MODEL", "Pro/moonshotai/Kimi-K2.6")

    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True, help="游戏名（对应 inputs/<game>/ 目录）")
    args = ap.parse_args()
    game = args.game

    out_dir = ROOT / "inputs" / game
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "网络资料.md"

    print(f"[i] 开始搜集资料：{game}", flush=True)

    # --- Step 1: 搜索 ---
    queries = [
        f"{game} 游戏玩法介绍 系统",
        f"{game} 攻略 养成 付费",
    ]
    all_urls: list[str] = []
    for q in queries:
        urls = search_duckduckgo(q, max_results=2)
        for u in urls:
            if u not in all_urls:
                all_urls.append(u)
        time.sleep(1)  # 避免触发搜索限流

    if not all_urls:
        print(f"[错] 搜索无结果，退出", flush=True)
        sys.exit(1)

    # --- Step 2: 抓取页面 ---
    raw_chunks: list[str] = []
    total_chars = 0
    for url in all_urls[:4]:  # 最多抓 4 个页面
        if total_chars >= MAX_RAW_CHARS:
            break
        text = fetch_page(url)
        if not text:
            continue
        chunk = text[:MAX_PER_PAGE]
        raw_chunks.append(f"[来源: {url[:80]}]\n{chunk}")
        total_chars += len(chunk)
        print(f"[fetch] 抓取 {len(chunk):,} chars from {url[:60]}…", flush=True)
        time.sleep(0.5)

    if not raw_chunks:
        print(f"[错] 所有页面抓取失败，退出", flush=True)
        sys.exit(1)

    raw_text = "\n\n".join(raw_chunks)
    print(f"[i] 原始文本总计 {len(raw_text):,} chars", flush=True)

    # --- Step 3: 摘要 ---
    summary = call_siliconflow_summary(raw_text, summary_model)

    if summary:
        final_content = f"# {game} — 网络资料（自动搜集）\n\n{summary}\n"
    else:
        # 摘要失败降级：写截断的原始文本
        print(f"[warn] 摘要失败，写入截断原始文本（≤{MAX_FALLBACK_CHARS} chars）", flush=True)
        fallback = raw_text[:MAX_FALLBACK_CHARS]
        final_content = f"# {game} — 网络资料（原始文本，摘要失败）\n\n{fallback}\n"

    # --- Step 4: 写入 ---
    out_file.write_text(final_content, encoding="utf-8")
    print(f"[✓] 写入 {out_file}（{len(final_content):,} chars）", flush=True)


if __name__ == "__main__":
    main()
