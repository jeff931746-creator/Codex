# Workspace Guard

Run `python tools/workspace-guard/check_paths.py <path> [...]` from the checkout root before file-changing commands. Python 3.10+ is required. The guard derives the workspace from its own file, resolves parent traversal and symbolic links, and accepts only that checkout and OS temporary directories. It returns 0 for allowed paths, 1 for external destinations, or 64 for a missing argument.

The same command runs on Windows, macOS and Linux. `check-paths.sh` remains a compatibility wrapper for existing Unix callers. See [Windows setup](../../docs/windows.md) for runtime hook generation.
