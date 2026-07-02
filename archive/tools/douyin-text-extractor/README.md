# Douyin Text Extractor

Extract public visible copy and metadata from Douyin share/video links.

This tool is intentionally conservative: it reads text surfaces exposed in the public page payload, such as title/description, hashtags, author metadata, share metadata, and any subtitle/caption-like fields already present in page JSON. It is not a full audio transcription tool.

## Usage

```bash
python3 archive/tools/douyin-text-extractor/scripts/extract_douyin_text.py 'https://v.douyin.com/xxxx/'
```

Markdown output:

```bash
python3 archive/tools/douyin-text-extractor/scripts/extract_douyin_text.py 'https://v.douyin.com/xxxx/' --format md
```

Parse saved HTML:

```bash
python3 archive/tools/douyin-text-extractor/scripts/extract_douyin_text.py 'https://www.douyin.com/video/123' --html-file page.html
```

Save fetched HTML for debugging:

```bash
python3 archive/tools/douyin-text-extractor/scripts/extract_douyin_text.py 'https://v.douyin.com/xxxx/' --save-html tmp/douyin-page.html
```

Paste a full Douyin share command; the tool keeps the visible share copy as a fallback:

```bash
python3 archive/tools/douyin-text-extractor/scripts/extract_douyin_text.py '复制打开抖音，看看【作者的作品】标题 https://v.douyin.com/xxxx/'
```

Use browser cookies when a public page requires session state:

```bash
python3 archive/tools/douyin-text-extractor/scripts/extract_douyin_text.py 'https://v.douyin.com/xxxx/' --cookie 'name=value; other=value'
```

Use a real browser session when Douyin returns an anti-bot challenge:

```bash
python3 archive/tools/douyin-text-extractor/scripts/extract_douyin_text.py 'https://v.douyin.com/xxxx/' --browser --format md
```

For pages that require login or an interactive check, run once with a visible persistent profile:

```bash
python3 archive/tools/douyin-text-extractor/scripts/extract_douyin_text.py 'https://v.douyin.com/xxxx/' \
  --browser --show-browser --user-data-dir /tmp/douyin-text-profile --format md
```

After login/check succeeds, reuse the same profile without showing the browser:

```bash
python3 archive/tools/douyin-text-extractor/scripts/extract_douyin_text.py 'https://v.douyin.com/xxxx/' \
  --browser --user-data-dir /tmp/douyin-text-profile --format md
```

If local Python certificates are broken but `curl` works, retry explicitly with:

```bash
python3 archive/tools/douyin-text-extractor/scripts/extract_douyin_text.py 'https://v.douyin.com/xxxx/' --insecure
```

## Output Status

- `ok`: structured page data was parsed.
- `html_meta_only`: browser/HTML meta tags were parsed, but no full video object was recognized.
- `blocked_by_challenge`: Douyin returned an anti-bot challenge page.
- `no_structured_payload`: HTML was fetched, but no parseable structured payload was found.
- `metadata_only`: JSON was found, but no video object was recognized.
- `fetch_error`: the page could not be fetched.

## Boundaries

- Short links and public page metadata usually work when Douyin serves a normal share payload.
- A full spoken transcript requires subtitles in the page payload or a separate ASR workflow.
- If Douyin returns an anti-bot challenge, the tool reports that state instead of pretending extraction succeeded.
- `--browser` uses normal browser rendering/session state; it does not bypass private content, login requirements, or CAPTCHA decisions.
