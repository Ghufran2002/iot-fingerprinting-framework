"""
SHAP Explainability for IoT Device Fingerprinting.
Generates:
  plots/shap_summary.png        — global feature importance (beeswarm)
  plots/shap_bar.png            — mean |SHAP| bar chart
  plots/shap_device_heatmap.png — per-device SHAP heatmap
Run: python explain_model.py
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import shap
import joblib
from pathlib import Path

from src.features.extractor import FEATURE_NAMES, DEVICE_TYPES
from src.data.generator import generate_dataset
from src.data.preprocessor import Preprocessor
from src.utils.logger import logger

PLOTS_DIR = Path("plots")
PLOTS_DIR.mkdir(exist_ok=True)

DARK_BG   = "#0d0f14"
CYAN      = "#00d4e8"
PURPLE    = "#a05aff"
GREEN     = "#00e580"
TEXT      = "#c9d1e0"
SURFACE   = "#13161e"
BORDER    = "#1f2535"

PALETTE = [
    "#00d4e8","#a05aff","#00e580","#ffcd43",
    "#ff4757","#00b8c8","#7c4fcc","#ff9f43"
]

logger.info("Loading models ...")
models_dir = Path("models")
rf         = joblib.load(models_dir / "fingerprinter_random_forest.pkl")
scaler     = joblib.load(models_dir / "scaler.pkl")

logger.info("Generating dataset for SHAP ...")
df = generate_dataset(save=False)
X  = df[FEATURE_NAMES].copy()
X.replace([float('inf'), float('-inf')], float('nan'), inplace=True)
X.fillna(X.median(), inplace=True)
X = X.clip(lower=0)
X_scaled = scaler.transform(X)
y_labels  = df['device_type'].values

# Use a balanced sample — 50 per device = 400 total (SHAP is slow on large data)
sample_idx = []
for dev in DEVICE_TYPES:
    idx = np.where(y_labels == dev)[0]
    sample_idx.extend(np.random.default_rng(42).choice(idx, size=min(50, len(idx)), replace=False))
sample_idx = np.array(sample_idx)

X_sample   = X_scaled[sample_idx]
y_sample   = y_labels[sample_idx]

logger.info(f"Computing SHAP values for {len(X_sample)} samples (this takes ~30s) ...")
explainer   = shap.TreeExplainer(rf)
shap_values = explainer.shap_values(X_sample)

# Normalise to (n_classes, n_samples, n_features) regardless of SHAP version
sv_arr = np.array(shap_values)
if sv_arr.ndim == 3 and sv_arr.shape[0] == len(X_sample):
    # SHAP >= 0.40 returns (n_samples, n_features, n_classes) — transpose
    sv_arr = sv_arr.transpose(2, 0, 1)   # → (n_classes, n_samples, n_features)
elif sv_arr.ndim == 3 and sv_arr.shape[0] == len(DEVICE_TYPES):
    pass  # already (n_classes, n_samples, n_features)
# sv_arr is now always (8, 400, 37)

feat_labels = [f.replace('_', ' ') for f in FEATURE_NAMES]


# ── Plot 1: SHAP bar — global feature importance ─────────────────────────────
logger.info("Plotting SHAP bar chart ...")
shap_abs_mean = np.abs(sv_arr).mean(axis=(0, 1))   # (n_features,)
top15_idx     = np.argsort(shap_abs_mean)[::-1][:15]
top15_labels  = [feat_labels[i] for i in top15_idx]
top15_vals    = shap_abs_mean[top15_idx]

fig, ax = plt.subplots(figsize=(11, 7))
fig.patch.set_facecolor(DARK_BG)
ax.set_facecolor(SURFACE)
bars = ax.barh(range(15), top15_vals[::-1],
               color=[PALETTE[i % len(PALETTE)] for i in range(15)],
               edgecolor=BORDER, linewidth=0.8)
ax.set_yticks(range(15))
ax.set_yticklabels(top15_labels[::-1], color=TEXT, fontsize=11)
ax.set_xlabel("Mean |SHAP Value| — Average Impact on Model Output", color=TEXT, fontsize=11)
ax.set_title("Top 15 Features by SHAP Importance\nIoT Device Fingerprinting — Random Forest",
             color=CYAN, fontsize=13, fontweight='bold', pad=12)
ax.tick_params(colors=TEXT)
ax.spines['bottom'].set_color(BORDER)
ax.spines['top'].set_color(BORDER)
ax.spines['left'].set_color(BORDER)
ax.spines['right'].set_color(BORDER)
for bar, val in zip(bars, top15_vals[::-1]):
    ax.text(val + top15_vals.max() * 0.01, bar.get_y() + bar.get_height() / 2,
            f'{val:.4f}', va='center', color=TEXT, fontsize=9)
plt.tight_layout()
out1 = PLOTS_DIR / "shap_bar.png"
fig.savefig(out1, dpi=150, facecolor=DARK_BG)
plt.close(fig)
logger.info(f"Saved: {out1}")


# ── Plot 2: Per-device SHAP heatmap (top 10 features × 8 devices) ────────────
logger.info("Plotting per-device SHAP heatmap ...")
shap_arr  = np.array(shap_values)   # (n_classes, n_samples, n_features)

# For each class, compute mean |SHAP| among samples of that class
device_shap = np.zeros((len(DEVICE_TYPES), len(FEATURE_NAMES)))
for ci, dev in enumerate(DEVICE_TYPES):
    mask = (y_sample == dev)
    if mask.sum() == 0:
        continue
    device_shap[ci] = np.abs(sv_arr[ci][mask]).mean(axis=0)

# Pick top 12 features overall
top12_idx    = np.argsort(shap_abs_mean)[::-1][:12]
heatmap_data = device_shap[:, top12_idx]           # (8, 12)
heatmap_data = heatmap_data / (heatmap_data.max() + 1e-9)  # normalize 0-1

fig, ax = plt.subplots(figsize=(13, 5))
fig.patch.set_facecolor(DARK_BG)
ax.set_facecolor(DARK_BG)

im = ax.imshow(heatmap_data, cmap='plasma', aspect='auto', vmin=0, vmax=1)

col_labels = [feat_labels[i] for i in top12_idx]
row_labels  = [d.replace('smart_', '').replace('_', ' ').title() for d in DEVICE_TYPES]

ax.set_xticks(range(len(col_labels)))
ax.set_xticklabels(col_labels, rotation=40, ha='right', color=TEXT, fontsize=9)
ax.set_yticks(range(len(row_labels)))
ax.set_yticklabels(row_labels, color=TEXT, fontsize=10)

for i in range(len(DEVICE_TYPES)):
    for j in range(len(col_labels)):
        val = heatmap_data[i, j]
        ax.text(j, i, f'{val:.2f}', ha='center', va='center',
                color='white' if val > 0.5 else TEXT, fontsize=8)

cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
cbar.ax.yaxis.set_tick_params(color=TEXT)
cbar.set_label('Normalised Mean |SHAP|', color=TEXT)
plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TEXT)

ax.set_title("Per-Device SHAP Feature Importance Heatmap\n(Darker = More Influential for That Device)",
             color=CYAN, fontsize=12, fontweight='bold', pad=10)
ax.spines[:].set_color(BORDER)
plt.tight_layout()
out2 = PLOTS_DIR / "shap_device_heatmap.png"
fig.savefig(out2, dpi=150, facecolor=DARK_BG)
plt.close(fig)
logger.info(f"Saved: {out2}")


# ── Plot 3: Single prediction explanation for each device ─────────────────────
logger.info("Plotting single-prediction waterfall examples ...")

fig, axes = plt.subplots(2, 4, figsize=(18, 9))
fig.patch.set_facecolor(DARK_BG)
fig.suptitle("SHAP Waterfall — Why the Model Predicted Each Device Type",
             color=CYAN, fontsize=13, fontweight='bold', y=1.01)

for ci, (dev, ax) in enumerate(zip(DEVICE_TYPES, axes.flatten())):
    ax.set_facecolor(SURFACE)
    mask = np.where(y_sample == dev)[0]
    if len(mask) == 0:
        ax.set_visible(False)
        continue

    sample_i   = mask[0]
    sv         = sv_arr[ci, sample_i]            # SHAP values for this sample, this class
    top_idx    = np.argsort(np.abs(sv))[::-1][:6]
    vals       = sv[top_idx]
    names      = [feat_labels[i] for i in top_idx]
    colors_bar = [GREEN if v > 0 else '#ff4757' for v in vals]

    y_pos = range(len(vals))
    ax.barh(y_pos, vals[::-1], color=colors_bar[::-1],
            edgecolor=BORDER, linewidth=0.6, height=0.6)
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(names[::-1], fontsize=8, color=TEXT)
    ax.axvline(0, color=BORDER, linewidth=1)
    ax.set_title(dev.replace('smart_','').replace('_',' ').title(),
                 color=PALETTE[ci], fontsize=10, fontweight='bold')
    ax.tick_params(colors=TEXT, labelsize=7)
    ax.spines[:].set_color(BORDER)

pos_patch = mpatches.Patch(color=GREEN,   label='Pushes toward this device')
neg_patch = mpatches.Patch(color='#ff4757', label='Pushes away from this device')
fig.legend(handles=[pos_patch, neg_patch], loc='lower center',
           ncol=2, framealpha=0, labelcolor=TEXT, fontsize=10)

plt.tight_layout()
out3 = PLOTS_DIR / "shap_per_device.png"
fig.savefig(out3, dpi=150, facecolor=DARK_BG, bbox_inches='tight')
plt.close(fig)
logger.info(f"Saved: {out3}")


# ── Print top 5 findings ──────────────────────────────────────────────────────
logger.info("=" * 60)
logger.info("SHAP KEY FINDINGS")
logger.info("=" * 60)
logger.info(f"{'Feature':<30} {'Mean|SHAP|':>12}  {'Rank'}")
for rank, idx in enumerate(np.argsort(shap_abs_mean)[::-1][:10], 1):
    logger.info(f"  {FEATURE_NAMES[idx]:<28} {shap_abs_mean[idx]:>12.4f}  #{rank}")
logger.info("=" * 60)
logger.info("Plots saved to plots/  — add shap_bar.png and shap_device_heatmap.png to your PPT")
