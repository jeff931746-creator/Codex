#!/usr/bin/env python3
"""
批量拆解 worker（支持 SiliconFlow 和 Gemini）

用法:
    python3 run.py --game "游戏名"
    python3 run.py --game "游戏名" --provider gemini
    python3 run.py --game "游戏名" --model Pro/zai-org/GLM-5.1
    python3 run.py --game "游戏名" --dry-run   # 只导出 prompt 不调 API

流程:
    1. 读 inputs/<游戏名>/ 下所有 .md/.txt 作为资料
    2. 读机制库《拆解质量标准》+ 一份参考拆解（保卫向日葵）
    3. 按 provider 调对应 API
    4. 按 ===FILE: xxx=== 分隔符拆分响应
    5. 写到 outputs/<游戏名>/
"""
import argparse
import json
import os
import re
import sys
import ssl
import urllib.request
import urllib.error
from pathlib import Path

try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CTX = ssl.create_default_context()

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent  # /Users/mt/Documents/Codex
LIBRARY = REPO_ROOT / "research" / "资料" / "机制库"
STANDARDS = LIBRARY / "拆解质量标准.md"
REFERENCE_GAME = LIBRARY / "保卫向日葵"

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

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def collect_inputs(game_dir: Path) -> str:
    if not game_dir.exists():
        sys.exit(f"[错] 资料目录不存在: {game_dir}")
    files = sorted([p for p in game_dir.rglob("*") if p.is_file() and p.suffix in {".md", ".txt"}])
    if not files:
        sys.exit(f"[错] {game_dir} 下没有 .md/.txt 资料")
    chunks = []
    for f in files:
        rel = f.relative_to(game_dir)
        chunks.append(f"===INPUT: {rel}===\n{read_text(f)}")
    return "\n\n".join(chunks)

def collect_reference() -> str:
    if not REFERENCE_GAME.exists():
        return ""
    files = sorted([p for p in REFERENCE_GAME.rglob("*.md") if p.is_file()])
    chunks = []
    for f in files:
        rel = f.relative_to(REFERENCE_GAME)
        chunks.append(f"===REF: {rel}===\n{read_text(f)}")
    return "\n\n".join(chunks)

# ---------- providers ----------

def http_post_json(url: str, payload: dict, headers: dict, timeout: int = 1200) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        sys.exit(f"[错] HTTP {e.code}: {body[:800]}")
    except urllib.error.URLError as e:
        sys.exit(f"[错] 网络错误: {e}")

def estimate_tokens(text: str) -> int:
    """粗估 token 数（中文约 1.5 chars/token，英文约 4 chars/token）"""
    return len(text) // 2

TOKEN_WARN = 40_000   # 超过此值打警告
TOKEN_ABORT = 80_000  # 超过此值直接退出，防止意外巨额消耗

def call_siliconflow(model: str, system_prompt: str, user_prompt: str) -> str:
    api_key = os.environ.get("SILICONFLOW_API_KEY")
    base_url = os.environ.get("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
    if not api_key:
        sys.exit("[错] SILICONFLOW_API_KEY 未设置")

    input_tokens = estimate_tokens(system_prompt + user_prompt)
    print(f"[tokens] 预估输入 ~{input_tokens:,} tokens（system {len(system_prompt):,} + user {len(user_prompt):,} chars）")
    if input_tokens > TOKEN_ABORT:
        sys.exit(f"[中止] 输入超过 {TOKEN_ABORT:,} tokens 安全阈值，请检查 prompt 构造")
    if input_tokens > TOKEN_WARN:
        print(f"[警告] 输入超过 {TOKEN_WARN:,} tokens，请确认 prompt 没有多余内容")

    url = f"{base_url}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 16384,
        "stream": True,  # 流式避免长文生成超时
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers)
    chunks = []
    char_count = 0
    try:
        with urllib.request.urlopen(req, timeout=1200, context=_SSL_CTX) as resp:
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
                            char_count += len(delta)
                            if char_count % 2000 < len(delta):
                                print(f"[stream] 已生成 {char_count:,} chars…", flush=True)
                    except Exception:
                        pass
    except urllib.error.HTTPError as e:
        body_err = e.read().decode("utf-8", "ignore")
        sys.exit(f"[错] HTTP {e.code}: {body_err[:800]}")
    except urllib.error.URLError as e:
        sys.exit(f"[错] 网络错误: {e}")
    content = "".join(chunks)
    print(f"[tokens] 输出 {char_count:,} chars（约 {char_count//2:,} tokens）")
    return content

def call_gemini(model: str, system_prompt: str, user_prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("[错] GEMINI_API_KEY 未设置")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 16384},
    }
    body = http_post_json(url, payload, {"Content-Type": "application/json"})
    try:
        parts = body["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts)
    except (KeyError, IndexError):
        sys.exit(f"[错] Gemini 响应结构异常: {json.dumps(body, ensure_ascii=False)[:500]}")

PROVIDERS = {
    "siliconflow": {
        "call": call_siliconflow,
        "default_model_env": "SILICONFLOW_MODEL",
        "default_model": "Pro/zai-org/GLM-5.1",
    },
    "gemini": {
        "call": call_gemini,
        "default_model_env": "GEMINI_MODEL",
        "default_model": "gemini-2.5-pro",
    },
}

# ---------- parse & write ----------

FILE_SEP = re.compile(r"^===FILE:\s*(.+?)\s*===\s*$", re.MULTILINE)

def split_files(text: str) -> list[tuple[str, str]]:
    matches = list(FILE_SEP.finditer(text))
    if not matches:
        return [("_raw_response.md", text)]
    out = []
    for i, m in enumerate(matches):
        path = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip() + "\n"
        out.append((path, content))
    return out

def write_outputs(game: str, files: list[tuple[str, str]]) -> Path:
    out_dir = ROOT / "outputs" / game
    out_dir.mkdir(parents=True, exist_ok=True)
    for rel, content in files:
        rel = rel.lstrip("/").replace("..", "_")
        dest = out_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
    return out_dir

# ---------- main ----------

def main():
    load_env()
    default_provider = os.environ.get("PROVIDER", "siliconflow").lower()
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True, help="游戏名（对应 inputs/<game>/ 目录）")
    ap.add_argument("--provider", default=default_provider, choices=list(PROVIDERS.keys()))
    ap.add_argument("--model", default=None, help="覆盖默认模型")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-critique", action="store_true", help="跳过第二轮自审（默认会跑）")
    args = ap.parse_args()

    prov = PROVIDERS[args.provider]
    model = args.model or os.environ.get(prov["default_model_env"], prov["default_model"])

    game_inputs = ROOT / "inputs" / args.game
    system_prompt = read_text(ROOT / "prompts" / "system.md")
    standards = read_text(STANDARDS)
    reference = collect_reference()
    materials = collect_inputs(game_inputs)

    user_prompt = f"""# 任务
给《{args.game}》做一份完整的机制库拆解。

# 拆解质量标准（必须逐条满足）
{standards}

# 参考范式：保卫向日葵（已完成的高质量拆解，对齐它的结构、粒度、语气）
{reference}

# 本次要拆解的游戏资料
{materials}

# 产出
按 system prompt 指定的 ===FILE: xxx=== 分隔符，输出 00_总档.md 和所有模块拆解文件。现在开始。
"""

    print(f"[i] provider={args.provider} model={model} game={args.game}")
    print(f"[i] system prompt: {len(system_prompt)} chars")
    print(f"[i] user prompt: {len(user_prompt)} chars (standards {len(standards)} + ref {len(reference)} + materials {len(materials)})")

    if args.dry_run:
        dump = ROOT / f"_dryrun_{args.game}.txt"
        dump.write_text(f"=== SYSTEM ===\n{system_prompt}\n\n=== USER ===\n{user_prompt}", encoding="utf-8")
        print(f"[i] dry-run → {dump}")
        return

    print(f"[i] 第 1 轮：出初稿…")
    draft = prov["call"](model, system_prompt, user_prompt)
    raw_dir = ROOT / "outputs" / args.game
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / "_draft_raw.md").write_text(draft, encoding="utf-8")
    print(f"[i] 初稿长度: {len(draft)} chars，存到 _draft_raw.md")

    if args.no_critique:
        final = draft
    else:
        critique_prompt = read_text(ROOT / "prompts" / "critique.md")
        critique_user = f"""# 拆解质量标准
{standards}

# 待审稿的初稿
{draft}

# 产出
按 system prompt 要求，输出重写后的完整拆解（用 ===FILE: xxx=== 分隔）。不要评论、不要 diff，直接给最终成品。"""
        print(f"[i] 第 2 轮：自审 + 重写…")
        final = prov["call"](model, critique_prompt, critique_user)
        (raw_dir / "_final_raw.md").write_text(final, encoding="utf-8")
        print(f"[i] 终稿长度: {len(final)} chars，存到 _final_raw.md")

    files = split_files(final)
    out_dir = write_outputs(args.game, files)
    print(f"[✓] 产出 {len(files)} 个文件 → {out_dir}")
    for rel, _ in files:
        print(f"    - {rel}")
    print(f"\n下一步：告诉 Claude『审校 {args.game}』，让它按质量标准过一遍再落库。")

if __name__ == "__main__":
    main()
