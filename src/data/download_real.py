"""
Download N-BaIoT dataset from UCI ML Repository.
Run once: python src/data/download_real.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.data.real_loader import download_nbaiot
from src.utils.logger import logger

if __name__ == "__main__":
    force = "--force" in sys.argv
    success = download_nbaiot(force=force)
    if success:
        logger.info("Download complete. Now run: python train.py --real")
    else:
        logger.error("Download failed. See instructions above.")
        sys.exit(1)
