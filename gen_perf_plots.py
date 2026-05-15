"""Generate performance plots using saved models."""
import warnings; warnings.filterwarnings('ignore')
import numpy as np, joblib, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.data.generator import generate_dataset
from src.features.extractor import FEATURE_NAMES, DEVICE_TYPES, DEVICE_LABEL_MAP, LABEL_DEVICE_MAP
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, roc_auc_score, confusion_matrix,
                              ConfusionMatrixDisplay, roc_curve, auc)
from sklearn.preprocessing import label_binarize

os.makedirs('plots', exist_ok=True)
C_BG='#FAFAFA'; C_GREY='#37474F'
C_BLUE='#1565C0'; C_GREEN='#2E7D32'; C_ORANGE='#E65100'; C_PURPLE='#6A1B9A'

df = generate_dataset(save=False)
X = df[FEATURE_NAMES].copy()
y_str = df['device_type'].values
y = np.array([DEVICE_LABEL_MAP[d] for d in y_str])
scaler = joblib.load('models/scaler.pkl')
X_sc = scaler.transform(X)
# classes in training order (0-7)
classes = list(range(len(DEVICE_TYPES)))
short = [d.replace('smart_','').replace('_',' ').title() for d in DEVICE_TYPES]

X_tr, X_te, y_tr, y_te = train_test_split(
    X_sc, y, test_size=0.15, random_state=42, stratify=y)

models = {
    'Random Forest':    joblib.load('models/fingerprinter_random_forest.pkl'),
    'Gradient Boosting':joblib.load('models/fingerprinter_gradient_boosting.pkl'),
    'SVM':              joblib.load('models/fingerprinter_svm.pkl'),
    'Voting Ensemble':  joblib.load('models/fingerprinter_voting_ensemble.pkl'),
}

acc = {}; rocs = {}
y_bin = label_binarize(y_te, classes=classes)

for i, (name, mdl) in enumerate(models.items(), 1):
    yp   = mdl.predict(X_te)
    ypr  = mdl.predict_proba(X_te)
    acc[name]  = accuracy_score(y_te, yp)
    rocs[name] = roc_auc_score(y_bin, ypr, multi_class='ovr', average='macro')

    cm = confusion_matrix(y_te, yp, labels=classes)
    fig, ax = plt.subplots(figsize=(9, 7))
    fig.patch.set_facecolor(C_BG); ax.set_facecolor(C_BG)
    disp = ConfusionMatrixDisplay(cm, display_labels=short)
    disp.plot(ax=ax, colorbar=False, cmap='Blues')
    ax.set_xticklabels(short, rotation=35, ha='right', fontsize=8)
    ax.set_yticklabels(short, fontsize=8)
    ax.set_title(f'Figure 8.{i} — Confusion Matrix — {name}',
                 fontsize=10, color=C_GREY, pad=10)
    plt.tight_layout()
    slug = name.lower().replace(' ', '_')
    plt.savefig(f'plots/fig8_{i}_cm_{slug}.png', dpi=180,
                bbox_inches='tight', facecolor=C_BG)
    plt.close()
    print(f'  CM {name}: acc={acc[name]:.4f}')

# ROC
rf = models['Random Forest']
yprob = rf.predict_proba(X_te)
fig, ax = plt.subplots(figsize=(9, 6.5))
fig.patch.set_facecolor(C_BG); ax.set_facecolor(C_BG)
colors = plt.cm.tab10(np.linspace(0, 1, 8))
for j, (dev, col) in enumerate(zip(classes, colors)):
    fpr, tpr, _ = roc_curve(y_bin[:, j], yprob[:, j])
    ra = auc(fpr, tpr)
    ax.plot(fpr, tpr, color=col, lw=1.6, label=f'{short[j]} (AUC={ra:.4f})')
ax.plot([0,1],[0,1], 'k--', lw=1)
ax.set_xlabel('False Positive Rate', fontsize=9)
ax.set_ylabel('True Positive Rate', fontsize=9)
ax.set_title('Figure 8.5 — ROC Curves (One-vs-Rest) — Random Forest',
             fontsize=10, color=C_GREY)
ax.legend(fontsize=7, loc='lower right')
ax.spines[['top','right']].set_visible(False)
plt.tight_layout()
plt.savefig('plots/fig8_5_roc.png', dpi=180, bbox_inches='tight', facecolor=C_BG)
plt.close(); print('ROC saved')

# Feature importances
fi = joblib.load('models/feature_importances.pkl')
idx = np.argsort(fi)[-15:]
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor(C_BG); ax.set_facecolor(C_BG)
ax.barh([FEATURE_NAMES[i] for i in idx], fi[idx], color=C_BLUE, edgecolor='white')
ax.set_xlabel('Gini Importance', fontsize=9)
ax.set_title('Figure 8.6 — Top-15 Feature Importances (Gini) — Random Forest',
             fontsize=10, color=C_GREY)
ax.spines[['top','right']].set_visible(False)
plt.tight_layout()
plt.savefig('plots/fig8_6_feature_importance.png', dpi=180,
            bbox_inches='tight', facecolor=C_BG)
plt.close(); print('Feature importance saved')

# Model comparison
cols_bar = [C_BLUE, C_GREEN, C_ORANGE, C_PURPLE]
names = list(acc.keys())
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.patch.set_facecolor(C_BG)
for ax, vals, ylabel, title in [
    (axes[0], acc,  'Test Accuracy',  'Test Accuracy per Model'),
    (axes[1], rocs, 'Macro ROC-AUC', 'Macro ROC-AUC per Model'),
]:
    ax.set_facecolor(C_BG)
    bars = ax.bar(names, [vals[n] for n in names], color=cols_bar, edgecolor='white')
    ax.set_ylim(0.8, 1.01)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(title, fontsize=10, color=C_GREY)
    for bar, n in zip(bars, names):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.002,
                f'{vals[n]:.4f}', ha='center', va='bottom', fontsize=8)
    ax.set_xticklabels(names, rotation=20, ha='right', fontsize=8)
    ax.spines[['top','right']].set_visible(False)
fig.suptitle('Figure 8.7/8.8 — Model Comparison: Test Accuracy & Macro ROC-AUC',
             fontsize=10, color=C_GREY)
plt.tight_layout()
plt.savefig('plots/fig8_7_8_model_comparison.png', dpi=180,
            bbox_inches='tight', facecolor=C_BG)
plt.close(); print('Model comparison saved')

print('All acc:', {k: round(v,4) for k,v in acc.items()})
print('All roc:', {k: round(v,4) for k,v in rocs.items()})
print('Done.')
