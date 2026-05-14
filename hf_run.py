"""
Hugging Face Spaces entry point.
FastAPI runs on $PORT (7860).
Dashboard is mounted inside FastAPI at /dashboard/
API docs available at /docs
"""
import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("DASH_PREFIX", "/dashboard/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    os.environ["API_BASE"] = f"http://127.0.0.1:{port}"
    subprocess.run([
        sys.executable, "-m", "uvicorn", "src.api.main:app",
        "--host", "0.0.0.0",
        "--port", str(port),
        "--log-level", "info",
    ], cwd=ROOT)
