#!/usr/bin/env python3
"""
Save a cleaned chat archive to a timestamped Markdown file.
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


def slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "chat-archive"


def read_body(args: argparse.Namespace) -> str:
    if args.body_file:
        return Path(args.body_file).read_text(encoding="utf-8").strip()
    return (args.body or "").strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write a cleaned chat archive to a timestamped Markdown file."
    )
    parser.add_argument("--output-dir", required=True, help="Directory to write into.")
    parser.add_argument("--topic", default="chat-archive", help="Topic used in filename.")
    parser.add_argument("--title", default="Chat Archive", help="Document title.")
    parser.add_argument("--body", help="Archive body as literal text.")
    parser.add_argument("--body-file", help="Path to a UTF-8 Markdown body file.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    body = read_body(args)

    if not body:
        parser.error("one of --body or --body-file must provide non-empty content")

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{timestamp}-{slugify(args.topic)}.md"
    output_path = output_dir / filename

    content = f"# {args.title.strip() or 'Chat Archive'}\n\n{body.rstrip()}\n"
    output_path.write_text(content, encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
