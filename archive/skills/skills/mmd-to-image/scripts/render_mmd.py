#!/usr/bin/env python3
"""Render Mermaid .mmd files to image formats through Mermaid CLI."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SUPPORTED_FORMATS = {"png", "svg", "pdf"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a Mermaid .mmd file to PNG, SVG, or PDF."
    )
    parser.add_argument("input", help="Path to a .mmd file")
    parser.add_argument("--out", "-o", help="Output image path")
    parser.add_argument(
        "--format",
        "-f",
        choices=sorted(SUPPORTED_FORMATS),
        help="Output format. Defaults to --out extension or png.",
    )
    parser.add_argument("--theme", default="default", help="Mermaid theme")
    parser.add_argument(
        "--background-color",
        default="white",
        help="Background color passed to mmdc",
    )
    parser.add_argument("--width", type=int, help="Viewport width for rendering")
    parser.add_argument("--height", type=int, help="Viewport height for rendering")
    parser.add_argument("--scale", type=float, help="Puppeteer device scale factor")
    parser.add_argument("--config", help="Path to a Mermaid config JSON file")
    parser.add_argument(
        "--puppeteer-config", help="Path to a Puppeteer config JSON file"
    )
    parser.add_argument(
        "--allow-npx",
        action="store_true",
        help="Use npx @mermaid-js/mermaid-cli if mmdc is not on PATH.",
    )
    parser.add_argument(
        "--print-command",
        action="store_true",
        help="Print the resolved command before running it.",
    )
    return parser.parse_args()


def extract_mermaid(text: str) -> str:
    stripped = text.strip()
    match = re.fullmatch(r"```(?:mermaid|mmd)?\s*\n(.*?)\n```", stripped, re.S)
    if match:
        return match.group(1).strip() + "\n"
    return text


def resolve_output(input_path: Path, out_arg: str | None, format_arg: str | None) -> tuple[Path, str]:
    if out_arg:
        out_path = Path(out_arg).expanduser()
        suffix = out_path.suffix.lower().lstrip(".")
        out_format = format_arg or (suffix if suffix in SUPPORTED_FORMATS else "png")
    else:
        out_format = format_arg or "png"
        out_path = input_path.with_suffix(f".{out_format}")

    if out_format not in SUPPORTED_FORMATS:
        raise SystemExit(f"Unsupported format: {out_format}")

    if out_path.suffix.lower().lstrip(".") != out_format:
        out_path = out_path.with_suffix(f".{out_format}")

    return out_path, out_format


def find_mmdc(allow_npx: bool) -> list[str]:
    mmdc = shutil.which("mmdc")
    if mmdc:
        return [mmdc]

    if allow_npx:
        npx = shutil.which("npx")
        if npx:
            return [npx, "-y", "@mermaid-js/mermaid-cli"]

    install_hint = (
        "Mermaid CLI was not found. Install it with "
        "`npm install -g @mermaid-js/mermaid-cli`, or rerun with --allow-npx "
        "if network/cached npm package use is acceptable."
    )
    raise SystemExit(install_hint)


def build_command(
    args: argparse.Namespace,
    normalized_input: Path,
    out_path: Path,
    puppeteer_config: Path | None,
) -> list[str]:
    command = find_mmdc(args.allow_npx)
    command.extend(
        [
            "-i",
            str(normalized_input),
            "-o",
            str(out_path),
            "-t",
            args.theme,
            "-b",
            args.background_color,
        ]
    )

    if args.width:
        command.extend(["--width", str(args.width)])
    if args.height:
        command.extend(["--height", str(args.height)])
    if args.scale:
        command.extend(["--scale", str(args.scale)])
    if args.config:
        command.extend(["--configFile", str(Path(args.config).expanduser())])
    if args.puppeteer_config:
        command.extend(
            ["--puppeteerConfigFile", str(Path(args.puppeteer_config).expanduser())]
        )
    elif puppeteer_config:
        command.extend(["--puppeteerConfigFile", str(puppeteer_config)])

    return command


def write_default_puppeteer_config() -> Path:
    config = {
        "args": [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
        ]
    }
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", suffix=".json", delete=False
    ) as temp_file:
        json.dump(config, temp_file)
        temp_file.write("\n")
        return Path(temp_file.name)


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser()
    if not input_path.exists():
        raise SystemExit(f"Input file does not exist: {input_path}")

    source = input_path.read_text(encoding="utf-8")
    normalized = extract_mermaid(source)
    out_path, _out_format = resolve_output(input_path, args.out, args.format)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", suffix=".mmd", delete=False
    ) as temp_file:
        temp_file.write(normalized)
        temp_input = Path(temp_file.name)

    temp_puppeteer_config: Path | None = None
    try:
        if not args.puppeteer_config:
            temp_puppeteer_config = write_default_puppeteer_config()

        command = build_command(args, temp_input, out_path, temp_puppeteer_config)
        if args.print_command:
            print(" ".join(command), flush=True)
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as exc:
            raise SystemExit(
                f"Mermaid render command failed with exit code {exc.returncode}."
            ) from exc
    finally:
        try:
            temp_input.unlink()
        except FileNotFoundError:
            pass
        if temp_puppeteer_config:
            try:
                temp_puppeteer_config.unlink()
            except FileNotFoundError:
                pass

    if not out_path.exists() or out_path.stat().st_size == 0:
        raise SystemExit(f"Render failed or produced an empty file: {out_path}")

    print(f"rendered: {out_path} ({out_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
