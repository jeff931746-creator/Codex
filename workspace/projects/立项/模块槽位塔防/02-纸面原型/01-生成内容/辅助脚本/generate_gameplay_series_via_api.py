#!/Library/Frameworks/Python.framework/Versions/3.10/bin/python3

import argparse
import base64
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import certifi


BASE_DIR = Path("/Users/mt/Documents/Codex/模块槽位塔防")
SERIES_PROMPTS = BASE_DIR / "模块槽位塔防_玩法图Prompts.md"
LOCKED_PROMPTS = BASE_DIR / "图2-图6_布局锁定修正版Prompts.md"
OUTPUT_DIR = BASE_DIR / "玩法图片输出_api"
DEFAULT_MODEL = "imagen-4.0-generate-001"
DEFAULT_API_ROOT = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_GEMINI_IMAGE_MODEL = "gemini-2.5-flash-image"

IMAGE_MARKERS = {
    1: "## 图1：基础防线",
    2: "## 图2：掉落模块 修正版",
    3: "## 图3：安装第一个模块 修正版",
    4: "## 图4：第二模块触发联动 修正版",
    5: "## 图5：Build 成型 修正版",
    6: "## 图6：Boss 波检验 修正版",
}

IMAGE_NAMES = {
    1: "图1_基础防线",
    2: "图2_掉落模块",
    3: "图3_安装第一个模块",
    4: "图4_第二模块触发联动",
    5: "图5_Build成型",
    6: "图6_Boss波检验",
}


def load_prompt(source: Path, marker: str) -> str:
    content = source.read_text(encoding="utf-8")
    lines = content.splitlines()
    capture_section = False
    capture_code = False
    captured = []

    for line in lines:
      if line == marker:
        capture_section = True
        continue
      if capture_section and line.startswith("## "):
        break
      if capture_section and line.strip() == "```text":
        capture_code = True
        continue
      if capture_section and capture_code and line.strip() == "```":
        break
      if capture_section and capture_code:
        captured.append(line)

    prompt = "\n".join(captured).strip()
    if not prompt:
      raise ValueError(f"Failed to extract prompt for marker: {marker}")
    return prompt


def prompt_for_image(index: int) -> str:
    if index == 1:
        return load_prompt(SERIES_PROMPTS, IMAGE_MARKERS[index])
    return load_prompt(LOCKED_PROMPTS, IMAGE_MARKERS[index])


def request_imagen(api_key: str, model: str, prompt: str, aspect_ratio: str, sample_count: int) -> dict:
    url = f"{DEFAULT_API_ROOT}/{model}:predict"
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": sample_count,
            "aspectRatio": aspect_ratio,
        },
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen(request, timeout=300, context=ssl_context) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Imagen API request failed: HTTP {exc.code}\n{detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Imagen API request failed: {exc}") from exc


def request_gemini_image(api_key: str, model: str, prompt: str) -> dict:
    url = f"{DEFAULT_API_ROOT}/{model}:generateContent"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}],
        }],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
        },
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen(request, timeout=300, context=ssl_context) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini image API request failed: HTTP {exc.code}\n{detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Gemini image API request failed: {exc}") from exc


def extract_images(response: dict) -> list[bytes]:
    images = []

    for prediction in response.get("predictions", []):
        if isinstance(prediction, dict):
            if prediction.get("bytesBase64Encoded"):
                images.append(base64.b64decode(prediction["bytesBase64Encoded"]))
            elif prediction.get("image", {}).get("imageBytes"):
                images.append(base64.b64decode(prediction["image"]["imageBytes"]))

    for candidate in response.get("candidates", []):
        content = candidate.get("content", {})
        for part in content.get("parts", []):
            inline_data = part.get("inlineData") or part.get("inline_data")
            if inline_data and inline_data.get("data"):
                images.append(base64.b64decode(inline_data["data"]))

    if not images:
        raise RuntimeError(f"No image bytes found in API response: {json.dumps(response, ensure_ascii=False)[:1000]}")

    return images


def save_image_set(index: int, prompt: str, response: dict, images: list[bytes]) -> None:
    folder = OUTPUT_DIR / IMAGE_NAMES[index]
    folder.mkdir(parents=True, exist_ok=True)

    (folder / "prompt.txt").write_text(prompt, encoding="utf-8")
    (folder / "response.json").write_text(
        json.dumps(response, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    for idx, image_bytes in enumerate(images, start=1):
        suffix = "" if len(images) == 1 else f"_{idx:02d}"
        image_path = folder / f"{IMAGE_NAMES[index]}{suffix}.png"
        image_path.write_bytes(image_bytes)


def generate_series(api_key: str, model: str, backend: str, aspect_ratio: str, sample_count: int, only: list[int], delay_seconds: float) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for index in only:
        prompt = prompt_for_image(index)
        print(f"[{index}] Generating {IMAGE_NAMES[index]}...")
        if backend == "imagen":
            response = request_imagen(api_key, model, prompt, aspect_ratio, sample_count)
        else:
            response = request_gemini_image(api_key, model, prompt)
        images = extract_images(response)
        save_image_set(index, prompt, response, images)
        print(f"[{index}] Saved {len(images)} image(s) to {OUTPUT_DIR / IMAGE_NAMES[index]}")
        if delay_seconds > 0:
            time.sleep(delay_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the module-slot tower defense gameplay image series via Imagen API and save locally.",
    )
    parser.add_argument(
        "images",
        nargs="*",
        type=int,
        help="Which images to generate (default: 1 2 3 4 5 6)",
    )
    parser.add_argument(
        "--backend",
        choices=["imagen", "gemini"],
        default="gemini",
        help='Image backend to use (default: "gemini")',
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override model id. Defaults depend on backend.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(OUTPUT_DIR),
        help="Where to save generated images (default: 玩法图片输出_api)",
    )
    parser.add_argument(
        "--aspect-ratio",
        default="9:16",
        help='Aspect ratio for generated images (default: "9:16")',
    )
    parser.add_argument(
        "--sample-count",
        type=int,
        default=1,
        help="How many images to generate per prompt (default: 1)",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=1.5,
        help="Delay between requests in seconds (default: 1.5)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("GEMINI_API_KEY is not set.", file=sys.stderr)
        return 1

    if args.sample_count < 1 or args.sample_count > 4:
        print("--sample-count must be between 1 and 4.", file=sys.stderr)
        return 1

    only = args.images or [1, 2, 3, 4, 5, 6]
    invalid = [index for index in only if index not in IMAGE_MARKERS]
    if invalid:
        print(f"Invalid image indexes: {invalid}", file=sys.stderr)
        return 1

    global OUTPUT_DIR
    OUTPUT_DIR = Path(args.output_dir)

    model = args.model or (DEFAULT_MODEL if args.backend == "imagen" else DEFAULT_GEMINI_IMAGE_MODEL)

    try:
        generate_series(
            api_key=api_key,
            model=model,
            backend=args.backend,
            aspect_ratio=args.aspect_ratio,
            sample_count=args.sample_count,
            only=only,
            delay_seconds=args.delay_seconds,
        )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
