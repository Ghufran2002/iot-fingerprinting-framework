"""
End-to-end training pipeline.
Phase 1: Data generation + preprocessing
Phase 2: Model training (fingerprinter + anomaly detectors)
Phase 3: Evaluation + plots
Phase 4: Save all artefacts
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize

from src.data.generator import generate_dataset
from src.data.preprocessor import Preprocessor
from src.data.real_loader import load_real_dataset, save_real_dataset
from src.models.fingerprinter import DeviceFingerprinter
from src.models.anomaly_detector import AnomalyDetector
from src.features.extractor import FEATURE_NAMES, DEVICE_TYPES, DEVICE_LABEL_MAP
from src.utils.logger import logger

PLOTS_DIR = Path(__file__).resolve().parents[2] / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

sns.set_theme(style="darkgrid", palette="muted")
COLORS = sns.color_palette("Set2", 8)


# ---------------------------------------------------------------------------
# Plotting helpers
# ---------------------------------------------------------------------------
def _plot_confusion_matrix(cm, model_name: str):
    fig, ax = plt.subplots(figsize=(10, 8))
    short = [d.replace('smart_', '').replace('_', '\n') for d in DEVICE_TYPES]
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=short, yticklabels=short,
                linewidths=0.5, linecolor='grey')
    ax.set_title(f'Confusion Matrix — {model_name.replace("_", " ").title()}',
                 fontsize=14, fontweight='bold', pad=12)
    ax.set_ylabel('True Label', fontsize=11)
    ax.set_xlabel('Predicted Label', fontsize=11)
    plt.tight_layout()
    fig.savefig(PLOTS_DIR / f"cm_{model_name}.png", dpi=150)
    plt.close(fig)
    logger.info(f"Saved: cm_{model_name}.png")


def _plot_roc_curves(X_test, y_test, fingerprinter: DeviceFingerprinter):
    rf = fingerprinter._models['random_forest']
    y_bin = label_binarize(y_test, classes=list(range(len(DEVICE_TYPES))))
    y_proba = rf.predict_proba(X_test)

    fig, ax = plt.subplots(figsize=(10, 8))
    for i, device in enumerate(DEVICE_TYPES):
        fpr, tpr, _ = roc_curve(y_bin[:, i], y_proba[:, i])
        roc_auc = auc(fpr, tpr)
        short = device.replace('smart_', '').replace('_', ' ').title()
        ax.plot(fpr, tpr, color=COLORS[i], lw=2,
                label=f'{short} (AUC = {roc_auc:.3f})')

    ax.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.6)
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.02])
    ax.set_xlabel('False Positive Rate', fontsize=12)
    ax.set_ylabel('True Positive Rate', fontsize=12)
    ax.set_title('ROC Curves — Random Forest (One-vs-Rest)', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right', fontsize=9)
    plt.tight_layout()
    fig.savefig(PLOTS_DIR / "roc_curves.png", dpi=150)
    plt.close(fig)
    logger.info("Saved: roc_curves.png")


def _plot_feature_importance(fingerprinter: DeviceFingerprinter):
    if fingerprinter.feature_importances_ is None:
        return
    top_n = 15
    importances = fingerprinter.feature_importances_
    indices = np.argsort(importances)[::-1][:top_n]
    feat_names = [FEATURE_NAMES[i].replace('_', ' ') for i in indices]
    feat_vals  = importances[indices]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(feat_names[::-1], feat_vals[::-1], color=COLORS[0], edgecolor='white')
    ax.set_xlabel('Feature Importance (Gini)', fontsize=11)
    ax.set_title('Top 15 Feature Importances — Random Forest', fontsize=14, fontweight='bold')
    for bar, val in zip(bars, feat_vals[::-1]):
        ax.text(val + 0.001, bar.get_y() + bar.get_height() / 2,
                f'{val:.4f}', va='center', fontsize=8)
    plt.tight_layout()
    fig.savefig(PLOTS_DIR / "feature_importance.png", dpi=150)
    plt.close(fig)
    logger.info("Saved: feature_importance.png")


def _plot_model_comparison(results: dict):
    names = [n.replace('_', '\n') for n in results]
    accs  = [results[n]['accuracy'] for n in results]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(names, accs, color=COLORS[:len(names)], edgecolor='white', width=0.5)
    ax.set_ylim(0.85, 1.02)
    ax.set_ylabel('Test Accuracy', fontsize=11)
    ax.set_title('Model Comparison — Device Fingerprinting', fontsize=14, fontweight='bold')
    for bar, acc in zip(bars, accs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.002,
                f'{acc:.4f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    plt.tight_layout()
    fig.savefig(PLOTS_DIR / "model_comparison.png", dpi=150)
    plt.close(fig)
    logger.info("Saved: model_comparison.png")


def _plot_anomaly_scores(anomaly_eval: list):
    devices = [r['device'] for r in anomaly_eval]
    mean_normal  = [r['mean_normal_score']  for r in anomaly_eval]
    mean_anomaly = [r['mean_anomaly_score'] for r in anomaly_eval]
    x = np.arange(len(devices))
    short = [d.replace('smart_', '').replace('_', '\n') for d in devices]

    fig, ax = plt.subplots(figsize=(12, 5))
    bars1 = ax.bar(x - 0.2, mean_normal,  0.35, label='Normal',   color='steelblue',  edgecolor='white')
    bars2 = ax.bar(x + 0.2, mean_anomaly, 0.35, label='Anomalous', color='tomato',     edgecolor='white')
    ax.axhline(y=0.75, color='red', linestyle='--', linewidth=1.5, label='Alert Threshold (0.75)')
    ax.set_xticks(x)
    ax.set_xticklabels(short, fontsize=9)
    ax.set_ylabel('Mean Anomaly Score', fontsize=11)
    ax.set_title('Per-Device Anomaly Score Distribution', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 1.1)
    ax.legend(fontsize=10)
    plt.tight_layout()
    fig.savefig(PLOTS_DIR / "anomaly_scores.png", dpi=150)
    plt.close(fig)
    logger.info("Saved: anomaly_scores.png")


def _plot_device_distribution(df: pd.DataFrame):
    counts = df.groupby('device_type').size()
    short = [d.replace('smart_', '').replace('_', ' ').title() for d in counts.index]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.pie(counts.values, labels=short, colors=COLORS,
           autopct='%1.1f%%', startangle=90,
           wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
    ax.set_title('Dataset — Device Type Distribution', fontsize=13, fontweight='bold')
    plt.tight_layout()
    fig.savefig(PLOTS_DIR / "device_distribution.png", dpi=150)
    plt.close(fig)
    logger.info("Saved: device_distribution.png")


def _plot_precision_recall_f1(results: dict):
    metrics = ['precision', 'recall', 'f1-score']
    model_names = list(results.keys())
    x = np.arange(len(metrics))
    width = 0.8 / len(model_names)

    fig, ax = plt.subplots(figsize=(9, 5))
    for i, name in enumerate(model_names):
        report = results[name]['report']
        vals = [report['macro avg'][m] for m in metrics]
        offset = (i - len(model_names) / 2 + 0.5) * width
        bars = ax.bar(x + offset, vals, width, label=name.replace('_', ' ').title(),
                      color=COLORS[i % len(COLORS)], edgecolor='white')

    ax.set_xticks(x)
    ax.set_xticklabels(['Macro Precision', 'Macro Recall', 'Macro F1'], fontsize=11)
    ax.set_ylim(0.85, 1.02)
    ax.set_ylabel('Score', fontsize=11)
    ax.set_title('Precision / Recall / F1 — Model Comparison', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    plt.tight_layout()
    fig.savefig(PLOTS_DIR / "precision_recall_f1.png", dpi=150)
    plt.close(fig)
    logger.info("Saved: precision_recall_f1.png")


# ---------------------------------------------------------------------------
# Main training function
# ---------------------------------------------------------------------------
def _build_dataset(mode: str) -> pd.DataFrame:
    """Build training dataset based on mode: synthetic | real | hybrid."""
    if mode == "synthetic":
        logger.info("Phase 1: Generating synthetic dataset ...")
        df = generate_dataset(save=True)

    elif mode == "real":
        logger.info("Phase 1: Loading real N-BaIoT dataset ...")
        df, missing = load_real_dataset()
        if missing:
            logger.warning(f"Missing {len(missing)} device types — consider --hybrid mode.")
        save_real_dataset(df)

    elif mode == "hybrid":
        logger.info("Phase 1: Building hybrid dataset (real N-BaIoT + synthetic fill-in) ...")
        try:
            df_real, missing = load_real_dataset()
            logger.info(f"  Real: {len(df_real)} flows")
        except FileNotFoundError as e:
            logger.error(str(e))
            raise

        if missing:
            logger.info(f"  Synthesising {len(missing)} missing device types: {missing}")
            # Generate synthetic data only for missing device types
            df_synth_all = generate_dataset(save=False)
            df_synth = df_synth_all[df_synth_all['device_type'].isin(missing)]
            df = pd.concat([df_real, df_synth], ignore_index=True)
        else:
            df = df_real

        save_real_dataset(df)
        logger.info(f"  Hybrid total: {len(df)} flows")

    else:
        raise ValueError(f"Unknown mode: {mode}")

    return df


def run_training(mode: str = "synthetic"):
    logger.info("=" * 60)
    logger.info("IoT Device Fingerprinting Framework — Training Pipeline")
    logger.info("=" * 60)

    # Phase 1 — Data
    df = _build_dataset(mode)
    logger.info(f"Dataset: {df.shape[0]} flows, {df.shape[1]} columns")
    _plot_device_distribution(df)

    # Phase 1b — Preprocessing
    logger.info("Phase 1b: Preprocessing ...")
    prep = Preprocessor()
    X_train, X_val, X_test, y_train, y_val, y_test = prep.fit_transform(df)
    prep.save()

    # Phase 2a — Device Fingerprinting
    logger.info("Phase 2a: Training device fingerprinting models ...")
    fp = DeviceFingerprinter()
    val_results = fp.train(X_train, y_train, X_val, y_val)

    # Phase 2b — Anomaly Detection
    logger.info("Phase 2b: Training per-device anomaly detectors ...")
    X_raw = df[FEATURE_NAMES]
    ad = AnomalyDetector()
    device_labels = df['device_type'].values
    is_anomaly    = df['is_anomaly'].values
    X_scaled_all  = prep.transform(X_raw)
    ad.train(X_scaled_all, device_labels, is_anomaly)

    # Phase 3 — Evaluation
    logger.info("Phase 3: Evaluating all models ...")
    fp_results = fp.evaluate(X_test, y_test)

    for name, res in fp_results.items():
        _plot_confusion_matrix(res['confusion_matrix'], name)

    _plot_roc_curves(X_test, y_test, fp)
    _plot_feature_importance(fp)
    _plot_model_comparison(fp_results)
    _plot_precision_recall_f1(fp_results)

    # Anomaly evaluation
    anomaly_eval = []
    for device in DEVICE_TYPES:
        mask_normal  = (df['device_type'] == device) & (df['is_anomaly'] == 0)
        mask_anomaly = (df['device_type'] == device) & (df['is_anomaly'] == 1)
        if mask_normal.sum() == 0 or mask_anomaly.sum() == 0:
            continue
        X_n = prep.transform(df[mask_normal][FEATURE_NAMES])
        X_a = prep.transform(df[mask_anomaly][FEATURE_NAMES])
        eval_res = ad.evaluate(X_n, X_a, device)
        anomaly_eval.append(eval_res)
        logger.info(f"Anomaly [{device}]: AUC={eval_res['roc_auc']:.4f}  "
                    f"F1={eval_res['f1']:.4f}  "
                    f"Normal={eval_res['mean_normal_score']:.3f}  "
                    f"Attack={eval_res['mean_anomaly_score']:.3f}")

    _plot_anomaly_scores(anomaly_eval)

    # Phase 4 — Save
    logger.info("Phase 4: Saving models ...")
    fp.save()
    ad.save()

    # Summary
    logger.info("=" * 60)
    logger.info("TRAINING COMPLETE — Results Summary")
    logger.info("=" * 60)
    for name, res in fp_results.items():
        logger.info(f"  {name:25s} Acc={res['accuracy']:.4f}  ROC-AUC={res['roc_auc']:.4f}")
    logger.info(f"Plots saved to: {PLOTS_DIR}")
    logger.info("=" * 60)

    return fp_results, anomaly_eval
