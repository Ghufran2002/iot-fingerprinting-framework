"""
Device Fingerprinting Module.
Primary: Random Forest (100 trees, max_depth=15).
Supported: Gradient Boosting, SVM, Voting Ensemble for comparison.
Confidence threshold 0.60 — below this, device is 'unknown'.
"""
import numpy as np
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, roc_auc_score)
from sklearn.preprocessing import label_binarize
from src.features.extractor import DEVICE_TYPES, LABEL_DEVICE_MAP
from src.utils.logger import logger

MODELS_DIR = Path(__file__).resolve().parents[2] / "models"
CONFIDENCE_THRESHOLD = 0.60


def _build_models():
    rf = RandomForestClassifier(
        n_estimators=100, max_depth=15, class_weight='balanced',
        n_jobs=-1, random_state=42)
    gb = GradientBoostingClassifier(
        n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
    svm = SVC(
        kernel='rbf', C=10, gamma='scale', probability=True,
        class_weight='balanced', random_state=42)
    ensemble = VotingClassifier(
        estimators=[('rf', rf), ('gb', gb), ('svm', svm)],
        voting='soft', n_jobs=-1)
    return {'random_forest': rf, 'gradient_boosting': gb, 'svm': svm, 'voting_ensemble': ensemble}


class DeviceFingerprinter:
    def __init__(self):
        self._models = _build_models()
        self._primary = 'random_forest'
        self._trained = False
        self.feature_importances_ = None

    def train(self, X_train, y_train, X_val, y_val):
        results = {}
        for name, model in self._models.items():
            logger.info(f"Training {name} ...")
            model.fit(X_train, y_train)
            val_acc = accuracy_score(y_val, model.predict(X_val))
            results[name] = val_acc
            logger.info(f"  {name} val accuracy: {val_acc:.4f}")

        best_name = max(results, key=results.get)
        self._primary = best_name
        logger.info(f"Best model: {best_name} (val acc={results[best_name]:.4f})")

        rf = self._models['random_forest']
        self.feature_importances_ = rf.feature_importances_
        self._trained = True
        return results

    def predict(self, X: np.ndarray):
        assert self._trained
        model = self._models[self._primary]
        proba = model.predict_proba(X)
        pred_idx = np.argmax(proba, axis=1)
        confidence = proba[np.arange(len(pred_idx)), pred_idx]

        labels = []
        for idx, conf in zip(pred_idx, confidence):
            if conf >= CONFIDENCE_THRESHOLD:
                labels.append(LABEL_DEVICE_MAP[idx])
            else:
                labels.append('unknown')
        return labels, confidence.tolist()

    def predict_single(self, x: np.ndarray):
        labels, confs = self.predict(x.reshape(1, -1))
        return labels[0], confs[0]

    def evaluate(self, X_test, y_test):
        assert self._trained
        results = {}
        for name, model in self._models.items():
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)
            y_bin = label_binarize(y_test, classes=list(range(len(DEVICE_TYPES))))
            acc = accuracy_score(y_test, y_pred)
            roc = roc_auc_score(y_bin, y_proba, multi_class='ovr', average='macro')
            cm = confusion_matrix(y_test, y_pred)
            report = classification_report(y_test, y_pred,
                                           target_names=DEVICE_TYPES, output_dict=True)
            results[name] = {
                'accuracy': round(acc, 4),
                'roc_auc':  round(roc, 4),
                'confusion_matrix': cm,
                'report': report,
            }
            logger.info(f"{name} | Test Acc={acc:.4f} | ROC-AUC={roc:.4f}")
        return results

    def save(self):
        MODELS_DIR.mkdir(exist_ok=True)
        for name, model in self._models.items():
            joblib.dump(model, MODELS_DIR / f"fingerprinter_{name}.pkl")
        joblib.dump(self._primary, MODELS_DIR / "fingerprinter_primary.pkl")
        if self.feature_importances_ is not None:
            joblib.dump(self.feature_importances_, MODELS_DIR / "feature_importances.pkl")
        logger.info("Fingerprinting models saved.")

    def load(self):
        for name in self._models:
            path = MODELS_DIR / f"fingerprinter_{name}.pkl"
            if path.exists():
                self._models[name] = joblib.load(path)
        primary_path = MODELS_DIR / "fingerprinter_primary.pkl"
        if primary_path.exists():
            self._primary = joblib.load(primary_path)
        fi_path = MODELS_DIR / "feature_importances.pkl"
        if fi_path.exists():
            self.feature_importances_ = joblib.load(fi_path)
        self._trained = True
        logger.info(f"Fingerprinter loaded (primary={self._primary}).")


fingerprinter = DeviceFingerprinter()
