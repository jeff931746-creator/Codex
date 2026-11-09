#!/usr/bin/env python3
"""Portable skill audit, installation and runtime-link diagnostics.

Windows defaults to copies so Developer Mode/admin symlink rights are unnecessary.
Existing installations are backed up before replacement. Run with --help.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def audit() -> int:
    errors = 0
    for source in sorted(SKILLS.iterdir()):
        if not source.is_dir():
            continue
        if not (source / "SKILL.md").is_file():
            print(f"missing: {source.name}/SKILL.md")
            errors += 1
        else:
            print(f"ok: {source.name}/SKILL.md")
        if not (source / "agents/openai.yaml").is_file():
            print(f"warn: {source.name}/agents/openai.yaml")
    return bool(errors)


def install(target: Path, name: str | None, mode: str) -> int:
    sources = [SKILLS / name] if name else sorted(SKILLS.iterdir())
    if name and (Path(name).name != name or name in {".", ".."}):
        raise SystemExit("Skill name must be one directory name")
    if name and not (sources[0] / "SKILL.md").is_file():
        raise SystemExit(f"Missing skill: {name}")
    target = target.expanduser().resolve()
    if target == SKILLS or SKILLS in target.parents:
        raise SystemExit("Installation target must be outside the skill source tree")
    target.mkdir(parents=True, exist_ok=True)
    for source in sources:
        if not source.is_dir() or not (source / "SKILL.md").is_file():
            continue
        dest = target / source.name
        if dest.is_symlink() and dest.resolve() == source.resolve() and mode == "link":
            print(f"ok: {dest}")
            continue
        if dest.exists() or dest.is_symlink():
            backup = dest.with_name(dest.name + ".backup-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
            dest.rename(backup)
            print(f"backup: {backup}")
        if mode == "link":
            dest.symlink_to(source, target_is_directory=True)
        else:
            shutil.copytree(source, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "node_modules", "evals", "tests", "tmp"))
        print(f"{mode}: {dest}")
    return 0


def doctor(target: Path) -> int:
    errors = audit()
    for source in sorted(SKILLS.iterdir()):
        if not (source / "SKILL.md").is_file():
            continue
        dest = target.expanduser() / source.name
        if not (dest / "SKILL.md").is_file():
            print(f"missing: {dest}")
            errors = 1
        elif dest.is_symlink() and dest.resolve() != source.resolve():
            print(f"wrong-link: {dest}")
            errors = 1
        elif not dest.is_symlink():
            print(f"copy: {dest} (rerun install after source updates)")
    return int(errors)


def main() -> int:
    import os
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("audit")
    p = sub.add_parser("install")
    p.add_argument("target", type=Path)
    p.add_argument("name", nargs="?")
    p.add_argument("--mode", choices=["copy", "link"], default="copy" if os.name == "nt" else "link")
    p = sub.add_parser("doctor")
    p.add_argument("target", nargs="?", type=Path, default=Path.home() / ".codex/skills")
    p = sub.add_parser("archive-backups")
    p.add_argument("stamp", help="Exact backup timestamp suffix to move")
    p.add_argument("--source", type=Path, default=Path.home() / ".codex/skills")
    args = parser.parse_args()
    if args.action == "audit":
        return int(audit())
    if args.action == "install":
        return install(args.target, args.name, args.mode)
    if args.action == "doctor":
        return doctor(args.target)
    if not args.stamp or any(c in args.stamp for c in '/\\*?[]'):
        parser.error("stamp must be a literal timestamp suffix")
    target = ROOT / "archive" / ("runtime-backups-" + args.stamp)
    for source in args.source.expanduser().glob("*.backup-" + args.stamp):
        target.mkdir(parents=True, exist_ok=True)
        dest = target / source.name
        if dest.exists():
            raise SystemExit(f"Refusing to overwrite: {dest}")
        source.rename(dest)
        print(f"archived: {source.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
