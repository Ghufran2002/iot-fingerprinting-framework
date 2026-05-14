"""
Launch both the FastAPI backend (port 8000) and Plotly Dash dashboard (port 8050).
Run: python run.py
Then open: http://127.0.0.1:8050  (Dashboard)
     and:  http://127.0.0.1:8000/docs  (API docs)
"""
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))


def main():
    print("=" * 60)
    print("  IoT Device Fingerprinting Framework")
    print("  M.Tech Cyber Forensics — NIELIT Srinagar")
    print("  Student: Md Ghufran Alam (NDU202400038)")
    print("=" * 60)

    models_exist = (ROOT / "models" / "scaler.pkl").exists()
    if not models_exist:
        print("\n[!] No trained models found. Running training pipeline first ...")
        result = subprocess.run([sys.executable, "train.py"], cwd=ROOT)
        if result.returncode != 0:
            print("[ERROR] Training failed. Check logs/app.log for details.")
            sys.exit(1)

    print("\n[1/2] Starting FastAPI backend on http://127.0.0.1:8000 ...")
    api_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.api.main:app",
         "--host", "0.0.0.0", "--port", "8000", "--log-level", "warning"],
        cwd=ROOT,
    )

    time.sleep(2)

    print("[2/2] Starting Plotly Dash dashboard on http://127.0.0.1:8050 ...")
    dash_proc = subprocess.Popen(
        [sys.executable, "-m", "src.dashboard.app"],
        cwd=ROOT,
    )

    time.sleep(3)
    print("\n[3/3] Opening browser ...")
    webbrowser.open("http://127.0.0.1:8050")
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8000/docs")

    print("\n" + "=" * 60)
    print("  Dashboard:  http://127.0.0.1:8050")
    print("  API Docs:   http://127.0.0.1:8000/docs")
    print("  Press Ctrl+C to stop.")
    print("=" * 60 + "\n")

    try:
        api_proc.wait()
    except KeyboardInterrupt:
        print("\n[*] Shutting down ...")
        api_proc.terminate()
        dash_proc.terminate()
        print("[*] Done.")


if __name__ == "__main__":
    main()
