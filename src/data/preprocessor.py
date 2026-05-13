"""
Preprocessing pipeline: clean → scale → SMOTE → stratified split.
RobustScaler is used instead of StandardScaler (outlier-resistant).
"""
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.preprocessing import RobustScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from src.features.extractor import FEATURE_NAMES, DEVICE_TYPES, DEVICE_LABEL_MAP
from src.utils.logger import logger

MODELS_DIR = Path(__file__).resolve().parents[2] / "models"


class Preprocessor:
    def __init__(self):
        self.scaler = RobustScaler()
        self.label_encoder = LabelEncoder()
        self._train_medians: pd.Series = None
        self._fitted = False

    def fit_transform(self, df: pd.DataFrame):
        logger.info("Preprocessing: cleaning NaN/Inf values ...")
        X = df[FEATURE_NAMES].copy()
        y_labels = df['device_type'].values

        X.replace([np.inf, -np.inf], np.nan, inplace=True)
        self._train_medians = X.median()
        X.fillna(self._train_medians, inplace=True)
        X = X.clip(lower=0)

        y = np.array([DEVICE_LABEL_MAP[d] for d in y_labels])

        logger.info("Preprocessing: fitting RobustScaler ...")
        X_scaled = self.scaler.fit_transform(X)

        logger.info("Preprocessing: applying SMOTE oversampling ...")
        smote = SMOTE(random_state=42, k_neighbors=min(5, min(np.bincount(y)) - 1))
        X_resampled, y_resampled = smote.fit_resample(X_scaled, y)
        logger.info(f"After SMOTE: {X_resampled.shape[0]} samples")

        X_temp, X_test, y_temp, y_test = train_test_split(
            X_resampled, y_resampled, test_size=0.15, random_state=42, stratify=y_resampled)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=0.15 / 0.85, random_state=42, stratify=y_temp)

        logger.info(f"Split — train:{len(X_train)} val:{len(X_val)} test:{len(X_test)}")
        self._fitted = True
        return X_train, X_val, X_test, y_train, y_val, y_test

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        assert self._fitted, "Call fit_transform first"
        X = X[FEATURE_NAMES].copy()
        X.replace([np.inf, -np.inf], np.nan, inplace=True)
        X.fillna(self._train_medians, inplace=True)
        X = X.clip(lower=0)
        return self.scaler.transform(X)

    def transform_single(self, features: dict) -> np.ndarray:
        assert self._fitted, "Preprocessor not fitted"
        row = {f: features.get(f, 0.0) for f in FEATURE_NAMES}
        df = pd.DataFrame([row])
        return self.transform(df)

    def save(self):
        MODELS_DIR.mkdir(exist_ok=True)
        joblib.dump(self.scaler, MODELS_DIR / "scaler.pkl")
        if self._train_medians is not None:
            joblib.dump(self._train_medians, MODELS_DIR / "train_medians.pkl")
        logger.info("Scaler saved.")

    def load(self):
        path = MODELS_DIR / "scaler.pkl"
        if not path.exists():
            raise FileNotFoundError(f"Scaler not found at {path}. Run train.py first.")
        self.scaler = joblib.load(path)
        medians_path = MODELS_DIR / "train_medians.pkl"
        if medians_path.exists():
            self._train_medians = joblib.load(medians_path)
        else:
            self._train_medians = pd.Series(0.0, index=FEATURE_NAMES)
        self._fitted = True
        logger.info("Scaler loaded.")


preprocessor = Preprocessor()
