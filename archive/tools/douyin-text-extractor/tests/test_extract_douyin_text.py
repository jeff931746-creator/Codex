#!/usr/bin/env python3
"""Smoke tests for the Douyin text extractor."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "extract_douyin_text.py"
FIXTURE = ROOT / "tests" / "fixtures" / "router_data.html"


def load_module():
    spec = importlib.util.spec_from_file_location("extract_douyin_text", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_parse_router_data_fixture():
    module = load_module()
    page_html = FIXTURE.read_text(encoding="utf-8")
    result = module.build_result(
        source="https://www.douyin.com/video/7654904410741574385",
        final_url="https://www.douyin.com/video/7654904410741574385",
        page_html=page_html,
        error=None,
    )

    assert result["status"] == "ok"
    assert result["video_id"] == "7654904410741574385"
    assert result["text"]["title_or_desc"].startswith("矛盾的普遍性")
    assert result["metadata"]["author_nickname"] == "智政堂"
    assert result["hashtags"] == ["政治", "矛盾"]
    assert result["video_urls"] == ["https://example.test/video.mp4"]


def test_extract_input_visible_copy():
    module = load_module()
    text = (
        ".71 复制打开抖音，看看【智政堂的作品】矛盾的普遍性与特殊性及其关系？ "
        "#政治 #矛盾 https://v.douyin.com/dM4uqk0A5P0/ 01/12 U@L.jp Eus:/ :9pm"
    )
    assert module.extract_input_visible_copy(text) == "【智政堂的作品】矛盾的普遍性与特殊性及其关系？ #政治 #矛盾"


if __name__ == "__main__":
    test_parse_router_data_fixture()
    test_extract_input_visible_copy()
    print("ok")
