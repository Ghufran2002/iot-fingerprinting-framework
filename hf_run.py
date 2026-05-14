"""
Hugging Face Spaces entry point.
API runs on port 8000 (internal), Dashboard on port 7860 (public).
"""
import os
import sys
import time
import threading
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("API_BASE", "http://127.0.0.1:8000")


def run_api():
    subprocess.run([
        sys.executable, "-m", "uvicorn", "src.api.main:app",
        "--host", "0.0.0.0", "--port", "8000", "--log-level", "warning"
    ], cwd=ROOT)


def run_dashboard():
    time.sleep(5)
    os.environ["PORT"] = "7860"
    subprocess.run([sys.executable, "-m", "src.dashboard.app"], cwd=ROOT)


if __name__ == "__main__":
    t = threading.Thread(target=run_api, daemon=True)
    t.start()
    run_dashboard()
