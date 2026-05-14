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


def wait_for_api(timeout=120):
    import urllib.request
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=3)
            print("[hf_run] API is ready.")
            return True
        except Exception:
            time.sleep(3)
    print("[hf_run] WARNING: API did not become ready in time, starting dashboard anyway.")
    return False


def run_dashboard():
    wait_for_api()
    os.environ["PORT"] = "7860"
    subprocess.run([sys.executable, "-m", "src.dashboard.app"], cwd=ROOT)


if __name__ == "__main__":
    t = threading.Thread(target=run_api, daemon=True)
    t.start()
    run_dashboard()
