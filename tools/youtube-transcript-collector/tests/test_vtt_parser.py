#!/usr/bin/env python3
"""Focused parser smoke test for collect_youtube_subtitles.py."""

from pathlib import Path
import importlib.util
import sys
import tempfile


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "collect_youtube_subtitles.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("collector", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["collector"] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    collector = load_module()
    sample = """WEBVTT

Kind: captions
Language: en

00:00:00.000 --> 00:00:02.000
<c>Hello</c> &amp; welcome

00:00:02.000 --> 00:00:04.000
<c>Hello</c> &amp; welcome

00:00:04.000 --> 00:00:06.000
to GMTK.
"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir) / "sample.vtt"
        path.write_text(sample, encoding="utf-8")
        output = collector.vtt_to_text(path)

    expected = "Hello & welcome\nto GMTK."
    if output != expected:
        raise AssertionError(f"unexpected parser output: {output!r}")
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
