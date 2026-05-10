"""Rate-limited alert manager with severity grading."""
import time
from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Deque, Dict, Optional
from src.utils.logger import logger


SEVERITY_THRESHOLDS = {
    'LOW':      (0.50, 0.65),
    'MEDIUM':   (0.65, 0.80),
    'HIGH':     (0.80, 0.90),
    'CRITICAL': (0.90, 1.01),
}
ALERT_COOLDOWN_SECONDS = 60
MAX_ALERTS = 500


@dataclass
class Alert:
    timestamp: float
    source_ip: str
    device_type: str
    anomaly_score: float
    severity: str
    message: str
    alert_id: int = 0


class AlertManager:
    def __init__(self, cooldown: int = ALERT_COOLDOWN_SECONDS, max_alerts: int = MAX_ALERTS):
        self._alerts: Deque[Alert] = deque(maxlen=max_alerts)
        self._last_alert_time: Dict[str, float] = defaultdict(float)
        self._cooldown = cooldown
        self._counter = 0
        self._total_processed = 0
        self._total_anomalies = 0

    def _get_severity(self, score: float) -> Optional[str]:
        for severity, (lo, hi) in SEVERITY_THRESHOLDS.items():
            if lo <= score < hi:
                return severity
        return None

    def process(self, source_ip: str, device_type: str, anomaly_score: float) -> Optional[Alert]:
        self._total_processed += 1
        severity = self._get_severity(anomaly_score)
        if severity is None:
            return None

        self._total_anomalies += 1
        now = time.time()
        if now - self._last_alert_time[source_ip] < self._cooldown:
            return None

        self._last_alert_time[source_ip] = now
        self._counter += 1
        alert = Alert(
            timestamp=now,
            source_ip=source_ip,
            device_type=device_type,
            anomaly_score=round(anomaly_score, 4),
            severity=severity,
            message=f"{severity} anomaly on {device_type} from {source_ip} (score={anomaly_score:.3f})",
            alert_id=self._counter,
        )
        self._alerts.append(alert)
        logger.warning(f"ALERT [{severity}] {alert.message}")
        return alert

    def recent(self, n: int = 50):
        alerts = list(self._alerts)
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)[:n]

    @property
    def anomaly_rate(self) -> float:
        if self._total_processed == 0:
            return 0.0
        return round(self._total_anomalies / self._total_processed, 4)

    @property
    def total_alerts(self) -> int:
        return self._counter


alert_manager = AlertManager()
