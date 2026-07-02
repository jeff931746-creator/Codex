#!/usr/bin/env python3
"""Extract public visible copy and metadata from a Douyin share/video URL.

This is not an ASR/transcription tool. It reads text surfaces exposed by the
public share page, such as title/description, hashtags, author metadata, and
any subtitle/caption-like JSON fields that are present in the page payload.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def first_url(text: str) -> str:
    match = re.search(r"https?://[^\s，。；;]+", text)
    if match:
        return match.group(0).rstrip(".,)")
    return text.strip()


def fetch_url(
    url: str,
    timeout: float,
    insecure: bool = False,
    cookie: str | None = None,
) -> tuple[str, str]:
    headers = dict(DEFAULT_HEADERS)
    if cookie:
        headers["Cookie"] = cookie
    request = urllib.request.Request(url, headers=headers)
    context = ssl._create_unverified_context() if insecure else None
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        body = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
        return response.geturl(), body.decode(charset, errors="replace")


def fetch_with_browser(
    url: str,
    timeout: float,
    headless: bool = True,
    user_data_dir: str | None = None,
) -> tuple[str, str]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Python playwright is not installed.") from exc

    launch_options: dict[str, Any] = {
        "headless": headless,
        "args": ["--disable-blink-features=AutomationControlled"],
    }
    chrome_path = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if chrome_path.exists():
        launch_options["executable_path"] = str(chrome_path)

    with sync_playwright() as playwright:
        if user_data_dir:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir,
                **launch_options,
            )
            close_target = context
        else:
            browser = playwright.chromium.launch(**launch_options)
            context = browser.new_context(
                user_agent=DEFAULT_HEADERS["User-Agent"],
                locale="zh-CN",
            )
            close_target = browser

        try:
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=int(timeout * 1000))
            try:
                page.wait_for_load_state("load", timeout=5000)
            except Exception:
                pass
            page.wait_for_timeout(1500)
            return page.url, page.content()
        finally:
            close_target.close()


def extract_video_id(url_or_text: str) -> str | None:
    text = urllib.parse.unquote(url_or_text)
    patterns = [
        r"/video/(\d{12,})",
        r"/share/video/(\d{12,})",
        r"(?:aweme_id|item_id|modal_id)=(\d{12,})",
        r"\b(\d{16,})\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def extract_input_visible_copy(text: str) -> str | None:
    before_url = re.split(r"https?://[^\s，。；;]+", text, maxsplit=1)[0]
    without_url = before_url
    without_url = re.sub(r"\b\d{1,2}/\d{1,2}\b", " ", without_url)
    without_url = re.sub(r"\b[A-Za-z0-9._@:/-]{4,}\b", " ", without_url)
    without_url = without_url.replace("复制打开抖音，看看", " ")
    without_url = without_url.replace("打开抖音，看看", " ")
    without_url = re.sub(r"^\s*[\W_]*\d+\s*", " ", without_url)
    without_url = re.sub(r"#\s+", "#", without_url)
    without_url = without_url.replace("...", "")
    without_url = without_url.replace("…", "")
    without_url = re.sub(r"\s+", " ", without_url).strip(" .:：，,;；")
    return without_url or None


def find_balanced_json(text: str, start: int) -> str | None:
    while start < len(text) and text[start] not in "[{":
        start += 1
    if start >= len(text):
        return None

    opening = text[start]
    closing = "}" if opening == "{" else "]"
    depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return None


def parse_json_surfaces(page_html: str) -> list[dict[str, Any]]:
    surfaces: list[dict[str, Any]] = []
    decoded = html.unescape(page_html)

    markers = [
        "window._ROUTER_DATA",
        "self.__pace_f.push",
        "videoInfoRes",
        "aweme_detail",
        "awemeDetail",
    ]
    for marker in markers:
        offset = 0
        while True:
            position = decoded.find(marker, offset)
            if position < 0:
                break
            json_text = find_balanced_json(decoded, position + len(marker))
            if json_text:
                try:
                    surfaces.append(json.loads(json_text))
                except json.JSONDecodeError:
                    pass
            offset = position + len(marker)

    for match in re.finditer(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        decoded,
        flags=re.DOTALL | re.IGNORECASE,
    ):
        try:
            surfaces.append(json.loads(html.unescape(match.group(1).strip())))
        except json.JSONDecodeError:
            pass

    return surfaces


def parse_html_meta(page_html: str) -> dict[str, str]:
    decoded = html.unescape(page_html)
    meta: dict[str, str] = {}

    title_match = re.search(r"<title[^>]*>(.*?)</title>", decoded, flags=re.DOTALL | re.IGNORECASE)
    if title_match:
        meta["title"] = re.sub(r"\s+", " ", title_match.group(1)).strip()

    for match in re.finditer(r"<meta\s+([^>]+)>", decoded, flags=re.IGNORECASE):
        attrs = dict(
            (key.lower(), html.unescape(value))
            for key, value in re.findall(r'([\w:-]+)=["\'](.*?)["\']', match.group(1))
        )
        name = attrs.get("name") or attrs.get("property")
        content = attrs.get("content")
        if name and content:
            meta[name] = content.strip()

    canonical_match = re.search(
        r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\'](.*?)["\']',
        decoded,
        flags=re.IGNORECASE,
    )
    if canonical_match:
        meta["canonical_url"] = html.unescape(canonical_match.group(1)).strip()

    return meta


def walk(value: Any, path: str = ""):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            yield from walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f"{path}[{index}]")


def unique_strings(values: list[Any], limit: int = 30) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value is None:
            continue
        if not isinstance(value, str):
            value = str(value)
        value = html.unescape(value).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
        if len(result) >= limit:
            break
    return result


def find_aweme_objects(surfaces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for surface in surfaces:
        for _path, obj in walk(surface):
            if not isinstance(obj, dict):
                continue
            has_video_identity = any(key in obj for key in ("aweme_id", "awemeId", "item_id"))
            has_copy = any(key in obj for key in ("desc", "description", "title"))
            if has_video_identity and has_copy:
                candidates.append(obj)
            if "aweme_detail" in obj and isinstance(obj["aweme_detail"], dict):
                candidates.append(obj["aweme_detail"])
            if "awemeDetail" in obj and isinstance(obj["awemeDetail"], dict):
                candidates.append(obj["awemeDetail"])

    candidates.sort(key=lambda item: len(json.dumps(item, ensure_ascii=False)), reverse=True)
    return candidates


def nested_get(obj: dict[str, Any], keys: list[str]) -> Any:
    current: Any = obj
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def extract_url_list(value: Any) -> list[str]:
    urls: list[Any] = []
    if isinstance(value, dict):
        if isinstance(value.get("url_list"), list):
            urls.extend(value["url_list"])
        for child in value.values():
            urls.extend(extract_url_list(child))
    elif isinstance(value, list):
        for child in value:
            urls.extend(extract_url_list(child))
    return unique_strings(urls, limit=20)


def extract_caption_like_text(surfaces: list[dict[str, Any]]) -> list[str]:
    values: list[Any] = []
    key_markers = ("caption", "subtitle", "sub_title", "ocr", "asr")
    text_keys = ("text", "content", "sentence", "utterance", "desc")
    for surface in surfaces:
        for path, obj in walk(surface):
            lower_path = path.lower()
            if isinstance(obj, dict) and any(marker in lower_path for marker in key_markers):
                for key in text_keys:
                    if key in obj:
                        values.append(obj[key])
            elif isinstance(obj, list) and any(marker in lower_path for marker in key_markers):
                values.extend(obj)
    return unique_strings(values, limit=100)


def build_result(
    source: str,
    final_url: str | None,
    page_html: str | None,
    error: str | None,
    input_visible_copy: str | None = None,
) -> dict[str, Any]:
    video_id = extract_video_id(final_url or source)
    result: dict[str, Any] = {
        "source": source,
        "final_url": final_url,
        "video_id": video_id,
        "status": "ok",
        "fetched_at": int(time.time()),
        "extraction_scope": "public_page_visible_text_and_metadata",
        "not_transcript_notice": (
            "This output is not a guaranteed full spoken transcript unless "
            "caption_like_text is populated from page data."
        ),
        "errors": [],
        "text": {},
        "metadata": {},
        "hashtags": [],
        "caption_like_text": [],
        "video_urls": [],
        "raw_signals": {},
    }

    if error:
        result["status"] = "fetch_error"
        result["errors"].append(error)
        result["text"]["input_visible_copy"] = input_visible_copy
        return result

    if not page_html:
        result["status"] = "empty"
        result["errors"].append("No HTML was available to parse.")
        return result

    html_meta = parse_html_meta(page_html)
    if "byted_acrawler" in page_html or "__ac_signature" in page_html:
        result["status"] = "blocked_by_challenge"
        result["errors"].append("Douyin returned an anti-bot challenge page.")

    surfaces = parse_json_surfaces(page_html)
    result["raw_signals"] = {
        "json_surfaces_found": len(surfaces),
        "html_size": len(page_html),
        "html_meta_found": bool(html_meta),
    }

    aweme = find_aweme_objects(surfaces)
    item = aweme[0] if aweme else {}

    title = (
        item.get("desc")
        or item.get("description")
        or item.get("title")
        or nested_get(item, ["share_info", "share_title"])
    )
    author = item.get("author") if isinstance(item.get("author"), dict) else {}
    music = item.get("music") if isinstance(item.get("music"), dict) else {}
    share_info = item.get("share_info") if isinstance(item.get("share_info"), dict) else {}
    statistics = item.get("statistics") if isinstance(item.get("statistics"), dict) else {}

    result["text"] = {
        "title_or_desc": html.unescape(title).strip() if isinstance(title, str) else html_meta.get("title"),
        "share_title": share_info.get("share_title"),
        "share_desc": share_info.get("share_desc") or html_meta.get("description"),
        "input_visible_copy": input_visible_copy,
    }

    meta_description = html_meta.get("description", "")
    author_from_description = re.search(r"-\s*([^-\s]+)于(\d{8})发布", meta_description)
    likes_from_description = re.search(r"收获了([^，,]+)个喜欢", meta_description)
    result["metadata"] = {
        "aweme_id": item.get("aweme_id") or item.get("awemeId") or item.get("item_id"),
        "author_nickname": author.get("nickname")
        or (author_from_description.group(1) if author_from_description else None),
        "author_unique_id": author.get("unique_id") or author.get("short_id"),
        "create_time": item.get("create_time"),
        "published_date": author_from_description.group(2) if author_from_description else None,
        "duration_ms": nested_get(item, ["video", "duration"]),
        "music_title": music.get("title"),
        "share_url": share_info.get("share_url") or html_meta.get("canonical_url"),
        "statistics": statistics,
        "like_count_text": likes_from_description.group(1) if likes_from_description else None,
        "keywords": html_meta.get("keywords"),
    }

    text_extra = item.get("text_extra")
    if isinstance(text_extra, list):
        result["hashtags"] = unique_strings(
            [
                entry.get("hashtag_name") or entry.get("hashtagName")
                for entry in text_extra
                if isinstance(entry, dict)
            ]
        )
    if not result["hashtags"] and html_meta.get("keywords"):
        result["hashtags"] = unique_strings(
            [
                keyword.strip()
                for keyword in html_meta["keywords"].split(",")
                if keyword.strip() not in ("抖音", "抖音短视频", "抖音官网")
            ]
        )

    result["caption_like_text"] = extract_caption_like_text(surfaces)
    result["video_urls"] = extract_url_list(item.get("video"))

    if not surfaces and result["status"] == "ok":
        result["status"] = "no_structured_payload"
        result["errors"].append("No parseable JSON payload was found in the page.")
    elif not item and result["status"] == "ok":
        result["status"] = "html_meta_only" if html_meta else "metadata_only"
        result["errors"].append("Structured JSON was found, but no aweme video object was recognized.")

    return result


def result_to_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Douyin Text Extraction",
        "",
        f"- Status: `{result.get('status')}`",
        f"- Source: {result.get('source')}",
        f"- Final URL: {result.get('final_url')}",
        f"- Video ID: `{result.get('video_id')}`",
        f"- Scope: {result.get('extraction_scope')}",
        "",
        "## Visible Copy",
    ]
    text = result.get("text") or {}
    for key in ("title_or_desc", "share_title", "share_desc", "input_visible_copy"):
        value = text.get(key)
        if value:
            lines.append(f"- {key}: {value}")

    metadata = result.get("metadata") or {}
    lines.extend(["", "## Metadata"])
    for key in ("author_nickname", "author_unique_id", "create_time", "duration_ms", "music_title", "share_url"):
        value = metadata.get(key)
        if value not in (None, "", {}):
            lines.append(f"- {key}: {value}")

    hashtags = result.get("hashtags") or []
    if hashtags:
        lines.extend(["", "## Hashtags", ", ".join(f"#{tag}" for tag in hashtags)])

    captions = result.get("caption_like_text") or []
    if captions:
        lines.extend(["", "## Caption-Like Text"])
        lines.extend(f"- {line}" for line in captions)

    errors = result.get("errors") or []
    if errors:
        lines.extend(["", "## Notes"])
        lines.extend(f"- {error}" for error in errors)

    lines.extend(["", f"> {result.get('not_transcript_notice')}"])
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace) -> dict[str, Any]:
    source = first_url(args.input)
    input_visible_copy = extract_input_visible_copy(args.input)
    final_url: str | None = None
    page_html: str | None = None
    error: str | None = None

    if args.html_file:
        page_html = Path(args.html_file).read_text(encoding="utf-8")
        final_url = source
    elif args.browser:
        try:
            final_url, page_html = fetch_with_browser(
                source,
                timeout=args.timeout,
                headless=not args.show_browser,
                user_data_dir=args.user_data_dir,
            )
        except (RuntimeError, TimeoutError, OSError, Exception) as exc:
            error = f"{type(exc).__name__}: {exc}"
            final_url = source
    else:
        try:
            final_url, page_html = fetch_url(
                source,
                timeout=args.timeout,
                insecure=args.insecure,
                cookie=args.cookie,
            )
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            error = f"{type(exc).__name__}: {exc}"
            final_url = source

        video_id = extract_video_id(final_url or source)
        if video_id and (not page_html or "videoInfoRes" not in page_html):
            share_url = f"https://www.iesdouyin.com/share/video/{video_id}/?from_ssr=1"
            try:
                final_url, page_html = fetch_url(
                    share_url,
                    timeout=args.timeout,
                    insecure=args.insecure,
                    cookie=args.cookie,
                )
                error = None
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                if error is None:
                    error = f"{type(exc).__name__}: {exc}"

    if args.save_html and page_html:
        Path(args.save_html).write_text(page_html, encoding="utf-8")

    return build_result(
        source=source,
        final_url=final_url,
        page_html=page_html,
        error=error,
        input_visible_copy=input_visible_copy,
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract public visible text and metadata from a Douyin URL."
    )
    parser.add_argument("input", help="Douyin URL, share text containing a URL, or video URL.")
    parser.add_argument("--html-file", help="Parse a previously saved Douyin HTML file instead of fetching.")
    parser.add_argument("--save-html", help="Save fetched HTML for debugging.")
    parser.add_argument("--timeout", type=float, default=15.0, help="Network timeout in seconds.")
    parser.add_argument("--cookie", help="Optional raw Cookie header copied from a browser session.")
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Fetch with Playwright/Chrome so page JavaScript and browser session state can run.",
    )
    parser.add_argument(
        "--show-browser",
        action="store_true",
        help="Show the browser window when using --browser. Useful for login or CAPTCHA checks.",
    )
    parser.add_argument(
        "--user-data-dir",
        help="Persistent browser profile directory for --browser, useful after logging in once.",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Skip TLS certificate verification. Use only when local Python CA certificates are broken.",
    )
    parser.add_argument("--format", choices=("json", "md"), default="json", help="Output format.")
    parser.add_argument("--output", help="Write output to this file instead of stdout.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    result = run(args)
    if args.format == "md":
        output = result_to_markdown(result)
    else:
        output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
