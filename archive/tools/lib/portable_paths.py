"""Portable generated filenames and model-provided relative output paths."""
from __future__ import annotations

from pathlib import Path, PureWindowsPath
import re

RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"} | {
    prefix + digit for prefix in ("COM", "LPT") for digit in "123456789¹²³"
}


def filename_stem(value: object, *, limit: int = 120) -> str:
    """Keep names readable while avoiding Windows devices, ADS and separators."""
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", str(value)).strip().rstrip(". ")
    text = text[:limit].rstrip(". ") or "untitled"
    if text.split(".", 1)[0].rstrip(" ").upper() in RESERVED_NAMES:
        text = "_" + text
    return text


def relative_output_path(value: str) -> Path:
    """Reject paths unsafe on Windows even when validation runs on POSIX."""
    windows = PureWindowsPath(value)
    parts = value.replace("\\", "/").split("/")
    if not value or windows.drive or windows.root:
        raise ValueError(f"Output path must be relative: {value!r}")
    for part in parts:
        if (not part or part in {".", ".."} or part.endswith((" ", "."))
                or re.search(r'[<>:"|?*\x00-\x1f]', part)
                or part.split(".", 1)[0].rstrip(" ").upper() in RESERVED_NAMES):
            raise ValueError(f"Invalid output path component: {value!r}")
    return Path(*parts)
