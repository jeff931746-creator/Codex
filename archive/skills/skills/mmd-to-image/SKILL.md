---
name: mmd-to-image
description: Render Mermaid diagrams from `.mmd` files or Mermaid fenced code blocks into image files such as PNG, SVG, or PDF. Use when Codex is asked to save, export, convert, render, preview, or batch-generate Mermaid/MMD diagrams as images, especially when the user wants a repeatable local workflow instead of re-discovering `mmdc` commands.
---

# MMD to Image

## Overview

Use the bundled `scripts/render_mmd.py` wrapper for deterministic Mermaid rendering. It normalizes common `.mmd` inputs, chooses the available Mermaid CLI renderer, creates the output directory, and reports the exact command when dependencies are missing.

## Quick Start

Render a single diagram:

```bash
python3 /path/to/mmd-to-image/scripts/render_mmd.py diagram.mmd --out diagram.png
```

Render as SVG:

```bash
python3 /path/to/mmd-to-image/scripts/render_mmd.py diagram.mmd --format svg
```

Use `--allow-npx` only when `mmdc` is not installed and the user is willing to let npm fetch or use the cached `@mermaid-js/mermaid-cli` package:

```bash
python3 /path/to/mmd-to-image/scripts/render_mmd.py diagram.mmd --out diagram.png --allow-npx
```

## Workflow

1. Locate the `.mmd` source or extract Mermaid content from the user's provided Markdown/code block.
2. Decide the output path:
   - If the user provides an output path, use it.
   - Otherwise write beside the source using the requested format, defaulting to `.png`.
3. Run `scripts/render_mmd.py` instead of hand-writing `mmdc` commands.
4. If the script reports that `mmdc` is missing, ask whether to install Mermaid CLI or rerun with `--allow-npx`; do not silently install network dependencies.
5. After rendering, verify the image exists and has non-zero size. For PNG/PDF outputs, inspect visually when layout quality matters.

## Batch Rendering

Use a shell loop around the wrapper when the user asks for multiple files:

```bash
for file in *.mmd; do
  python3 /path/to/mmd-to-image/scripts/render_mmd.py "$file" --format png
done
```

Prefer rendering into a dedicated output folder for many files:

```bash
mkdir -p rendered
for file in *.mmd; do
  python3 /path/to/mmd-to-image/scripts/render_mmd.py "$file" --out "rendered/${file%.mmd}.png"
done
```

## Notes

- The script supports `.mmd` files that contain either raw Mermaid text or a single fenced block such as ```mermaid.
- PNG/PDF rendering needs a working browser environment through Mermaid CLI/Puppeteer.
- SVG is usually the fastest format for documentation and version control.
