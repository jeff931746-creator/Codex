#!/usr/bin/env python3
"""Collect YouTube channel subtitles with yt-dlp and build Markdown summaries."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_CHANNEL_URL = "https://www.youtube.com/@GMTK"
DEFAULT_OUTPUT_DIR = (
    Path(__file__).resolve().parents[1] / "output" / "gmtk"
)
DEFAULT_LANGUAGES = "en,en-en,en-orig"
TIMESTAMP_RE = re.compile(
    r"^\d{2}:\d{2}:\d{2}\.\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}\.\d{3}"
)
TAG_RE = re.compile(r"<[^>]+>")
SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass(frozen=True)
class Video:
    video_id: str
    title: str
    url: str
    upload_date: str = ""
    duration: int | None = None

    @property
    def slug(self) -> str:
        date = self.upload_date or "unknown-date"
        title = SAFE_NAME_RE.sub("-", self.title).strip("-").lower()[:80]
        return f"{date}_{self.video_id}_{title or 'untitled'}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download YouTube channel subtitles and combine them into Markdown."
    )
    parser.add_argument("--channel-url", default=DEFAULT_CHANNEL_URL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--languages", default=DEFAULT_LANGUAGES)
    parser.add_argument("--limit", type=int, default=0, help="Limit videos for smoke tests.")
    parser.add_argument("--force", action="store_true", help="Re-download existing transcripts.")
    parser.add_argument(
        "--no-auto-subs",
        action="store_true",
        help="Do not fall back to generated subtitles.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would run without calling yt-dlp.",
    )
    parser.add_argument(
        "--cookies-from-browser",
        metavar="BROWSER",
        help="Pass browser cookies to yt-dlp, for example: chrome, safari, firefox.",
    )
    parser.add_argument(
        "--cookies-file",
        type=Path,
        help="Pass a Netscape-format cookies.txt file to yt-dlp.",
    )
    return parser.parse_args()


def run_json(command: list[str]) -> dict:
    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def run_command(command: list[str]) -> None:
    subprocess.run(command, check=True)


def require_ytdlp(dry_run: bool) -> str:
    ytdlp = shutil.which("yt-dlp")
    if ytdlp:
        return ytdlp
    if dry_run:
        return "yt-dlp"
    raise SystemExit(
        "Missing dependency: yt-dlp is not available on PATH. "
        "Install it outside this workspace, then run this script again."
    )


def print_command(command: Iterable[str]) -> None:
    print(" ".join(shell_quote(part) for part in command))


def shell_quote(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_@%+=:,./-]+", value):
        return value
    return "'" + value.replace("'", "'\"'\"'") + "'"


def ensure_dirs(output_dir: Path) -> tuple[Path, Path]:
    raw_dir = output_dir / "subtitles_raw"
    md_dir = output_dir / "transcripts_md"
    raw_dir.mkdir(parents=True, exist_ok=True)
    md_dir.mkdir(parents=True, exist_ok=True)
    return raw_dir, md_dir


def list_videos(ytdlp: str, channel_url: str, limit: int, dry_run: bool) -> list[Video]:
    command = [
        ytdlp,
        "--flat-playlist",
        "--dump-single-json",
        "--no-warnings",
        channel_url,
    ]
    if dry_run:
        print("Would enumerate channel videos:")
        print_command(command)
        return []

    payload = run_json(command)
    videos: list[Video] = []
    for entry in payload.get("entries", []):
        video_id = entry.get("id")
        if not video_id:
            continue
        title = entry.get("title") or video_id
        url = entry.get("url") or f"https://www.youtube.com/watch?v={video_id}"
        if not url.startswith("http"):
            url = f"https://www.youtube.com/watch?v={video_id}"
        videos.append(
            Video(
                video_id=video_id,
                title=title,
                url=url,
                upload_date=entry.get("upload_date") or "",
                duration=entry.get("duration"),
            )
        )
        if limit and len(videos) >= limit:
            break
    return videos


def save_videos(output_dir: Path, videos: list[Video]) -> None:
    payload = [
        {
            "id": video.video_id,
            "title": video.title,
            "url": video.url,
            "upload_date": video.upload_date,
            "duration": video.duration,
        }
        for video in videos
    ]
    (output_dir / "videos.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def download_subtitles(
    ytdlp: str,
    video: Video,
    raw_dir: Path,
    languages: str,
    include_auto_subs: bool,
    cookies_from_browser: str | None,
    cookies_file: Path | None,
    dry_run: bool,
) -> list[Path]:
    before = set(raw_dir.glob(f"*{video.video_id}*"))
    output_template = str(raw_dir / f"{video.slug}.%(ext)s")
    command = [
        ytdlp,
        "--skip-download",
        "--quiet",
        "--no-progress",
        "--no-warnings",
        "--write-subs",
        "--write-info-json",
        "--sub-langs",
        languages,
        "--sub-format",
        "vtt/best",
        "-o",
        output_template,
        video.url,
    ]
    if include_auto_subs:
        command.insert(3, "--write-auto-subs")
    if cookies_from_browser:
        command[1:1] = ["--cookies-from-browser", cookies_from_browser]
    if cookies_file:
        command[1:1] = ["--cookies", str(cookies_file)]

    if dry_run:
        print(f"Would download subtitles for {video.video_id}:")
        print_command(command)
        return []

    try:
        run_command(command)
    except subprocess.CalledProcessError as exc:
        print(f"[warn] yt-dlp failed for {video.video_id}: {exc}", file=sys.stderr)
        return []

    after = set(raw_dir.glob(f"*{video.video_id}*"))
    return sorted(path for path in after - before if path.suffix == ".vtt")


def find_existing_vtt(raw_dir: Path, video: Video) -> list[Path]:
    return sorted(raw_dir.glob(f"*{video.video_id}*.vtt"))


def vtt_to_text(vtt_path: Path) -> str:
    lines: list[str] = []
    previous = ""
    for raw_line in vtt_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line == "WEBVTT" or line.startswith(("Kind:", "Language:", "NOTE")):
            continue
        if TIMESTAMP_RE.match(line):
            continue
        if re.fullmatch(r"\d+", line):
            continue
        cleaned = TAG_RE.sub("", line)
        cleaned = html.unescape(cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if cleaned and cleaned != previous:
            lines.append(cleaned)
            previous = cleaned
    return "\n".join(lines).strip()


def write_transcript(video: Video, vtt_paths: list[Path], md_dir: Path, force: bool) -> Path | None:
    transcript_path = md_dir / f"{video.slug}.md"
    if transcript_path.exists() and not force:
        return transcript_path
    if not vtt_paths:
        return None

    selected = vtt_paths[0]
    text = vtt_to_text(selected)
    if not text:
        return None

    body = [
        f"# {video.title}",
        "",
        f"- Video ID: `{video.video_id}`",
        f"- URL: {video.url}",
        f"- Source subtitle: `{selected.name}`",
        "",
        "## Transcript",
        "",
        text,
        "",
    ]
    transcript_path.write_text("\n".join(body), encoding="utf-8")
    return transcript_path


def write_index(output_dir: Path, rows: list[dict[str, str]]) -> None:
    index_path = output_dir / "index.csv"
    with index_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "video_id",
                "title",
                "url",
                "upload_date",
                "subtitle_status",
                "transcript_path",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def write_combined(output_dir: Path, transcript_paths: list[Path]) -> None:
    combined_path = output_dir / "all_transcripts.md"
    parts = ["# YouTube Channel Transcripts", ""]
    for path in transcript_paths:
        parts.append(path.read_text(encoding="utf-8").strip())
        parts.append("")
        parts.append("---")
        parts.append("")
    combined_path.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    ytdlp = require_ytdlp(args.dry_run)
    output_dir = args.output_dir.resolve()
    raw_dir, md_dir = ensure_dirs(output_dir)

    videos = list_videos(ytdlp, args.channel_url, args.limit, args.dry_run)
    if args.dry_run:
        print(f"Output directory: {output_dir}")
        print(f"Languages: {args.languages}")
        print(f"Include auto subtitles: {not args.no_auto_subs}")
        print("Dry run complete.")
        return 0

    save_videos(output_dir, videos)
    rows: list[dict[str, str]] = []
    transcript_paths: list[Path] = []

    for index, video in enumerate(videos, start=1):
        print(f"[{index}/{len(videos)}] {video.title} ({video.video_id})")
        transcript_path = md_dir / f"{video.slug}.md"
        vtt_paths = find_existing_vtt(raw_dir, video)
        if args.force or not transcript_path.exists():
            downloaded = download_subtitles(
                ytdlp=ytdlp,
                video=video,
                raw_dir=raw_dir,
                languages=args.languages,
                include_auto_subs=not args.no_auto_subs,
                cookies_from_browser=args.cookies_from_browser,
                cookies_file=args.cookies_file,
                dry_run=False,
            )
            vtt_paths = downloaded or find_existing_vtt(raw_dir, video)

        written = write_transcript(video, vtt_paths, md_dir, args.force)
        status = "ok" if written else "missing"
        if written:
            transcript_paths.append(written)
        rows.append(
            {
                "video_id": video.video_id,
                "title": video.title,
                "url": video.url,
                "upload_date": video.upload_date,
                "subtitle_status": status,
                "transcript_path": str(written.relative_to(output_dir)) if written else "",
            }
        )

    write_index(output_dir, rows)
    write_combined(output_dir, transcript_paths)
    print(f"Done. {len(transcript_paths)}/{len(videos)} transcripts written to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
