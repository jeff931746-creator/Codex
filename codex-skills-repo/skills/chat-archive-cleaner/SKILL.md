---
name: chat-archive-cleaner
description: Save important parts of the current Codex conversation to local files and remove irrelevant chatter from the saved result. Use when the user asks to save, archive, record, summarize, compact, or clean up a chat; when a long thread should be converted into a reusable local note; or when Codex should keep only decisions, tasks, code paths, commands, constraints, and outputs while dropping greetings, repetition, failed tangents, and other low-value dialogue.
---

# Chat Archive Cleaner

## Overview

Save the current conversation into a local archive that remains useful later. Prefer a compact, structured record of decisions and next actions over a raw transcript.

## Default Behavior

When this skill is triggered:

1. Infer whether the user wants a concise archive, a fuller transcript, or both.
2. Preserve high-signal content:
   - user goals
   - constraints and preferences
   - accepted decisions
   - file paths, commands, APIs, URLs, and identifiers that matter later
   - unresolved questions, follow-ups, and next steps
3. Remove low-signal content from the saved output unless the user explicitly asks for a full transcript:
   - greetings and pleasantries
   - repeated restatements
   - abandoned false starts
   - filler acknowledgements
   - duplicate code or repeated command output summaries
4. Save the result under a timestamped filename.

Do not claim background or hook-based automation that the environment does not actually provide. If the user asks for "automatic" saving, interpret that as "perform the archive step immediately when asked" unless a separate automation is explicitly requested.

## Archive Format

Prefer Markdown. Use this structure unless the user asks for a different format:

```markdown
# Chat Archive

## Session
- Date:
- User goal:
- Outcome:

## Key Decisions
- ...

## Important Context
- ...

## Files And Commands
- ...

## Next Actions
- ...

## Clean Transcript
Optional. Include only if the user asked for a fuller record.
```

Keep the archive readable by a future human. Do not store raw chain-of-thought. Summarize reasoning into conclusions, tradeoffs, and action points.

## Storage Rules

Default output directory:

- `./chat-archives` relative to the current workspace when the user does not specify a path

Filename pattern:

- `YYYYMMDD-HHMMSS-topic.md`

If a topic is not obvious, use `chat-archive`.

If the target directory does not exist, create it.

## Cleanup Rules

Apply these rules when deciding what to delete from the saved artifact:

- Keep facts that would change future work.
- Keep concrete requests and accepted answers.
- Keep errors, blockers, and resolutions.
- Keep exact file paths and commands when they influenced the result.
- Drop small-talk unless it changes intent.
- Drop repeated explanations after the final accepted version exists.
- Drop speculative branches that were not used, unless they explain an important rejection.

If the conversation contains both useful content and noise mixed together, rewrite into a clean narrative instead of preserving the original order verbatim.

## Workflow

1. Determine output scope.
   If the user said "保存聊天" or similar without more detail, save a concise archive plus a short action list.
2. Build the archive content.
   Extract goals, decisions, paths, commands, outputs, and next actions.
3. Clean the archive.
   Remove repetition and irrelevant chatter.
4. Save locally.
   Use `scripts/save_chat_archive.py` when a deterministic file write is helpful.
5. Report back.
   Tell the user where the file was saved and whether the result is summary-only or summary-plus-transcript.

## Script

Use `scripts/save_chat_archive.py` to write the archive deterministically.

Example:

```bash
python3 scripts/save_chat_archive.py \
  --output-dir ./chat-archives \
  --topic "skill-design" \
  --title "Chat Archive" \
  --body-file /tmp/archive-body.md
```

The script creates the directory if needed, slugifies the topic, writes a timestamped Markdown file, and prints the saved path.
