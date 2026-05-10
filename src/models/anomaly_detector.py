"""
Per-device anomaly detection ensemble.
Each device type has its own (IsolationForest + OneClassSVM) pair.
Ensemble score = 0.60 * IF_score + 0.40 * OC-SVM_score.
A global fallback model is used for unknown device types.
Alert threshold: 0.75
"""
import numpy as np
import joblib
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from src.features.extractor import DEVICE_TYPES
from src.utils.logger import logger

MODELS_DIR = Path(__file__).resolve().parents[2] / "models"
ALERT_THRESHOLD = 0.75
IF_WEIGHT   = 0.60
OCSVM_WEIGHT = 0.40


_SCORE_POWER = 0.6   # power < 1 boosts mid-range scores, separating attack from normal


def _scale_scores(raw: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """Map raw decision scores to [0,1] using training-fit bounds + power calibration."""
    shifted = -raw
    if hi == lo:
        return np.full(len(shifted), 0.5)
    scaled = (shifted - lo) / (hi - lo)
    return np.clip(scaled, 0.0, 1.0) ** _SCORE_POWER


class PerDeviceDetector:
    def __init__(self, device_type: str):
        self.device_type = device_type
        self.if_model = IsolationForest(
            n_estimators=50, contamination=0.05,
            max_samples=128, random_state=42, n_jobs=-1)
        self.ocsvm_model = OneClassSVM(
            kernel='rbf', nu=0.05, gamma='auto')
        # Normalization bounds computed on normal training data
        self._if_lo = self._if_hi = 0.0
        self._ocsvm_lo = self._ocsvm_hi = 0.0
        self._trained = False

    def train(self, X_normal: np.ndarray):
        if len(X_normal) < 10:
            logger.warning(f"Too few normal samples for {self.device_type}, skipping.")
            return
        self.if_model.fit(X_normal)
        self.ocsvm_model.fit(X_normal)
        # Fit normalization bounds: normal data scores should cluster near 0
        if_train = -self.if_model.decision_function(X_normal)
        oc_train = -self.ocsvm_model.decision_function(X_normal)
        # Use [p5, p95+margin] so anomalies map above 0.75
        self._if_lo   = float(np.percentile(if_train, 5))
        self._if_hi   = float(np.percentile(if_train, 95) * 2.0)
        self._ocsvm_lo = float(np.percentile(oc_train, 5))
        self._ocsvm_hi = float(np.percentile(oc_train, 95) * 2.0)
        self._trained = True

    def score(self, X: np.ndarray) -> np.ndarray:
        if not self._trained:
            return np.zeros(len(X))
        if_raw    = self.if_model.decision_function(X)
        ocsvm_raw = self.ocsvm_model.decision_function(X)
        if_score   = _scale_scores(if_raw,   self._if_lo,    self._if_hi)
        ocsvm_score = _scale_scores(ocsvm_raw, self._ocsvm_lo, self._ocsvm_hi)
        return IF_WEIGHT * if_score + OCSVM_WEIGHT * ocsvm_score

    def score_single(self, x: np.ndarray) -> float:
        return float(self.score(x.reshape(1, -1))[0])


class AnomalyDetector:
    def __init__(self):
        self._detectors = {d: PerDeviceDetector(d) for d in DEVICE_TYPES}
        self._global_fallback = PerDeviceDetector('global')
        self._trained = False

    def train(self, df_features, df_labels, df_is_anomaly):
        """Train per-device models on NORMAL traffic only."""
        import pandas as pd
        for device in DEVICE_TYPES:
            mask = (df_labels == device) & (df_is_anomaly == 0)
            X_normal = df_features[mask].values if hasattr(df_features, 'values') else df_features[mask]
            logger.info(f"Training anomaly detector for {device}: {len(X_normal)} normal samples")
            self._detectors[device].train(X_normal)

        all_normal = df_features[df_is_anomaly == 0].values if hasattr(df_features, 'values') else df_features[df_is_anomaly == 0]
        logger.info(f"Training global fallback on {len(all_normal)} normal samples")
        self._global_fallback.train(all_normal)
        self._trained = True

    def score(self, X: np.ndarray, device_type: str) -> np.ndarray:
        detector = self._detectors.get(device_type, self._global_fallback)
        if not detector._trained:
            detector = self._global_fallback
        return detector.score(X)

    def score_single(self, x: np.ndarray, device_type: str) -> float:
        return float(self.score(x.reshape(1, -1), device_type)[0])

    def is_anomalous(self, score: float) -> bool:
        return score >= ALERT_THRESHOLD

    def evaluate(self, X_normal: np.ndarray, X_anomaly: np.ndarray, device_type: str) -> dict:
        from sklearn.metrics import roc_auc_score
        scores_normal  = self.score(X_normal, device_type)
        scores_anomaly = self.score(X_anomaly, device_type)

        # Fixed-threshold metrics
        tp = int((scores_anomaly >= ALERT_THRESHOLD).sum())
        tn = int((scores_normal  <  ALERT_THRESHOLD).sum())
        fp = int((scores_normal  >= ALERT_THRESHOLD).sum())
        fn = int((scores_anomaly <  ALERT_THRESHOLD).sum())
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall + 1e-9)

        # Threshold-independent AUC-ROC (primary metric for anomaly detection)
        all_scores = np.concatenate([scores_normal, scores_anomaly])
        all_labels = np.concatenate([np.zeros(len(scores_normal)), np.ones(len(scores_anomaly))])
        roc_auc = float(roc_auc_score(all_labels, all_scores))

        return {
            'device': device_type,
            'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn,
            'precision': round(precision, 4),
            'recall':    round(recall, 4),
            'f1':        round(f1, 4),
            'roc_auc':   round(roc_auc, 4),
            'mean_normal_score':  round(float(scores_normal.mean()), 4),
            'mean_anomaly_score': round(float(scores_anomaly.mean()), 4),
        }

    def save(self):
        MODELS_DIR.mkdir(exist_ok=True)
        for device, det in self._detectors.items():
            if det._trained:
                joblib.dump(det, MODELS_DIR / f"anomaly_{device}.pkl")
        joblib.dump(self._global_fallback, MODELS_DIR / "anomaly_global.pkl")
        logger.info("Anomaly detectors saved.")

    def load(self):
        for device in DEVICE_TYPES:
            path = MODELS_DIR / f"anomaly_{device}.pkl"
            if path.exists():
                self._detectors[device] = joblib.load(path)
        global_path = MODELS_DIR / "anomaly_global.pkl"
        if global_path.exists():
            self._global_fallback = joblib.load(global_path)
        self._trained = True
        logger.info("Anomaly detectors loaded.")


anomaly_detector = AnomalyDetector()
