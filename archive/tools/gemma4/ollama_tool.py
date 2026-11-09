from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parents[1] / 'model-tools/gemma4/ollama_tool.py'), run_name='__main__')
