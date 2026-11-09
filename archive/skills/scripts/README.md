# Cross-platform skill administration

Run these commands from the workspace root with Python 3.10 or newer. On Windows,
use `py -3` in place of `python3` if that is your installed Python launcher.

```powershell
py -3 archive/skills/scripts/skill_admin.py audit
py -3 archive/skills/scripts/skill_admin.py install "$env:USERPROFILE/.codex/skills"
py -3 archive/skills/scripts/skill_admin.py doctor "$env:USERPROFILE/.codex/skills"
```

Windows installation defaults to copying. Rerun installation after updating the
source skills; existing installed directories are timestamped backups. `--mode
link` enables symlinks when the machine allows them. macOS/Linux default to links.
The `.sh` files are compatibility wrappers around this Python implementation.

`archive-backups <stamp> --source <runtime-skills-dir>` moves only backup
directories matching the supplied literal timestamp into this skill repository's
`archive/` folder. Review the destination before running it.
