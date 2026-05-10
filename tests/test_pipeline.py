"""
pytest test suite — IoT Device Fingerprinting Framework
Run: pytest tests/ -v
"""
import sys
import numpy as np
import pandas as pd
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# ---------------------------------------------------------------------------
# Feature extractor tests
# ---------------------------------------------------------------------------
class TestFeatureExtractor:
    def test_feature_count(self):
        from src.features.extractor import FEATURE_NAMES
        assert len(FEATURE_NAMES) == 37, f"Expected 37 features, got {len(FEATURE_NAMES)}"

    def test_device_count(self):
        from src.features.extractor import DEVICE_TYPES
        assert len(DEVICE_TYPES) == 8

    def test_label_maps_consistent(self):
        from src.features.extractor import DEVICE_LABEL_MAP, LABEL_DEVICE_MAP, DEVICE_TYPES
        assert len(DEVICE_LABEL_MAP) == len(DEVICE_TYPES)
        for name, idx in DEVICE_LABEL_MAP.items():
            assert LABEL_DEVICE_MAP[idx] == name

    def test_feature_categories_cover_all(self):
        from src.features.extractor import FEATURE_NAMES, FEATURE_CATEGORIES
        all_in_cats = []
        for feats in FEATURE_CATEGORIES.values():
            all_in_cats.extend(feats)
        assert sorted(all_in_cats) == sorted(FEATURE_NAMES)


# ---------------------------------------------------------------------------
# Data generator tests
# ---------------------------------------------------------------------------
class TestDataGenerator:
    @pytest.fixture(scope="class")
    def dataset(self):
        from src.data.generator import generate_dataset
        return generate_dataset(save=False)

    def test_shape(self, dataset):
        assert dataset.shape[0] == 1600
        assert 'device_type' in dataset.columns
        assert 'is_anomaly' in dataset.columns

    def test_all_devices_present(self, dataset):
        from src.features.extractor import DEVICE_TYPES
        for d in DEVICE_TYPES:
            assert d in dataset['device_type'].values

    def test_flows_per_device(self, dataset):
        counts = dataset['device_type'].value_counts()
        for count in counts:
            assert count == 200

    def test_anomaly_fraction(self, dataset):
        anomaly_rate = dataset['is_anomaly'].mean()
        assert abs(anomaly_rate - 0.05) < 0.01

    def test_feature_completeness(self, dataset):
        from src.features.extractor import FEATURE_NAMES
        for f in FEATURE_NAMES:
            assert f in dataset.columns, f"Missing feature: {f}"
            assert dataset[f].isna().sum() == 0, f"NaN in feature: {f}"

    def test_no_negative_rates(self, dataset):
        for col in ['byte_rate', 'packet_rate', 'byte_count', 'packet_count']:
            assert (dataset[col] >= 0).all(), f"Negative values in {col}"

    def test_device_separation(self, dataset):
        """Smart camera byte_rate should be much higher than motion sensor."""
        cam_rate    = dataset[dataset['device_type'] == 'smart_camera']['byte_rate'].mean()
        sensor_rate = dataset[dataset['device_type'] == 'motion_sensor']['byte_rate'].mean()
        assert cam_rate > sensor_rate * 100, "Device profiles not sufficiently distinct"


# ---------------------------------------------------------------------------
# Preprocessor tests
# ---------------------------------------------------------------------------
class TestPreprocessor:
    @pytest.fixture(scope="class")
    def split_data(self):
        from src.data.generator import generate_dataset
        from src.data.preprocessor import Preprocessor
        df   = generate_dataset(save=False)
        prep = Preprocessor()
        return prep.fit_transform(df), prep

    def test_split_sizes(self, split_data):
        (X_train, X_val, X_test, y_train, y_val, y_test), prep = split_data
        total = len(X_train) + len(X_val) + len(X_test)
        assert len(X_train) > len(X_test)
        assert len(X_val) > 0

    def test_no_nan_after_scaling(self, split_data):
        (X_train, X_val, X_test, y_train, y_val, y_test), prep = split_data
        assert not np.isnan(X_train).any()
        assert not np.isnan(X_test).any()

    def test_feature_dimensions(self, split_data):
        (X_train, X_val, X_test, y_train, y_val, y_test), prep = split_data
        assert X_train.shape[1] == 37
        assert X_test.shape[1]  == 37

    def test_label_range(self, split_data):
        (X_train, X_val, X_test, y_train, y_val, y_test), prep = split_data
        assert y_train.min() == 0
        assert y_train.max() == 7

    def test_transform_single(self, split_data):
        (X_train, X_val, X_test, y_train, y_val, y_test), prep = split_data
        from src.features.extractor import FEATURE_NAMES
        features = {f: 0.0 for f in FEATURE_NAMES}
        result = prep.transform_single(features)
        assert result.shape == (1, 37)


# ---------------------------------------------------------------------------
# Fingerprinter tests
# ---------------------------------------------------------------------------
class TestFingerprinter:
    @pytest.fixture(scope="class")
    def trained_fp(self):
        from src.data.generator import generate_dataset
        from src.data.preprocessor import Preprocessor
        from src.models.fingerprinter import DeviceFingerprinter
        df   = generate_dataset(save=False)
        prep = Preprocessor()
        X_train, X_val, X_test, y_train, y_val, y_test = prep.fit_transform(df)
        fp = DeviceFingerprinter()
        fp.train(X_train, y_train, X_val, y_val)
        return fp, X_test, y_test

    def test_accuracy_above_threshold(self, trained_fp):
        from sklearn.metrics import accuracy_score
        fp, X_test, y_test = trained_fp
        labels, _ = fp.predict(X_test)
        from src.features.extractor import DEVICE_LABEL_MAP
        y_pred = [DEVICE_LABEL_MAP.get(l, -1) for l in labels if l != 'unknown']
        y_true_filtered = [y_test[i] for i, l in enumerate(labels) if l != 'unknown']
        acc = accuracy_score(y_true_filtered, y_pred) if y_pred else 0.0
        assert acc >= 0.90, f"Accuracy {acc:.3f} below 90%"

    def test_confidence_range(self, trained_fp):
        fp, X_test, y_test = trained_fp
        _, confs = fp.predict(X_test[:20])
        for c in confs:
            assert 0.0 <= c <= 1.0

    def test_feature_importances_present(self, trained_fp):
        fp, _, _ = trained_fp
        assert fp.feature_importances_ is not None
        assert len(fp.feature_importances_) == 37

    def test_predict_single(self, trained_fp):
        fp, X_test, _ = trained_fp
        label, conf = fp.predict_single(X_test[0])
        assert isinstance(label, str)
        assert 0.0 <= conf <= 1.0


# ---------------------------------------------------------------------------
# Anomaly Detector tests
# ---------------------------------------------------------------------------
class TestAnomalyDetector:
    @pytest.fixture(scope="class")
    def trained_ad(self):
        from src.data.generator import generate_dataset
        from src.data.preprocessor import Preprocessor
        from src.models.anomaly_detector import AnomalyDetector
        from src.features.extractor import FEATURE_NAMES
        df   = generate_dataset(save=False)
        prep = Preprocessor()
        prep.fit_transform(df)
        X_scaled = prep.transform(df[FEATURE_NAMES])
        ad = AnomalyDetector()
        ad.train(X_scaled, df['device_type'].values, df['is_anomaly'].values)
        return ad, X_scaled, df

    def test_normal_scores_low(self, trained_ad):
        ad, X_scaled, df = trained_ad
        # Score normal smart_camera flows against the smart_camera detector
        mask = (df['is_anomaly'] == 0) & (df['device_type'] == 'smart_camera')
        scores = ad.score(X_scaled[mask], 'smart_camera')
        assert scores.mean() < 0.70, f"Normal mean score too high: {scores.mean():.3f}"

    def test_anomaly_scores_high(self, trained_ad):
        ad, X_scaled, df = trained_ad
        mask = (df['is_anomaly'] == 1) & (df['device_type'] == 'smart_camera')
        if mask.sum() == 0:
            pytest.skip("No smart_camera anomalies in dataset")
        scores = ad.score(X_scaled[mask], 'smart_camera')
        assert scores.mean() > 0.50, f"Anomaly mean score too low: {scores.mean():.3f}"

    def test_score_range(self, trained_ad):
        ad, X_scaled, df = trained_ad
        scores = ad.score(X_scaled[:50], 'smart_tv')
        assert (scores >= 0.0).all() and (scores <= 1.0).all()

    def test_global_fallback(self, trained_ad):
        ad, X_scaled, _ = trained_ad
        scores = ad.score(X_scaled[:5], 'unknown_device')
        assert scores is not None
        assert len(scores) == 5


# ---------------------------------------------------------------------------
# Alert Manager tests
# ---------------------------------------------------------------------------
class TestAlertManager:
    def test_alert_generated_above_threshold(self):
        from src.utils.alert_manager import AlertManager
        mgr   = AlertManager(cooldown=0)
        alert = mgr.process("192.168.1.10", "smart_camera", 0.85)
        assert alert is not None
        assert alert.severity == "HIGH"

    def test_no_alert_below_threshold(self):
        from src.utils.alert_manager import AlertManager
        mgr   = AlertManager(cooldown=0)
        alert = mgr.process("192.168.1.10", "smart_camera", 0.40)
        assert alert is None

    def test_cooldown_suppresses_duplicate(self):
        from src.utils.alert_manager import AlertManager
        mgr = AlertManager(cooldown=60)
        mgr.process("192.168.1.1", "smart_camera", 0.85)
        alert2 = mgr.process("192.168.1.1", "smart_camera", 0.90)
        assert alert2 is None

    def test_severity_levels(self):
        from src.utils.alert_manager import AlertManager
        mgr = AlertManager(cooldown=0)
        cases = [(0.55, 'LOW'), (0.70, 'MEDIUM'), (0.85, 'HIGH'), (0.95, 'CRITICAL')]
        for score, expected_sev in cases:
            mgr._last_alert_time.clear()
            alert = mgr.process(f"10.0.0.{int(score*100)}", "smart_bulb", score)
            assert alert is not None and alert.severity == expected_sev, \
                f"Score {score}: expected {expected_sev}, got {alert.severity if alert else None}"

    def test_anomaly_rate(self):
        from src.utils.alert_manager import AlertManager
        mgr = AlertManager(cooldown=0)
        mgr.process("1.1.1.1", "smart_tv", 0.30)
        mgr.process("1.1.1.2", "smart_tv", 0.85)
        mgr.process("1.1.1.3", "smart_tv", 0.20)
        mgr.process("1.1.1.4", "smart_tv", 0.90)
        assert abs(mgr.anomaly_rate - 0.5) < 0.01
