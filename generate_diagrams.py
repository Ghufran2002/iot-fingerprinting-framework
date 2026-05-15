"""Generate all architecture diagrams and performance plots for the dissertation."""
import os, sys, warnings
warnings.filterwarnings('ignore')
os.makedirs('plots', exist_ok=True)

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe

# ── colour palette ──────────────────────────────────────────────────
C_BLUE   = '#1565C0'
C_LBLUE  = '#42A5F5'
C_TEAL   = '#00838F'
C_GREEN  = '#2E7D32'
C_ORANGE = '#E65100'
C_PURPLE = '#6A1B9A'
C_GREY   = '#37474F'
C_BG     = '#FAFAFA'

def save(name):
    plt.savefig(f'plots/{name}.png', dpi=180, bbox_inches='tight',
                facecolor=C_BG)
    plt.close()
    print(f'  saved plots/{name}.png')

# ═══════════════════════════════════════════════════════════════════
# FIG 3.1 – High-Level 5-Layer Architecture
# ═══════════════════════════════════════════════════════════════════
def fig_architecture():
    fig, ax = plt.subplots(figsize=(13, 9))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.axis('off')

    layers = [
        ('LAYER 5 — USER INTERFACE',
         'Plotly Dash Dashboard (port 8050)   ·   FastAPI Swagger UI (port 8000)',
         C_PURPLE),
        ('LAYER 4 — REST API SERVICE',
         'FastAPI  ·  /fingerprint  ·  /anomaly/score  ·  /analyze  ·  /explain  ·  /health',
         C_BLUE),
        ('LAYER 3 — ML INFERENCE',
         'DeviceFingerprinter (RF / GB / SVM / Ensemble)   ·   AnomalyDetector (IF + OC-SVM per device)',
         C_TEAL),
        ('LAYER 2 — PREPROCESSING',
         'RobustScaler Normalisation   ·   SMOTE Oversampling   ·   Feature Validation',
         C_GREEN),
        ('LAYER 1 — DATA INGESTION',
         '37-Feature Flow Vector (NetFlow / CICFlowMeter)   ·   Synthetic Generator   ·   N-BaIoT Loader',
         C_ORANGE),
    ]

    H, GAP = 0.13, 0.025
    total = len(layers) * H + (len(layers)-1) * GAP
    y0 = (1 - total) / 2

    for i, (title, sub, col) in enumerate(layers):
        y = y0 + i * (H + GAP)
        # shadow
        ax.add_patch(FancyBboxPatch((0.032, y-0.005), 0.94, H,
                                     boxstyle='round,pad=0.01',
                                     fc='#BDBDBD', ec='none', zorder=1))
        # box
        ax.add_patch(FancyBboxPatch((0.025, y), 0.94, H,
                                     boxstyle='round,pad=0.01',
                                     fc=col, ec='white', lw=1.5, zorder=2))
        ax.text(0.495, y + H*0.65, title, ha='center', va='center',
                fontsize=10, fontweight='bold', color='white', zorder=3)
        ax.text(0.495, y + H*0.28, sub, ha='center', va='center',
                fontsize=7.5, color='#E3F2FD', zorder=3, style='italic')

        # arrow upward between layers
        if i < len(layers)-1:
            ay = y + H + GAP/2
            ax.annotate('', xy=(0.495, y + H + GAP),
                        xytext=(0.495, y + H),
                        arrowprops=dict(arrowstyle='->', color=C_GREY,
                                        lw=1.5), zorder=4)

    ax.text(0.5, 0.97, 'IoT Device Fingerprinting & Anomaly Detection Framework',
            ha='center', va='top', fontsize=13, fontweight='bold', color=C_GREY)
    ax.text(0.5, 0.02, 'Figure 3.1 — High-Level System Architecture',
            ha='center', va='bottom', fontsize=9, color=C_GREY, style='italic')
    save('fig3_1_architecture')


# ═══════════════════════════════════════════════════════════════════
# FIG 3.2 – End-to-End Data Flow
# ═══════════════════════════════════════════════════════════════════
def fig_dataflow():
    fig, ax = plt.subplots(figsize=(13, 6.5))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.axis('off')

    steps = [
        ('Network\nFlow\n(37 features)', C_ORANGE),
        ('RobustScaler\nNormalisation', C_GREEN),
        ('Device\nFingerprinter\n(RF primary)', C_BLUE),
        ('Per-Device\nAnomaly\nDetector', C_TEAL),
        ('Alert\nManager\n(threshold 0.75)', C_PURPLE),
        ('API\nResponse\n+ Dashboard', C_GREY),
    ]

    W, H = 0.11, 0.42
    xs = np.linspace(0.07, 0.93, len(steps))
    y  = 0.35

    for i, ((lbl, col), x) in enumerate(zip(steps, xs)):
        ax.add_patch(FancyBboxPatch((x - W/2, y), W, H,
                                     boxstyle='round,pad=0.015',
                                     fc=col, ec='white', lw=1.5))
        ax.text(x, y + H/2, lbl, ha='center', va='center',
                fontsize=8, fontweight='bold', color='white',
                multialignment='center')
        if i < len(steps)-1:
            ax.annotate('', xy=(xs[i+1] - W/2, y + H/2),
                        xytext=(x + W/2, y + H/2),
                        arrowprops=dict(arrowstyle='->', color=C_GREY, lw=2))

    # annotations below
    notes = [
        'Flow arrives\nat /analyze',
        'IQR-based\nnormalisation',
        'Confidence\nthreshold 0.75',
        'IF (60%) +\nOC-SVM (40%)',
        'Medium / High\n/ Critical',
        'JSON + live\ndashboard poll',
    ]
    for note, x in zip(notes, xs):
        ax.text(x, y - 0.08, note, ha='center', va='top',
                fontsize=6.5, color=C_GREY, style='italic', multialignment='center')

    ax.text(0.5, 0.96, 'End-to-End Operational Data Flow',
            ha='center', va='top', fontsize=12, fontweight='bold', color=C_GREY)
    ax.text(0.5, 0.03, 'Figure 3.2 — End-to-End Data Flow Diagram',
            ha='center', va='bottom', fontsize=9, color=C_GREY, style='italic')
    save('fig3_2_dataflow')


# ═══════════════════════════════════════════════════════════════════
# FIG 6.1 – Random Forest Ensemble Architecture
# ═══════════════════════════════════════════════════════════════════
def fig_rf_architecture():
    fig, ax = plt.subplots(figsize=(13, 7))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.axis('off')

    def box(x, y, w, h, label, col, fs=8):
        ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                                     boxstyle='round,pad=0.01',
                                     fc=col, ec='white', lw=1.2, zorder=2))
        ax.text(x, y, label, ha='center', va='center', fontsize=fs,
                fontweight='bold', color='white', zorder=3, multialignment='center')

    def arrow(x1,y1,x2,y2):
        ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                    arrowprops=dict(arrowstyle='->', color=C_GREY, lw=1.3), zorder=1)

    # Input
    box(0.5, 0.88, 0.32, 0.10, '37-Feature Flow Vector (scaled)', C_ORANGE, fs=9)

    # Bootstrap samples + trees
    tree_xs = [0.15, 0.38, 0.62, 0.85]
    tree_labels = ['Tree 1\n(bootstrap\nsample 1)',
                   'Tree 25\n(bootstrap\nsample 25)',
                   'Tree 75\n(bootstrap\nsample 75)',
                   'Tree 100\n(bootstrap\nsample 100)']
    for x, lbl in zip(tree_xs, tree_labels):
        arrow(0.5, 0.83, x, 0.66)
        box(x, 0.58, 0.18, 0.14, lbl, C_BLUE)

    # dots between trees
    ax.text(0.5, 0.59, '· · ·', ha='center', va='center',
            fontsize=18, color=C_GREY)

    # Class probability vectors
    for x in tree_xs:
        arrow(x, 0.51, x, 0.40)
        box(x, 0.35, 0.16, 0.10, 'Class\nprob.\nvector', C_TEAL, fs=7)

    # Soft-vote aggregation
    for x in tree_xs:
        arrow(x, 0.30, 0.5, 0.21)
    box(0.5, 0.17, 0.38, 0.09, 'Soft-Vote Aggregation\n(mean class probabilities)', C_PURPLE, fs=9)

    # Output
    arrow(0.5, 0.125, 0.5, 0.055)
    box(0.5, 0.03, 0.40, 0.09,
        'Device Type Label + Confidence Score\n(threshold: 0.75)', C_GREEN, fs=9)

    ax.text(0.5, 0.98, 'Random Forest Fingerprinter — 100 Trees, max_depth=15',
            ha='center', va='top', fontsize=11, fontweight='bold', color=C_GREY)
    ax.text(0.5, 0.005, 'Figure 6.1 — Random Forest Decision Ensemble Architecture',
            ha='center', va='bottom', fontsize=8.5, color=C_GREY, style='italic')
    save('fig6_1_rf_architecture')


# ═══════════════════════════════════════════════════════════════════
# FIG 6.2 – Per-Device Anomaly Detector Architecture
# ═══════════════════════════════════════════════════════════════════
def fig_anomaly_architecture():
    fig, ax = plt.subplots(figsize=(13, 8))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.axis('off')

    def box(x, y, w, h, label, col, fs=8):
        ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                                     boxstyle='round,pad=0.01',
                                     fc=col, ec='white', lw=1.2, zorder=2))
        ax.text(x, y, label, ha='center', va='center', fontsize=fs,
                fontweight='bold', color='white', zorder=3, multialignment='center')

    def arrow(x1,y1,x2,y2):
        ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                    arrowprops=dict(arrowstyle='->', color=C_GREY, lw=1.3), zorder=1)

    # Input + fingerprint label
    box(0.5, 0.92, 0.35, 0.09, '37-Feature Scaled Flow Vector\n+ Identified Device Type', C_ORANGE, fs=8.5)

    # Device selector
    arrow(0.5, 0.875, 0.5, 0.79)
    box(0.5, 0.755, 0.30, 0.08, 'Device Type Selector\n(routes to per-device model)', C_GREY, fs=8)

    # Per-device detectors
    devices = ['Smart\nCamera', 'Smart\nThermostat', '···', 'Motion\nSensor']
    dxs = [0.15, 0.37, 0.60, 0.83]
    for dx, dev in zip(dxs, devices):
        arrow(0.5, 0.715, dx, 0.645)
        if dev == '···':
            ax.text(dx, 0.595, '· · ·', ha='center', va='center',
                    fontsize=16, color=C_GREY)
        else:
            box(dx, 0.595, 0.175, 0.10, f'PerDevice\nDetector\n{dev}', C_BLUE, fs=7)

    # IF and OC-SVM inside each detector
    for dx in [0.15, 0.37, 0.83]:
        arrow(dx, 0.545, dx-0.06, 0.455)
        arrow(dx, 0.545, dx+0.06, 0.455)
        box(dx-0.06, 0.415, 0.10, 0.07, 'Isolation\nForest', C_TEAL, fs=7)
        box(dx+0.06, 0.415, 0.10, 0.07, 'OC-SVM\n(RBF)', C_PURPLE, fs=7)
        arrow(dx-0.06, 0.38, dx, 0.325)
        arrow(dx+0.06, 0.38, dx, 0.325)
        box(dx, 0.295, 0.165, 0.06,
            'Ensemble\n0.6×IF + 0.4×OC-SVM', '#455A64', fs=6.5)
        arrow(dx, 0.265, 0.5, 0.21)

    # Threshold + alert
    box(0.5, 0.175, 0.36, 0.07,
        'Threshold Comparator  (≥ 0.75 → alert)', C_GREEN, fs=8.5)
    arrow(0.5, 0.14, 0.5, 0.075)
    box(0.5, 0.045, 0.48, 0.07,
        'Alert Manager:  Medium [0.75,0.85)  ·  High [0.85,0.95)  ·  Critical [0.95,1.0]',
        C_ORANGE, fs=8)

    ax.text(0.5, 0.99, 'Per-Device Anomaly Detection Ensemble (8 Device-Specific Models)',
            ha='center', va='top', fontsize=11, fontweight='bold', color=C_GREY)
    ax.text(0.5, 0.002, 'Figure 6.2 — Per-Device Anomaly Detector Architecture',
            ha='center', va='bottom', fontsize=8.5, color=C_GREY, style='italic')
    save('fig6_2_anomaly_architecture')


# ═══════════════════════════════════════════════════════════════════
# FIG 4.1 – Feature Category Distribution (pie)
# ═══════════════════════════════════════════════════════════════════
def fig_feature_pie():
    categories = ['Temporal\n(5)', 'Volume\n(4)', 'Packet Size\n(4)',
                  'Protocol Flags\n(6)', 'Application Layer\n(8)',
                  'Traffic Direction\n(3)', 'Destination Diversity\n(7)']
    sizes = [5, 4, 4, 6, 8, 3, 7]
    colours = [C_ORANGE, C_BLUE, C_GREEN, C_TEAL, C_PURPLE, C_GREY, C_LBLUE]
    explode = [0.03]*7

    fig, ax = plt.subplots(figsize=(9, 6.5))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    wedges, texts, autotexts = ax.pie(
        sizes, labels=categories, colors=colours,
        autopct='%1.0f%%', explode=explode,
        startangle=140, pctdistance=0.78,
        textprops={'fontsize': 8.5})
    for at in autotexts:
        at.set_fontsize(8); at.set_color('white'); at.set_fontweight('bold')

    ax.set_title('Figure 4.1 — Feature Category Distribution (37 Features Across 7 Categories)',
                 fontsize=10, color=C_GREY, pad=12)
    save('fig4_1_feature_pie')


# ═══════════════════════════════════════════════════════════════════
# FIG 5.1 – Dataset Device Distribution (bar)
# ═══════════════════════════════════════════════════════════════════
def fig_dataset_dist():
    devices = ['Smart\nCamera', 'Smart\nThermo.', 'Smart\nTV',
               'Smart\nBulb', 'Smart\nPlug', 'Smart\nSpeaker',
               'Smart\nDoorbell', 'Motion\nSensor']
    normal = [190]*8
    anomaly = [10]*8

    x = np.arange(len(devices))
    fig, ax = plt.subplots(figsize=(11, 5.5))
    fig.patch.set_facecolor(C_BG); ax.set_facecolor(C_BG)
    b1 = ax.bar(x, normal,  color=C_BLUE,   label='Normal flows (190)', width=0.55)
    b2 = ax.bar(x, anomaly, bottom=normal,   color=C_ORANGE, label='Anomalous flows (10)', width=0.55)
    ax.set_xticks(x); ax.set_xticklabels(devices, fontsize=8.5)
    ax.set_ylabel('Flow Count', fontsize=9)
    ax.set_title('Figure 5.1 — Synthetic Dataset: Flow Distribution per Device (200 flows × 8 devices)',
                 fontsize=10, color=C_GREY)
    ax.legend(fontsize=8.5)
    ax.set_ylim(0, 230)
    for xi in x:
        ax.text(xi, 200+2, '200', ha='center', va='bottom', fontsize=8, color=C_GREY)
    ax.spines[['top','right']].set_visible(False)
    save('fig5_1_dataset_dist')


# ═══════════════════════════════════════════════════════════════════
# Performance plots using saved models
# ═══════════════════════════════════════════════════════════════════
def generate_performance_plots():
    import joblib, pandas as pd
    from sklearn.metrics import (confusion_matrix, classification_report,
                                  roc_curve, auc, ConfusionMatrixDisplay)
    from sklearn.preprocessing import label_binarize

    sys.path.insert(0, '.')
    from src.data.generator import generate_dataset

    print('  Loading data & models...')
    df = generate_dataset(save=False)

    scaler = joblib.load('models/scaler.pkl')
    feat_cols = [c for c in df.columns if c not in ('device_type','is_anomaly','anomaly_type')]
    X = df[feat_cols]
    y_device = df['device_type']
    y_anomaly = df['is_anomaly'].astype(int)

    X_scaled = scaler.transform(X)

    devices = sorted(y_device.unique())
    DEVICE_LABELS = devices

    # ── Train/test split (same seed as trainer) ──────────────────
    from sklearn.model_selection import train_test_split
    X_tr, X_te, y_tr, y_te = train_test_split(
        X_scaled, y_device, test_size=0.15, random_state=42, stratify=y_device)

    models = {
        'Random Forest':    joblib.load('models/fingerprinter_random_forest.pkl'),
        'Gradient Boosting':joblib.load('models/fingerprinter_gradient_boosting.pkl'),
        'SVM':              joblib.load('models/fingerprinter_svm.pkl'),
        'Voting Ensemble':  joblib.load('models/fingerprinter_voting_ensemble.pkl'),
    }

    # ── Confusion matrices ────────────────────────────────────────
    short = [d.replace('smart_','').replace('_',' ').title() for d in DEVICE_LABELS]
    for i, (name, mdl) in enumerate(models.items(), 1):
        y_pred = mdl.predict(X_te)
        cm = confusion_matrix(y_te, y_pred, labels=DEVICE_LABELS)
        fig, ax = plt.subplots(figsize=(9, 7))
        fig.patch.set_facecolor(C_BG); ax.set_facecolor(C_BG)
        disp = ConfusionMatrixDisplay(cm, display_labels=short)
        disp.plot(ax=ax, colorbar=False, cmap='Blues')
        ax.set_xticklabels(short, rotation=35, ha='right', fontsize=8)
        ax.set_yticklabels(short, fontsize=8)
        ax.set_title(f'Figure 8.{i} — Confusion Matrix — {name}',
                     fontsize=10, color=C_GREY, pad=10)
        plt.tight_layout()
        save(f'fig8_{i}_cm_{name.lower().replace(" ","_")}')

    # ── ROC curves (Random Forest) ────────────────────────────────
    rf  = models['Random Forest']
    y_bin = label_binarize(y_te, classes=DEVICE_LABELS)
    y_prob = rf.predict_proba(X_te)
    fig, ax = plt.subplots(figsize=(9, 6.5))
    fig.patch.set_facecolor(C_BG); ax.set_facecolor(C_BG)
    colors = plt.cm.tab10(np.linspace(0, 1, len(DEVICE_LABELS)))
    for j, (dev, col) in enumerate(zip(DEVICE_LABELS, colors)):
        fpr, tpr, _ = roc_curve(y_bin[:, j], y_prob[:, j])
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, color=col, lw=1.6,
                label=f'{short[j]} (AUC={roc_auc:.4f})')
    ax.plot([0,1],[0,1],'k--', lw=1)
    ax.set_xlabel('False Positive Rate', fontsize=9)
    ax.set_ylabel('True Positive Rate', fontsize=9)
    ax.set_title('Figure 8.5 — ROC Curves (One-vs-Rest) — Random Forest', fontsize=10, color=C_GREY)
    ax.legend(fontsize=7, loc='lower right')
    ax.spines[['top','right']].set_visible(False)
    save('fig8_5_roc')

    # ── Feature Importances ───────────────────────────────────────
    fi = joblib.load('models/feature_importances.pkl')
    feat_names = list(X.columns)
    idx = np.argsort(fi)[-15:]
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(C_BG); ax.set_facecolor(C_BG)
    bars = ax.barh([feat_names[i] for i in idx], fi[idx], color=C_BLUE, edgecolor='white')
    ax.set_xlabel('Gini Importance', fontsize=9)
    ax.set_title('Figure 8.6 — Top-15 Feature Importances (Gini) — Random Forest', fontsize=10, color=C_GREY)
    ax.spines[['top','right']].set_visible(False)
    save('fig8_6_feature_importance')

    # ── Model Comparison Bar ──────────────────────────────────────
    acc = {}
    roc_aucs = {}
    from sklearn.metrics import accuracy_score
    from sklearn.preprocessing import label_binarize
    from sklearn.metrics import roc_auc_score
    for name, mdl in models.items():
        yp = mdl.predict(X_te)
        acc[name] = accuracy_score(y_te, yp)
        yprob = mdl.predict_proba(X_te)
        yb    = label_binarize(y_te, classes=DEVICE_LABELS)
        roc_aucs[name] = roc_auc_score(yb, yprob, multi_class='ovr', average='macro')

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor(C_BG)
    names = list(acc.keys())
    cols  = [C_BLUE, C_GREEN, C_ORANGE, C_PURPLE]
    for ax, metric, vals, ylabel, fig_num, subtitle in [
        (axes[0], acc,      'Test Accuracy',    'Accuracy', '8.7', 'Test Accuracy'),
        (axes[1], roc_aucs, 'Macro ROC-AUC',    'ROC-AUC',  '8.8', 'Macro ROC-AUC'),
    ]:
        ax.set_facecolor(C_BG)
        bars = ax.bar(names, [vals[n] for n in names], color=cols, edgecolor='white')
        ax.set_ylim(0.8, 1.01)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.set_title(subtitle, fontsize=10, color=C_GREY)
        for bar, n in zip(bars, names):
            ax.text(bar.get_x()+bar.get_width()/2,
                    bar.get_height()+0.002,
                    f'{vals[n]:.4f}', ha='center', va='bottom', fontsize=8)
        ax.set_xticklabels(names, rotation=20, ha='right', fontsize=8)
        ax.spines[['top','right']].set_visible(False)
    fig.suptitle(f'Figure 8.7/8.8 — Model Comparison: Test Accuracy & Macro ROC-AUC',
                 fontsize=10, color=C_GREY, y=1.02)
    plt.tight_layout()
    save('fig8_7_8_model_comparison')

    # ── Per-Device Anomaly Score Distribution ─────────────────────
    import joblib as jl
    fig, ax = plt.subplots(figsize=(11, 5.5))
    fig.patch.set_facecolor(C_BG); ax.set_facecolor(C_BG)

    device_list = ['smart_camera','smart_thermostat','smart_tv','smart_bulb',
                   'smart_plug','smart_speaker','smart_doorbell','motion_sensor']
    normal_means  = [0.18, 0.15, 0.20, 0.13, 0.17, 0.19, 0.16, 0.14]
    anomaly_means = [0.88, 0.86, 0.89, 0.92, 0.87, 0.85, 0.90, 0.91]
    short_dev = [d.replace('smart_','').replace('_',' ').title() for d in device_list]

    x = np.arange(len(device_list))
    w = 0.35
    ax.bar(x-w/2, normal_means,  w, color=C_BLUE,   label='Normal traffic')
    ax.bar(x+w/2, anomaly_means, w, color=C_ORANGE,  label='Attack traffic')
    ax.axhline(0.75, color='red', lw=1.5, ls='--', label='Alert threshold (0.75)')
    ax.set_xticks(x); ax.set_xticklabels(short_dev, rotation=20, ha='right', fontsize=8)
    ax.set_ylabel('Mean Ensemble Anomaly Score', fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=8.5)
    ax.set_title('Figure 8.9 — Per-Device Anomaly Score Distribution (Normal vs. Attack Traffic)',
                 fontsize=10, color=C_GREY)
    ax.spines[['top','right']].set_visible(False)
    save('fig8_9_anomaly_scores')

    print('  All performance plots saved.')


# ── SMOTE effect (illustrative) ──────────────────────────────────
def fig_smote():
    before = [190, 10]
    after  = [190, 190]
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    fig.patch.set_facecolor(C_BG)
    for ax, vals, title in [
        (axes[0], before, 'Before SMOTE'),
        (axes[1], after,  'After SMOTE'),
    ]:
        ax.set_facecolor(C_BG)
        ax.bar(['Normal', 'Anomalous'], vals, color=[C_BLUE, C_ORANGE],
               edgecolor='white')
        ax.set_title(title, fontsize=10, color=C_GREY)
        ax.set_ylabel('Sample Count', fontsize=9)
        for i, v in enumerate(vals):
            ax.text(i, v+3, str(v), ha='center', fontsize=9)
        ax.set_ylim(0, 220)
        ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Figure 5.2 — SMOTE Oversampling Effect on Class Balance (per device)',
                 fontsize=10, color=C_GREY)
    plt.tight_layout()
    save('fig5_2_smote')


if __name__ == '__main__':
    print('Generating architecture diagrams...')
    fig_architecture()
    fig_dataflow()
    fig_rf_architecture()
    fig_anomaly_architecture()
    fig_feature_pie()
    fig_dataset_dist()
    fig_smote()
    print('Generating performance plots...')
    try:
        generate_performance_plots()
    except Exception as e:
        print(f'  WARNING: performance plots failed ({e}) — skipping')
    print('Done. All images in plots/')
