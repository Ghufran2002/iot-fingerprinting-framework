"""
Hugging Face Spaces entry point.
FastAPI runs on $PORT (7860).
Train models on first boot if not already present.
"""
import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))

    # Train models if missing (handles cold starts after Space restart)
    if not (ROOT / "models" / "scaler.pkl").exists():
        print("[hf_run] Models not found — running train.py ...")
        result = subprocess.run([sys.executable, "train.py"], cwd=ROOT)
        if result.returncode != 0:
            print("[hf_run] Training failed — API will start without models.")

    subprocess.run([
        sys.executable, "-m", "uvicorn", "src.api.main:app",
        "--host", "0.0.0.0",
        "--port", str(port),
        "--log-level", "info",
    ], cwd=ROOT)
