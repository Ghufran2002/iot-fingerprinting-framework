"""
Training entry point.

Usage:
  python train.py              # synthetic data (default — always works)
  python train.py --real       # real N-BaIoT data (download first)
  python train.py --hybrid     # real N-BaIoT + synthetic fill-in (recommended)
  python train.py --download   # download N-BaIoT then train hybrid
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.models.trainer import run_training


def parse_args():
    p = argparse.ArgumentParser(description="IoT Device Fingerprinting — Training Pipeline")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--real",     action="store_true", help="Train on real N-BaIoT data only")
    g.add_argument("--hybrid",   action="store_true", help="Real N-BaIoT + synthetic fill-in (recommended)")
    g.add_argument("--synthetic",action="store_true", help="Train on synthetic data (default)")
    p.add_argument("--download", action="store_true", help="Download N-BaIoT before training")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.download:
        from src.data.real_loader import download_nbaiot
        ok = download_nbaiot()
        if not ok:
            print("\n[ERROR] Download failed. See instructions above.")
            sys.exit(1)
        if not args.real and not args.hybrid:
            args.hybrid = True

    mode = "synthetic"
    if args.real:
        mode = "real"
    elif args.hybrid:
        mode = "hybrid"

    print(f"\n{'='*60}")
    print(f"  Training mode: {mode.upper()}")
    print(f"{'='*60}\n")

    fp_results, anomaly_eval = run_training(mode=mode)

    print("\n=== Fingerprinting Results ===")
    for name, res in fp_results.items():
        print(f"  {name:25s}  Acc={res['accuracy']:.4f}  ROC-AUC={res['roc_auc']:.4f}")

    print("\n=== Anomaly Detection Results ===")
    for res in anomaly_eval:
        print(f"  {res['device']:20s}  AUC={res['roc_auc']:.4f}  F1={res['f1']:.4f}  "
              f"Normal={res['mean_normal_score']:.3f}  Attack={res['mean_anomaly_score']:.3f}")

    print(f"\nTraining complete [{mode}]. Start the system: python run.py")
