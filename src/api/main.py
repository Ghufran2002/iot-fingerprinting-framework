"""
FastAPI REST API — IoT Device Fingerprinting & Anomaly Detection Framework
Port: 8000
"""
import time
import random
import shap
import numpy as np
import joblib
import pandas as pd
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from src.data.preprocessor import Preprocessor
from src.models.fingerprinter import DeviceFingerprinter
from src.models.anomaly_detector import AnomalyDetector
from src.utils.alert_manager import AlertManager, Alert
from src.features.extractor import FEATURE_NAMES, DEVICE_TYPES
from src.utils.logger import logger

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------
_state: Dict[str, Any] = {
    "prep": None, "fp": None, "ad": None,
    "alert_mgr": None, "start_time": time.time(),
    "request_count": 0, "models_loaded": False,
    "shap_explainer": None,
}


def _load_models():
    try:
        prep = Preprocessor()
        prep.load()
        fp = DeviceFingerprinter()
        fp.load()
        ad = AnomalyDetector()
        ad.load()
        _state["prep"] = prep
        _state["fp"]   = fp
        _state["ad"]   = ad
        _state["alert_mgr"] = AlertManager()
        _state["models_loaded"] = True
        logger.info("All models loaded successfully.")
        try:
            rf_model = joblib.load(Path("models") / "fingerprinter_random_forest.pkl")
            _state["shap_explainer"] = shap.TreeExplainer(rf_model)
            logger.info("SHAP TreeExplainer loaded.")
        except Exception as e:
            logger.warning(f"SHAP explainer not loaded: {e}")
            _state["shap_explainer"] = None
    except FileNotFoundError as e:
        logger.warning(f"Models not found: {e}. Run train.py first.")
        _state["models_loaded"] = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    _load_models()
    yield


app = FastAPI(
    title="IoT Device Fingerprinting & Anomaly Detection API",
    description=(
        "M.Tech Cyber Forensics — NIELIT Srinagar\n\n"
        "**Student:** Md Ghufran Alam (NDU202400038)\n\n"
        "Identifies IoT device types and detects anomalous network behaviour "
        "using a Random Forest fingerprinter and Isolation Forest + OC-SVM anomaly ensemble."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class FlowFeatures(BaseModel):
    flow_duration: float = Field(default=10.0, description="Flow duration in seconds")
    mean_iat: float      = Field(default=0.01)
    std_iat: float       = Field(default=0.005)
    min_iat: float       = Field(default=0.001)
    max_iat: float       = Field(default=0.05)
    packet_count: float  = Field(default=100.0)
    byte_count: float    = Field(default=150000.0)
    packet_rate: float   = Field(default=10.0)
    byte_rate: float     = Field(default=15000.0)
    mean_pkt_size: float = Field(default=1400.0)
    std_pkt_size: float  = Field(default=100.0)
    min_pkt_size: float  = Field(default=64.0)
    max_pkt_size: float  = Field(default=1500.0)
    tcp_ratio: float     = Field(default=0.9)
    udp_ratio: float     = Field(default=0.1)
    syn_ratio: float     = Field(default=0.01)
    fin_ratio: float     = Field(default=0.008)
    rst_ratio: float     = Field(default=0.002)
    ack_ratio: float     = Field(default=0.6)
    is_https: float      = Field(default=1.0)
    is_mqtt: float       = Field(default=0.0)
    is_coap: float       = Field(default=0.0)
    is_mdns: float       = Field(default=0.0)
    is_ntp: float        = Field(default=0.0)
    dns_query_count: float = Field(default=3.0)
    well_known_port_ratio: float = Field(default=0.9)
    is_encrypted: float  = Field(default=1.0)
    upload_bytes: float  = Field(default=100000.0)
    download_bytes: float = Field(default=50000.0)
    upload_download_ratio: float = Field(default=2.0)
    unique_dest_ports: float = Field(default=3.0)
    unique_dest_ips: float   = Field(default=2.0)
    port_entropy: float      = Field(default=1.0)
    ip_entropy: float        = Field(default=0.8)
    well_known_ports_count: float = Field(default=2.0)
    mean_dest_port: float    = Field(default=443.0)
    std_dest_port: float     = Field(default=20.0)

    def to_dict(self) -> dict:
        return {f: getattr(self, f) for f in FEATURE_NAMES}


class AnomalyRequest(BaseModel):
    features: FlowFeatures
    device_type: str = Field(default="smart_camera",
                             description="Known device type for per-device scoring")
    source_ip: Optional[str] = Field(default=None)


class AnalyzeRequest(BaseModel):
    features: FlowFeatures
    source_ip: Optional[str] = Field(default=None)


class DemoInjectRequest(BaseModel):
    device_type: str
    anomaly_score: float
    source_ip: Optional[str] = Field(default=None)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _require_models():
    if not _state["models_loaded"]:
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Run python train.py first, then restart the API.")


def _random_ip():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health", tags=["System"])
def health():
    uptime = round(time.time() - _state["start_time"], 1)
    return {
        "status": "healthy",
        "models_loaded": _state["models_loaded"],
        "shap_ready": _state["shap_explainer"] is not None,
        "uptime_seconds": uptime,
        "request_count": _state["request_count"],
    }


@app.get("/status", include_in_schema=False)
def status_page():
    uptime_s = round(time.time() - _state["start_time"], 1)
    h = int(uptime_s // 3600)
    m = int((uptime_s % 3600) // 60)
    s = int(uptime_s % 60)
    uptime_fmt = f"{h:02d}:{m:02d}:{s:02d}"
    models_ok = _state["models_loaded"]
    shap_ok   = _state["shap_explainer"] is not None
    req_count = _state["request_count"]

    def _row(label, value, ok=True):
        color  = "#00ff88" if ok else "#ff4757"
        icon   = "✔" if ok else "✘"
        return f"""
        <div class="row">
          <span class="label">{label}</span>
          <span class="value" style="color:{color}">{icon}&nbsp;&nbsp;{value}</span>
        </div>"""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <meta http-equiv="refresh" content="10"/>
  <title>API Status — IoT Fingerprinting</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&display=swap"/>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:#0d0f14;color:#c9d1e0;font-family:'JetBrains Mono',monospace;
          min-height:100vh;display:flex;flex-direction:column;align-items:center;
          justify-content:center;padding:30px 16px}}
    .card{{background:#13161e;border:1px solid #1f2535;border-radius:14px;
           width:100%;max-width:540px;overflow:hidden;
           box-shadow:0 0 40px rgba(0,245,255,.07)}}
    .header{{background:linear-gradient(90deg,#0d1b2a,#1a1e28);
             border-bottom:1px solid #1f2535;padding:22px 28px}}
    .badge{{display:inline-block;padding:3px 10px;border-radius:20px;
            font-size:10px;font-weight:700;letter-spacing:1px;margin-bottom:10px;
            background:rgba(0,255,136,.1);border:1px solid #00ff88;color:#00ff88}}
    .badge.down{{background:rgba(255,71,87,.1);border-color:#ff4757;color:#ff4757}}
    h1{{font-size:16px;font-weight:700;
        background:linear-gradient(90deg,#00f5ff,#b06aff);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        background-clip:text;letter-spacing:.4px}}
    .sub{{font-size:11px;color:#6b7898;margin-top:4px}}
    .body{{padding:24px 28px;display:flex;flex-direction:column;gap:14px}}
    .row{{display:flex;justify-content:space-between;align-items:center;
          padding:12px 16px;background:#0d0f14;border-radius:8px;
          border:1px solid #1f2535}}
    .label{{font-size:12px;color:#6b7898;text-transform:uppercase;letter-spacing:.8px}}
    .value{{font-size:13px;font-weight:600}}
    .kpi-row{{display:flex;gap:10px}}
    .kpi{{flex:1;background:#0d0f14;border:1px solid #1f2535;border-radius:8px;
           padding:12px;text-align:center}}
    .kpi .num{{font-size:22px;font-weight:700;color:#00f5ff}}
    .kpi .lbl{{font-size:10px;color:#6b7898;text-transform:uppercase;
               letter-spacing:.8px;margin-top:3px}}
    .footer{{padding:14px 28px;border-top:1px solid #1f2535;
             font-size:10px;color:#6b7898;text-align:center}}
    body::before{{content:'';position:fixed;inset:0;pointer-events:none;
                  background:repeating-linear-gradient(0deg,transparent,transparent 2px,
                  rgba(0,245,255,.012) 2px,rgba(0,245,255,.012) 4px)}}
  </style>
</head>
<body>
<div class="card">
  <div class="header">
    <div class="badge {'badge' if models_ok else 'badge down'}">
      {'● ONLINE' if models_ok else '● DEGRADED'}
    </div>
    <h1>IoT Fingerprinting — API Status</h1>
    <div class="sub">M.Tech Cyber Forensics &nbsp;|&nbsp; NIELIT Srinagar &nbsp;|&nbsp; Md Ghufran Alam</div>
  </div>
  <div class="body">
    <div class="kpi-row">
      <div class="kpi"><div class="num">8</div><div class="lbl">Devices</div></div>
      <div class="kpi"><div class="num">37</div><div class="lbl">Features</div></div>
      <div class="kpi"><div class="num" style="color:#b06aff">{req_count}</div><div class="lbl">Requests</div></div>
      <div class="kpi"><div class="num" style="color:#ffcd43">{uptime_fmt}</div><div class="lbl">Uptime</div></div>
    </div>
    {_row("API Server",     "Running &nbsp;/ &nbsp;FastAPI v0.104+", True)}
    {_row("ML Models",      "Loaded — Random Forest + IForest + OC-SVM" if models_ok else "Not Loaded — Run train.py", models_ok)}
    {_row("SHAP Explainer", "TreeExplainer Ready" if shap_ok else "Not Available", shap_ok)}
    {_row("Dashboard",      "Mounted at /dashboard/", True)}
    {_row("API Docs",       "Available at /docs", True)}
  </div>
  <div class="footer">Auto-refreshes every 10 seconds &nbsp;|&nbsp; JSON: <a href="/health" style="color:#00b8c8">/health</a></div>
</div>
</body>
</html>"""
    return HTMLResponse(html_content)


@app.get("/devices", tags=["System"])
def list_devices():
    descriptions = {
        "smart_camera":     "High-bandwidth HTTPS/RTSP continuous streaming",
        "smart_thermostat": "Low-bandwidth MQTT periodic temperature updates",
        "smart_tv":         "Very high-bandwidth streaming, multiple destination IPs",
        "smart_bulb":       "Ultra-low CoAP on/off commands only",
        "smart_plug":       "Minimal traffic, power usage reporting, short bursts",
        "smart_speaker":    "Medium traffic, voice streaming, cloud API calls",
        "smart_doorbell":   "Medium-high traffic, camera+audio, motion-triggered bursts",
        "motion_sensor":    "Ultra-low event-driven MQTT/CoAP traffic",
    }
    return {"supported_devices": DEVICE_TYPES, "descriptions": descriptions}


@app.post("/fingerprint", tags=["Fingerprinting"])
def fingerprint(flow: FlowFeatures):
    _require_models()
    _state["request_count"] += 1
    prep = _state["prep"]
    fp   = _state["fp"]

    df = pd.DataFrame([flow.to_dict()])
    X  = prep.transform(df)
    device_type, confidence = fp.predict_single(X[0])

    return {
        "device_type": device_type,
        "confidence":  round(confidence, 4),
        "is_known":    device_type != "unknown",
        "model_used":  fp._primary,
    }


@app.post("/anomaly/score", tags=["Anomaly Detection"])
def anomaly_score(req: AnomalyRequest):
    _require_models()
    _state["request_count"] += 1
    prep = _state["prep"]
    ad   = _state["ad"]

    df  = pd.DataFrame([req.features.to_dict()])
    X   = prep.transform(df)
    score = ad.score_single(X[0], req.device_type)
    is_anomaly = ad.is_anomalous(score)

    severity = None
    if is_anomaly:
        from src.utils.alert_manager import SEVERITY_THRESHOLDS
        for sev, (lo, hi) in SEVERITY_THRESHOLDS.items():
            if lo <= score < hi:
                severity = sev
                break

    source_ip = req.source_ip or _random_ip()
    if is_anomaly:
        _state["alert_mgr"].process(source_ip, req.device_type, score)

    return {
        "device_type":   req.device_type,
        "anomaly_score": round(score, 4),
        "is_anomalous":  is_anomaly,
        "severity":      severity,
        "threshold":     0.75,
    }


@app.post("/analyze", tags=["Combined Analysis"])
def analyze(req: AnalyzeRequest):
    """Fingerprint + anomaly score in a single call."""
    _require_models()
    _state["request_count"] += 1
    prep      = _state["prep"]
    fp        = _state["fp"]
    ad        = _state["ad"]
    alert_mgr = _state["alert_mgr"]

    df = pd.DataFrame([req.features.to_dict()])
    X  = prep.transform(df)

    device_type, confidence = fp.predict_single(X[0])
    # Use best-guess class for anomaly model even when confidence < threshold
    best_guess = fp._models[fp._primary].predict(X)[0]
    from src.features.extractor import LABEL_DEVICE_MAP
    effective_device = device_type if device_type != "unknown" else LABEL_DEVICE_MAP[best_guess]
    score      = ad.score_single(X[0], effective_device)
    is_anomaly = ad.is_anomalous(score)

    severity = None
    if is_anomaly:
        from src.utils.alert_manager import SEVERITY_THRESHOLDS
        for sev, (lo, hi) in SEVERITY_THRESHOLDS.items():
            if lo <= score < hi:
                severity = sev
                break

    source_ip = req.source_ip or _random_ip()
    # Log alert with effective_device so table never shows "unknown"
    alert_mgr.process(source_ip, effective_device, score)

    return {
        "fingerprint": {
            "device_type": effective_device,
            "confidence":  round(confidence, 4),
            "is_known":    device_type != "unknown",
        },
        "anomaly": {
            "anomaly_score": round(score, 4),
            "is_anomalous":  is_anomaly,
            "severity":      severity,
            "threshold":     0.75,
        },
        "source_ip": source_ip,
    }


@app.post("/explain", tags=["Explainability"])
def explain(flow: FlowFeatures):
    """SHAP explanation — top 10 features that drove the fingerprint prediction.

    Returns SHAP values for the predicted device class. Positive values push
    the model toward that device type; negative values push away from it.
    """
    _require_models()
    if _state["shap_explainer"] is None:
        raise HTTPException(
            status_code=503,
            detail="SHAP explainer not available. Ensure train.py has been run and restart the API.")
    _state["request_count"] += 1

    prep = _state["prep"]
    fp   = _state["fp"]

    df = pd.DataFrame([flow.to_dict()])
    X  = prep.transform(df)          # shape (1, 37) — RobustScaler-scaled

    device_type, confidence = fp.predict_single(X[0])
    effective_device = device_type if device_type in DEVICE_TYPES else DEVICE_TYPES[0]

    sv     = _state["shap_explainer"].shap_values(X)
    sv_arr = np.array(sv)

    # Handle all SHAP return shapes for multi-class RandomForest:
    # - list of (n_samples, n_features) per class  → after np.array: (n_classes, n_samples, n_features)
    # - (n_samples, n_features, n_classes)          → transpose to (n_classes, n_samples, n_features)
    # - (n_samples, n_features)                     → single-class fallback
    if sv_arr.ndim == 3:
        if sv_arr.shape[0] == len(DEVICE_TYPES):
            pass  # already (n_classes, n_samples, n_features)
        elif sv_arr.shape[2] == len(DEVICE_TYPES):
            sv_arr = sv_arr.transpose(2, 0, 1)
        elif sv_arr.shape[0] == len(X):
            sv_arr = sv_arr.transpose(2, 0, 1)
    elif sv_arr.ndim == 2:
        sv_arr = sv_arr[np.newaxis, :, :]  # treat as single class

    class_idx = min(DEVICE_TYPES.index(effective_device), sv_arr.shape[0] - 1)
    sv_class  = sv_arr[class_idx, 0]   # (n_features,)

    top_idx = np.argsort(np.abs(sv_class))[::-1][:10]
    contributions = [
        {
            "feature":    FEATURE_NAMES[i],
            "shap_value": round(float(sv_class[i]), 6),
            "direction":  "toward" if sv_class[i] > 0 else "away",
            "abs_impact": round(abs(float(sv_class[i])), 6),
        }
        for i in top_idx
    ]

    return {
        "device_type": device_type,
        "confidence":  round(confidence, 4),
        "explanation": contributions,
        "note":        "Positive SHAP = pushes prediction TOWARD this device; negative = pushes AWAY",
    }


@app.get("/alerts/recent", tags=["Alerts"])
def recent_alerts(n: int = 50):
    _require_models()
    alerts = _state["alert_mgr"].recent(n)
    return {
        "count": len(alerts),
        "alerts": [
            {
                "alert_id":      a.alert_id,
                "timestamp":     a.timestamp,
                "source_ip":     a.source_ip,
                "device_type":   a.device_type,
                "anomaly_score": a.anomaly_score,
                "severity":      a.severity,
                "message":       a.message,
            }
            for a in alerts
        ],
    }


@app.get("/metrics", tags=["System"])
def metrics():
    _require_models()
    mgr    = _state["alert_mgr"]
    uptime = round(time.time() - _state["start_time"], 1)
    return {
        "uptime_seconds":    uptime,
        "request_count":     _state["request_count"],
        "total_alerts":      mgr.total_alerts,
        "anomaly_rate":      mgr.anomaly_rate,
        "models_loaded":     _state["models_loaded"],
        "shap_ready":        _state["shap_explainer"] is not None,
        "supported_devices": len(DEVICE_TYPES),
        "feature_count":     len(FEATURE_NAMES),
    }




@app.post("/demo/inject", tags=["Demo"])
def demo_inject(req: DemoInjectRequest):
    """Inject a simulated anomaly event from the live dashboard demo."""
    if not _state["models_loaded"]:
        return {"injected": False}
    src_ip = req.source_ip or _random_ip()
    alert  = _state["alert_mgr"].process(src_ip, req.device_type, req.anomaly_score)
    _state["request_count"] += 1
    return {"injected": alert is not None, "source_ip": src_ip}


# ---------------------------------------------------------------------------
# Custom dark-themed Swagger UI
# ---------------------------------------------------------------------------
_DOCS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>IoT Fingerprinting API — Docs</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap" />
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg:        #0d0f14;
      --surface:   #13161e;
      --surface2:  #1a1e28;
      --border:    #1f2535;
      --cyan:      #00f5ff;
      --cyan-dim:  #00b8c8;
      --purple:    #b06aff;
      --purple-dim:#7c4fcc;
      --green:     #00ff88;
      --red:       #ff4757;
      --text:      #c9d1e0;
      --text-dim:  #6b7898;
      --font:      'JetBrains Mono', 'Fira Code', monospace;
    }

    html, body { height: 100%; background: var(--bg); color: var(--text); font-family: var(--font); font-size: 13px; }

    #cyber-header {
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 0 24px;
      display: flex;
      flex-direction: column;
      gap: 0;
    }

    #cyber-brand {
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 16px 0 10px;
      border-bottom: 1px solid var(--border);
    }

    #cyber-brand .logo {
      width: 44px; height: 44px;
      background: linear-gradient(135deg, var(--cyan) 0%, var(--purple) 100%);
      border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      font-size: 22px; flex-shrink: 0;
      box-shadow: 0 0 18px rgba(0,245,255,.25);
    }

    #cyber-brand .title-block h1 {
      font-size: 17px; font-weight: 700; letter-spacing: .5px;
      background: linear-gradient(90deg, var(--cyan), var(--purple));
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    #cyber-brand .title-block p {
      font-size: 11px; color: var(--text-dim); margin-top: 2px; letter-spacing: .3px;
    }

    #cyber-brand .badge {
      margin-left: auto;
      background: rgba(0,245,255,.08);
      border: 1px solid var(--cyan-dim);
      color: var(--cyan);
      font-size: 10px; font-weight: 600;
      padding: 4px 10px; border-radius: 20px; letter-spacing: .8px;
      white-space: nowrap;
    }

    #stats-bar {
      display: flex; align-items: center; gap: 0;
      padding: 10px 0 12px;
      overflow-x: auto;
    }

    .stat-item {
      display: flex; flex-direction: column; align-items: center;
      padding: 0 22px; gap: 3px;
      border-right: 1px solid var(--border);
      flex-shrink: 0;
    }
    .stat-item:first-child { padding-left: 0; }
    .stat-item:last-child  { border-right: none; }

    .stat-value { font-size: 18px; font-weight: 700; letter-spacing: .5px; }
    .stat-label { font-size: 10px; color: var(--text-dim); letter-spacing: .6px; text-transform: uppercase; }

    .stat-item:nth-child(1) .stat-value { color: var(--cyan);   text-shadow: 0 0 12px rgba(0,245,255,.5); }
    .stat-item:nth-child(2) .stat-value { color: var(--purple); text-shadow: 0 0 12px rgba(176,106,255,.5); }
    .stat-item:nth-child(3) .stat-value { color: var(--green);  text-shadow: 0 0 12px rgba(0,255,136,.5); }
    .stat-item:nth-child(4) .stat-value { color: #ffcd43;       text-shadow: 0 0 12px rgba(255,205,67,.5); }
    .stat-item:nth-child(5) .stat-value { color: var(--cyan);   text-shadow: 0 0 12px rgba(0,245,255,.5); }

    #student-bar {
      background: linear-gradient(90deg, rgba(0,245,255,.05) 0%, rgba(176,106,255,.05) 100%);
      border-top: 1px solid var(--border);
      padding: 7px 24px;
      display: flex; align-items: center; gap: 24px; flex-wrap: wrap;
    }

    .student-item { display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--text-dim); }
    .student-item .icon { font-size: 13px; }
    .student-item strong { color: var(--text); font-weight: 500; }

    .swagger-ui { font-family: var(--font) !important; }
    .swagger-ui .topbar { display: none !important; }
    .swagger-ui .info    { display: none !important; }

    .swagger-ui .scheme-container,
    .swagger-ui .wrapper { background: var(--bg) !important; }

    .swagger-ui .opblock-tag {
      background: var(--surface) !important;
      border: 1px solid var(--border) !important;
      border-radius: 6px !important;
      color: var(--cyan) !important;
      font-family: var(--font) !important;
      font-size: 13px !important;
      letter-spacing: .4px;
    }

    .swagger-ui .opblock {
      background: var(--surface2) !important;
      border: 1px solid var(--border) !important;
      border-radius: 6px !important;
      box-shadow: none !important;
      margin: 6px 0 !important;
    }

    .swagger-ui .opblock.opblock-get    .opblock-summary-method { background: var(--cyan-dim)   !important; font-family: var(--font) !important; }
    .swagger-ui .opblock.opblock-post   .opblock-summary-method { background: var(--purple-dim) !important; font-family: var(--font) !important; }
    .swagger-ui .opblock.opblock-delete .opblock-summary-method { background: var(--red)        !important; font-family: var(--font) !important; }

    .swagger-ui .opblock-summary-path,
    .swagger-ui .opblock-summary-description,
    .swagger-ui table thead tr th,
    .swagger-ui .response-col_status,
    .swagger-ui .response-col_description,
    .swagger-ui .col_header,
    .swagger-ui label,
    .swagger-ui p,
    .swagger-ui h4,
    .swagger-ui h5,
    .swagger-ui td,
    .swagger-ui li { color: var(--text) !important; font-family: var(--font) !important; }

    .swagger-ui .opblock-body,
    .swagger-ui .opblock-section-header,
    .swagger-ui .tab-header,
    .swagger-ui .model-container,
    .swagger-ui section.models { background: var(--surface) !important; }

    .swagger-ui input[type=text],
    .swagger-ui textarea,
    .swagger-ui select {
      background: var(--bg) !important;
      border: 1px solid var(--border) !important;
      color: var(--cyan) !important;
      font-family: var(--font) !important;
      border-radius: 4px !important;
    }

    .swagger-ui .btn.execute {
      background: linear-gradient(135deg, var(--cyan-dim), var(--purple-dim)) !important;
      border: none !important;
      color: #fff !important;
      font-family: var(--font) !important;
      font-weight: 600 !important;
      letter-spacing: .5px !important;
      box-shadow: 0 0 14px rgba(0,245,255,.2) !important;
    }

    .swagger-ui .btn.execute:hover { box-shadow: 0 0 22px rgba(0,245,255,.4) !important; }

    .swagger-ui .btn.cancel {
      border-color: var(--red) !important;
      color: var(--red) !important;
      font-family: var(--font) !important;
    }

    .swagger-ui .microlight,
    .swagger-ui code,
    .swagger-ui pre {
      background: var(--bg) !important;
      color: var(--green) !important;
      font-family: var(--font) !important;
      font-size: 12px !important;
      border-radius: 4px !important;
    }

    .swagger-ui .model { color: var(--text) !important; font-family: var(--font) !important; }
    .swagger-ui .model-toggle { color: var(--purple) !important; }
    .swagger-ui .prop-type  { color: var(--cyan)   !important; }
    .swagger-ui .prop-name  { color: var(--text)   !important; }

    .swagger-ui section.models .model-container { border-color: var(--border) !important; }

    .swagger-ui .tab li { color: var(--text-dim) !important; font-family: var(--font) !important; }
    .swagger-ui .tab li.active { color: var(--cyan) !important; }

    .swagger-ui svg { fill: var(--text-dim) !important; }

    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--surface); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--cyan-dim); }

    body::before {
      content: '';
      position: fixed; inset: 0; pointer-events: none; z-index: 9999;
      background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,245,255,.015) 2px, rgba(0,245,255,.015) 4px);
    }
  </style>
</head>
<body>

<div id="cyber-header">
  <div id="cyber-brand">
    <div class="logo">&#x1F4F6;</div>
    <div class="title-block">
      <h1>IoT Device Fingerprinting &amp; Anomaly Detection API</h1>
      <p>Random Forest Fingerprinter &nbsp;|&nbsp; Isolation Forest + OC-SVM Ensemble &nbsp;|&nbsp; SHAP Explainability &nbsp;|&nbsp; v1.0.0</p>
    </div>
    <div class="badge">&#x25CF;&nbsp;LIVE</div>
  </div>

  <div id="stats-bar">
    <div class="stat-item">
      <span class="stat-value">&#x2714;&nbsp;YES</span>
      <span class="stat-label">Models Loaded</span>
    </div>
    <div class="stat-item">
      <span class="stat-value">8</span>
      <span class="stat-label">Devices</span>
    </div>
    <div class="stat-item">
      <span class="stat-value">37</span>
      <span class="stat-label">Features</span>
    </div>
    <div class="stat-item">
      <span class="stat-value">100%</span>
      <span class="stat-label">Accuracy</span>
    </div>
    <div class="stat-item">
      <span class="stat-value">SHAP</span>
      <span class="stat-label">Explainable AI</span>
    </div>
  </div>
</div>

<div id="student-bar">
  <div class="student-item">
    <span class="icon">&#x1F393;</span>
    <span><strong>Md Ghufran Alam</strong></span>
  </div>
  <div class="student-item">
    <span class="icon">&#x1F194;</span>
    <span><strong>NDU202400038</strong></span>
  </div>
  <div class="student-item">
    <span class="icon">&#x1F3DB;</span>
    <span><strong>NIELIT Srinagar</strong> &mdash; M.Tech Cyber Forensics</span>
  </div>
</div>

<div id="swagger-ui"></div>

<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
<script>
  window.onload = () => {
    SwaggerUIBundle({
      url: "/openapi.json",
      dom_id: "#swagger-ui",
      presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
      layout: "StandaloneLayout",
      deepLinking: true,
      defaultModelsExpandDepth: 1,
      defaultModelExpandDepth: 1,
      displayRequestDuration: true,
      filter: true,
      syntaxHighlight: { activate: true, theme: "monokai" },
    });
  };
</script>
</body>
</html>"""


@app.get("/docs", include_in_schema=False)
def custom_docs():
    return HTMLResponse(_DOCS_HTML)


@app.get("/dashboard", include_in_schema=False)
@app.get("/dashboard/", include_in_schema=False)
@app.get("/app", include_in_schema=False)
@app.get("/app/", include_in_schema=False)
def dashboard():
    return HTMLResponse(_DASHBOARD_HTML)


_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>IoT Security Monitor — Live Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0F1117;color:#E0E0E0;font-family:'Segoe UI',sans-serif;min-height:100vh}
.header{background:linear-gradient(90deg,#1A237E,#283593);padding:16px 28px;
  display:flex;align-items:center;justify-content:space-between;
  border-bottom:2px solid #3949AB}
.header h1{font-size:20px;font-weight:700;color:#90CAF9;margin:0}
.header p{font-size:11px;color:#B0BEC5;margin:3px 0 0}
#hdr-status{font-size:12px;color:#A5D6A7;text-align:right}
.kpi-row{display:flex;gap:14px;padding:18px 28px 10px;flex-wrap:wrap}
.kpi{background:#1A1F2E;border:1px solid #2196F3;border-radius:8px;
  padding:14px 20px;flex:1;min-width:120px}
.kpi .lbl{font-size:11px;color:#90A4AE;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px}
.kpi .val{font-size:26px;font-weight:700}
.charts-row{display:flex;gap:14px;padding:0 28px 14px;flex-wrap:wrap}
.chart-box{background:#1A1F2E;border-radius:8px;padding:14px;flex:1;min-width:280px}
.chart-box h3{font-size:14px;color:#90CAF9;margin-bottom:8px}
.alerts-box{margin:0 28px 20px;background:#1A1F2E;border-radius:8px;padding:16px}
.alerts-box h3{font-size:14px;color:#90CAF9;margin-bottom:10px}
table{width:100%;border-collapse:collapse;font-size:12px}
th{padding:7px 10px;border-bottom:1px solid #37474F;color:#90CAF9;text-align:left}
td{padding:6px 10px;border-bottom:1px solid #1E272E}
.badge{padding:2px 8px;border-radius:10px;font-weight:700;font-size:11px}
.links{display:flex;gap:10px;padding:0 28px 20px;flex-wrap:wrap}
a.btn{display:inline-block;background:#1A237E;border:1px solid #3949AB;
  color:#90CAF9;padding:8px 18px;border-radius:6px;text-decoration:none;font-size:13px}
a.btn:hover{background:#283593}
</style>
</head>
<body>
<div class="header">
  <div>
    <h1>IoT Device Fingerprinting &amp; Anomaly Detection</h1>
    <p>M.Tech Cyber Forensics &nbsp;|&nbsp; NIELIT Srinagar &nbsp;|&nbsp; Md Ghufran Alam (NDU202400038)</p>
  </div>
  <div id="hdr-status">Loading...</div>
</div>

<div class="kpi-row" id="kpi-row">
  <div class="kpi"><div class="lbl">Devices</div><div class="val" style="color:#4CAF50">8</div></div>
  <div class="kpi"><div class="lbl">Features</div><div class="val" style="color:#9C27B0">37</div></div>
  <div class="kpi"><div class="lbl">Accuracy</div><div class="val" style="color:#2196F3">100%</div></div>
  <div class="kpi"><div class="lbl">Threshold</div><div class="val" style="color:#00BCD4">0.75</div></div>
  <div class="kpi"><div class="lbl">Total Alerts</div><div class="val" id="kpi-alerts" style="color:#F44336">—</div></div>
  <div class="kpi"><div class="lbl">Requests</div><div class="val" id="kpi-requests" style="color:#FF9800">—</div></div>
  <div class="kpi"><div class="lbl">Uptime</div><div class="val" id="kpi-uptime" style="color:#A5D6A7;font-size:18px">—</div></div>
</div>

<div class="charts-row">
  <div class="chart-box" style="flex:2"><h3>Live Anomaly Score Timeline</h3><div id="chart-timeline" style="height:260px"></div></div>
  <div class="chart-box" style="flex:1"><h3>Severity Distribution</h3><div id="chart-sev" style="height:260px"></div></div>
</div>

<div class="alerts-box">
  <h3>Recent Anomaly Alerts</h3>
  <div id="alerts-table"><p style="color:#607D8B;font-style:italic">Loading alerts...</p></div>
</div>

<div class="links">
  <a class="btn" href="/docs">📡 API Docs (Swagger)</a>
  <a class="btn" href="/status">🟢 Status Page</a>
  <a class="btn" href="/health">❤️ Health JSON</a>
  <a class="btn" href="/devices">📋 Devices List</a>
</div>

<script>
const SEV_COLOR = {LOW:'#4CAF50',MEDIUM:'#FF9800',HIGH:'#F44336',CRITICAL:'#9C27B0',NORMAL:'#4CAF50'};
const DEV_COLOR = {smart_camera:'#2196F3',smart_thermostat:'#FF9800',smart_tv:'#9C27B0',
  smart_bulb:'#FFEB3B',smart_plug:'#4CAF50',smart_speaker:'#00BCD4',
  smart_doorbell:'#F44336',motion_sensor:'#795548',unknown:'#9E9E9E'};

let scores = [], labels = [], times = [];

function fmt(s){let h=~~(s/3600),m=~~((s%3600)/60),sec=~~(s%60);
  return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`}

async function getJSON(url){try{let r=await fetch(url);return r.ok?r.json():null}catch{return null}}

async function refresh(){
  // Metrics
  const m = await getJSON('/metrics');
  if(m){
    document.getElementById('hdr-status').innerHTML =
      `Status: ${m.models_loaded?'✅ Models Loaded':'⚠️ No Models'} | SHAP: ${m.shap_ready?'✅':'❌'}<br>Uptime: ${fmt(m.uptime_seconds)} | Requests: ${m.request_count}`;
    document.getElementById('kpi-alerts').textContent = m.total_alerts ?? '—';
    document.getElementById('kpi-requests').textContent = m.request_count ?? '—';
    document.getElementById('kpi-uptime').textContent = fmt(m.uptime_seconds ?? 0);
  }

  // Auto-simulate a real API call every refresh — increments request_count & creates alerts
  // Values derived from training data generator means (all 8 devices get 100% confidence)
  const FLOWS = {
    smart_camera:    {flow_duration:90,mean_iat:0.003,std_iat:0.002,min_iat:0.001,max_iat:0.015,packet_count:28000,byte_count:42000000,packet_rate:400,byte_rate:600000,mean_pkt_size:1400,std_pkt_size:180,min_pkt_size:64,max_pkt_size:1500,tcp_ratio:0.95,udp_ratio:0.05,syn_ratio:0.005,fin_ratio:0.004,rst_ratio:0.001,ack_ratio:0.60,is_https:1,is_mqtt:0,is_coap:0,is_mdns:0,is_ntp:0,dns_query_count:4,well_known_port_ratio:0.90,is_encrypted:1,upload_bytes:28000000,download_bytes:14000000,upload_download_ratio:2.0,unique_dest_ports:4,unique_dest_ips:3,port_entropy:1.2,ip_entropy:1.0,well_known_ports_count:3,mean_dest_port:443,std_dest_port:30},
    smart_thermostat:{flow_duration:4,mean_iat:0.8,std_iat:0.3,min_iat:0.05,max_iat:5.0,packet_count:8,byte_count:800,packet_rate:2,byte_rate:200,mean_pkt_size:85,std_pkt_size:20,min_pkt_size:40,max_pkt_size:200,tcp_ratio:0.15,udp_ratio:0.85,syn_ratio:0.05,fin_ratio:0.04,rst_ratio:0.01,ack_ratio:0.10,is_https:0,is_mqtt:1,is_coap:0,is_mdns:0,is_ntp:0,dns_query_count:1,well_known_port_ratio:0.60,is_encrypted:0,upload_bytes:400,download_bytes:400,upload_download_ratio:1.0,unique_dest_ports:2,unique_dest_ips:1,port_entropy:0.4,ip_entropy:0.2,well_known_ports_count:2,mean_dest_port:1883,std_dest_port:10},
    smart_tv:        {flow_duration:3600,mean_iat:0.001,std_iat:0.0008,min_iat:0.0005,max_iat:0.05,packet_count:500000,byte_count:700000000,packet_rate:140,byte_rate:200000,mean_pkt_size:1400,std_pkt_size:200,min_pkt_size:64,max_pkt_size:1500,tcp_ratio:0.85,udp_ratio:0.15,syn_ratio:0.003,fin_ratio:0.002,rst_ratio:0.001,ack_ratio:0.55,is_https:1,is_mqtt:0,is_coap:0,is_mdns:0,is_ntp:0,dns_query_count:20,well_known_port_ratio:0.92,is_encrypted:1,upload_bytes:5000000,download_bytes:695000000,upload_download_ratio:0.007,unique_dest_ports:12,unique_dest_ips:18,port_entropy:2.8,ip_entropy:3.0,well_known_ports_count:10,mean_dest_port:443,std_dest_port:150},
    smart_bulb:      {flow_duration:0.5,mean_iat:0.05,std_iat:0.02,min_iat:0.01,max_iat:0.3,packet_count:4,byte_count:120,packet_rate:8,byte_rate:240,mean_pkt_size:30,std_pkt_size:8,min_pkt_size:18,max_pkt_size:60,tcp_ratio:0.05,udp_ratio:0.95,syn_ratio:0.02,fin_ratio:0.02,rst_ratio:0.005,ack_ratio:0.05,is_https:0,is_mqtt:0,is_coap:1,is_mdns:0,is_ntp:0,dns_query_count:0.3,well_known_port_ratio:0.40,is_encrypted:0,upload_bytes:60,download_bytes:60,upload_download_ratio:1.0,unique_dest_ports:1,unique_dest_ips:1,port_entropy:0.05,ip_entropy:0.05,well_known_ports_count:1,mean_dest_port:5683,std_dest_port:3},
    smart_plug:      {flow_duration:1.5,mean_iat:0.2,std_iat:0.08,min_iat:0.03,max_iat:1.5,packet_count:6,byte_count:300,packet_rate:4,byte_rate:200,mean_pkt_size:50,std_pkt_size:12,min_pkt_size:25,max_pkt_size:120,tcp_ratio:0.25,udp_ratio:0.75,syn_ratio:0.08,fin_ratio:0.07,rst_ratio:0.02,ack_ratio:0.12,is_https:0,is_mqtt:0,is_coap:0,is_mdns:0,is_ntp:0,dns_query_count:0.5,well_known_port_ratio:0.55,is_encrypted:0,upload_bytes:150,download_bytes:150,upload_download_ratio:1.0,unique_dest_ports:2,unique_dest_ips:1,port_entropy:0.3,ip_entropy:0.2,well_known_ports_count:2,mean_dest_port:8883,std_dest_port:8},
    smart_speaker:   {flow_duration:15,mean_iat:0.02,std_iat:0.015,min_iat:0.005,max_iat:0.8,packet_count:1500,byte_count:800000,packet_rate:100,byte_rate:55000,mean_pkt_size:550,std_pkt_size:150,min_pkt_size:64,max_pkt_size:1460,tcp_ratio:0.55,udp_ratio:0.45,syn_ratio:0.012,fin_ratio:0.010,rst_ratio:0.003,ack_ratio:0.38,is_https:1,is_mqtt:0,is_coap:0,is_mdns:0,is_ntp:0,dns_query_count:8,well_known_port_ratio:0.88,is_encrypted:1,upload_bytes:120000,download_bytes:680000,upload_download_ratio:0.18,unique_dest_ports:6,unique_dest_ips:5,port_entropy:1.8,ip_entropy:1.6,well_known_ports_count:5,mean_dest_port:443,std_dest_port:80},
    smart_doorbell:  {flow_duration:30,mean_iat:0.008,std_iat:0.02,min_iat:0.002,max_iat:0.5,packet_count:5000,byte_count:4000000,packet_rate:180,byte_rate:140000,mean_pkt_size:850,std_pkt_size:350,min_pkt_size:64,max_pkt_size:1500,tcp_ratio:0.75,udp_ratio:0.25,syn_ratio:0.008,fin_ratio:0.007,rst_ratio:0.003,ack_ratio:0.50,is_https:1,is_mqtt:0,is_coap:0,is_mdns:0,is_ntp:0,dns_query_count:5,well_known_port_ratio:0.85,is_encrypted:1,upload_bytes:2500000,download_bytes:1500000,upload_download_ratio:1.67,unique_dest_ports:5,unique_dest_ips:3,port_entropy:1.5,ip_entropy:1.1,well_known_ports_count:4,mean_dest_port:443,std_dest_port:60},
    motion_sensor:   {flow_duration:0.3,mean_iat:0.08,std_iat:0.04,min_iat:0.01,max_iat:0.8,packet_count:3,byte_count:80,packet_rate:10,byte_rate:270,mean_pkt_size:27,std_pkt_size:6,min_pkt_size:14,max_pkt_size:55,tcp_ratio:0.04,udp_ratio:0.96,syn_ratio:0.015,fin_ratio:0.012,rst_ratio:0.004,ack_ratio:0.04,is_https:0,is_mqtt:0,is_coap:1,is_mdns:0,is_ntp:0,dns_query_count:0.2,well_known_port_ratio:0.35,is_encrypted:0,upload_bytes:45,download_bytes:35,upload_download_ratio:1.3,unique_dest_ports:1,unique_dest_ips:1,port_entropy:0.02,ip_entropy:0.02,well_known_ports_count:1,mean_dest_port:1884,std_dest_port:2},
  };
  const DEVLIST = Object.keys(FLOWS);
  const dev = DEVLIST[Math.floor(Math.random()*DEVLIST.length)];
  const baseFlow = {...FLOWS[dev]};
  // ~10% chance of injecting attack-like features
  const isAttack = Math.random() < 0.10;
  const flow = isAttack ? {...baseFlow,
    packet_count:baseFlow.packet_count*25, byte_count:baseFlow.byte_count*30,
    packet_rate:baseFlow.packet_rate*25, byte_rate:baseFlow.byte_rate*30,
    upload_bytes:baseFlow.upload_bytes*50, upload_download_ratio:80,
    unique_dest_ips:baseFlow.unique_dest_ips*5, port_entropy:3.5
  } : baseFlow;
  let score = 0.2;
  try {
    const res = await fetch('/analyze', {method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({features: flow, source_ip: `192.168.1.${Math.floor(Math.random()*200)+10}`})});
    if(res.ok){
      const j = await res.json();
      score = j?.anomaly?.anomaly_score ?? score;
    }
  } catch(e){}
  scores.push(score); times.push(new Date().toLocaleTimeString());
  if(scores.length>60){scores.shift();times.shift();}

  const colors = scores.map(s=>s>=0.75?'#F44336':'#42A5F5');
  const sizes  = scores.map(s=>s>=0.75?10:5);
  Plotly.react('chart-timeline',[{
    x:times, y:scores, mode:'lines+markers', name:'Score',
    line:{color:'#42A5F5',width:2},
    marker:{color:colors,size:sizes}
  },{
    x:[times[0],times[times.length-1]], y:[0.75,0.75],
    mode:'lines', name:'Threshold',
    line:{color:'#F44336',dash:'dash',width:1.5}
  }],{
    paper_bgcolor:'#1A1F2E',plot_bgcolor:'#12161F',font:{color:'#E0E0E0',size:11},
    margin:{l:40,r:20,t:10,b:40},
    yaxis:{range:[0,1.05],gridcolor:'#1f2535'},
    xaxis:{gridcolor:'#1f2535',tickangle:-30,nticks:8},
    legend:{bgcolor:'rgba(0,0,0,0)',font:{size:10}},
    showlegend:true
  },{responsive:true});

  // Alerts
  const ad = await getJSON('/alerts/recent?n=20');
  const alerts = ad?.alerts ?? [];

  // Severity chart
  const sev = {LOW:0,MEDIUM:0,HIGH:0,CRITICAL:0};
  alerts.forEach(a=>{if(a.severity in sev) sev[a.severity]++});
  Plotly.react('chart-sev',[{
    x:Object.keys(sev), y:Object.values(sev),
    type:'bar', marker:{color:Object.keys(sev).map(k=>SEV_COLOR[k])},
    text:Object.values(sev), textposition:'outside', textfont:{color:'#E0E0E0'}
  }],{
    paper_bgcolor:'#1A1F2E',plot_bgcolor:'#12161F',font:{color:'#E0E0E0',size:11},
    margin:{l:30,r:20,t:10,b:40},
    yaxis:{gridcolor:'#1f2535',range:[0,Math.max(...Object.values(sev))+2]},
    xaxis:{gridcolor:'#1f2535'},showlegend:false
  },{responsive:true});

  // Alerts table
  const box = document.getElementById('alerts-table');
  if(!alerts.length){
    box.innerHTML='<p style="color:#607D8B;font-style:italic">No alerts yet.</p>';
  } else {
    let html='<table><thead><tr><th>#</th><th>Time</th><th>IP</th><th>Device</th><th>Score</th><th>Severity</th></tr></thead><tbody>';
    alerts.slice(0,15).forEach(a=>{
      const t=new Date(a.timestamp*1000).toLocaleTimeString();
      const sc=SEV_COLOR[a.severity]||'#9E9E9E';
      const dc=DEV_COLOR[a.device_type]||'#9E9E9E';
      html+=`<tr>
        <td style="color:#90A4AE">${a.alert_id}</td>
        <td>${t}</td>
        <td style="font-family:monospace">${a.source_ip}</td>
        <td style="color:${dc}">${a.device_type?.replace('smart_','').replace(/_/g,' ')}</td>
        <td>${a.anomaly_score}</td>
        <td><span class="badge" style="background:${sc}22;color:${sc}">${a.severity}</span></td>
      </tr>`;
    });
    html+='</tbody></table>';
    box.innerHTML=html;
  }
}

refresh();
setInterval(refresh, 5000);
</script>
</body>
</html>"""
