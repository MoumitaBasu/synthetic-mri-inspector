import sys
import os
from pathlib import Path

# Add src to sys.path
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

# Patch environment if needed
os.environ["PYTHONPATH"] = f"{src_path}{os.pathsep}{os.environ.get('PYTHONPATH', '')}"

if __name__ == "__main__":
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", "app.py", "--server.port=8501", "--server.headless=true"]
    sys.exit(stcli.main())
