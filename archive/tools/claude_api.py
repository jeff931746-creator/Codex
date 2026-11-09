"""Compatibility import for the maintained scripts.claude_api module."""
from pathlib import Path
import runpy
import sys
_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))
if __name__ == '__main__':
    runpy.run_module('archive.tools.scripts.claude_api', run_name='__main__')
else:
    from archive.tools.scripts.claude_api import *
