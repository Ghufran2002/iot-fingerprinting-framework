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
from fastapi.responses import HTMLResponse, RedirectResponse
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
    effective_device = device_type if device_type != "unknown" else "smart_camera"
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
    alert_mgr.process(source_ip, device_type, score)

    return {
        "fingerprint": {
            "device_type": device_type,
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


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/dashboard/")


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


# ── Mount Dash dashboard at /dashboard ──────────────────────────────────────
try:
    from starlette.middleware.wsgi import WSGIMiddleware
    from src.dashboard.app import app as _dash_app
    app.mount("/dashboard", WSGIMiddleware(_dash_app.server))
    logger.info("Dash dashboard mounted at /dashboard")
except Exception as _e:
    logger.warning(f"Dashboard mount skipped: {_e}")
