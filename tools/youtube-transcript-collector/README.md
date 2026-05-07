# YouTube Transcript Collector

Collect subtitles from every video on a YouTube channel and build a local transcript corpus.

Default target:

```text
https://www.youtube.com/@GMTK
```

## Dependency

This tool uses the system `yt-dlp` command and Python standard library only.

It does not install or vendor `yt-dlp` into this workspace. If `yt-dlp` is missing, install it outside the workspace with your preferred system package manager.

## Usage

Dry run:

```bash
python3 tools/youtube-transcript-collector/scripts/collect_youtube_subtitles.py --dry-run
```

Collect GMTK subtitles:

```bash
python3 tools/youtube-transcript-collector/scripts/collect_youtube_subtitles.py
```

Collect a limited sample:

```bash
python3 tools/youtube-transcript-collector/scripts/collect_youtube_subtitles.py --limit 5
```

Use only manually authored subtitles:

```bash
python3 tools/youtube-transcript-collector/scripts/collect_youtube_subtitles.py --no-auto-subs
```

If YouTube asks for sign-in or bot confirmation, use your local browser session:

```bash
python3 tools/youtube-transcript-collector/scripts/collect_youtube_subtitles.py --limit 5 --cookies-from-browser chrome
```

Or use an exported cookies file:

```bash
python3 tools/youtube-transcript-collector/scripts/collect_youtube_subtitles.py --cookies-file /path/to/cookies.txt
```

## Output

By default, outputs are written to:

```text
tools/youtube-transcript-collector/output/gmtk/
```

Generated files:

- `videos.json`: normalized video list from the channel.
- `index.csv`: video metadata and subtitle status.
- `subtitles_raw/`: raw `.vtt` subtitles and `.info.json` metadata.
- `transcripts_md/`: one cleaned Markdown transcript per video.
- `all_transcripts.md`: all cleaned transcripts combined into one file.

## Notes

- The first full run can take a long time because it has to enumerate and fetch a channel archive.
- Some videos may have no subtitles in the requested language.
- The default language selector is `en,en-en,en-orig`, which keeps the run focused on English tracks and avoids downloading every translated subtitle derived from English.
- Use this for personal research and respect YouTube's terms and creator rights.
