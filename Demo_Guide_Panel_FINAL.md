# Panel Demo Guide — Step by Step
**IoT Device Fingerprinting & Anomaly Detection Framework**
Md Ghufran Alam | NDU202400038 | NIELIT Srinagar

**Base URL:** `https://mdghufran-iot-fingerprinting.hf.space`

---

## BEFORE THE PRESENTATION — Setup Checklist

- [ ] Open Chrome or Edge browser
- [ ] Keep this URL ready: `https://mdghufran-iot-fingerprinting.hf.space`
- [ ] Keep `/docs` tab open: `https://mdghufran-iot-fingerprinting.hf.space/docs`
- [ ] Keep `/status` tab open: `https://mdghufran-iot-fingerprinting.hf.space/status`
- [ ] Internet connection confirmed
- [ ] Projector/screen connected and mirroring

---

## DEMO SEQUENCE — 5 Steps

---

### STEP 1 — Show the Live System is Running
**What to say:** *"The system is live right now. Let me show you the status page."*

**Action:** Open → `https://mdghufran-iot-fingerprinting.hf.space/status`

**What panel will see:**
- System: ONLINE (green)
- Models Loaded: Random Forest + IForest + OC-SVM
- SHAP Explainer: Ready
- Uptime counter running
- Request count

**What to say:** *"This page shows the system is healthy, all 3 ML models are loaded, and SHAP is ready. The uptime counter is running live."*

---

### STEP 2 — Show the API Documentation
**What to say:** *"This is the API documentation — all 8 endpoints are available and testable directly from the browser."*

**Action:** Open → `https://mdghufran-iot-fingerprinting.hf.space/docs`

**What panel will see:**
- Dark-themed Swagger UI
- Endpoints grouped: System, Fingerprinting, Anomaly Detection, Combined Analysis, Explainability, Alerts

**What to say:** *"We have 8 REST API endpoints. I will demonstrate 4 of them live right now."*

---

### STEP 3 — Demo 1: Device Fingerprinting (Smart Camera)
**What to say:** *"First, I will fingerprint a smart camera from its network traffic alone."*

**Action:**
1. Click **POST /fingerprint** → Click **"Try it out"**
2. Replace the request body with this:

```json
{
  "flow_duration": 10.0,
  "mean_iat": 0.0025,
  "std_iat": 0.001,
  "min_iat": 0.001,
  "max_iat": 0.01,
  "packet_count": 4000.0,
  "byte_count": 28000000.0,
  "packet_rate": 400.0,
  "byte_rate": 2800000.0,
  "mean_pkt_size": 1400.0,
  "std_pkt_size": 80.0,
  "min_pkt_size": 64.0,
  "max_pkt_size": 1500.0,
  "tcp_ratio": 0.95,
  "udp_ratio": 0.05,
  "syn_ratio": 0.01,
  "fin_ratio": 0.008,
  "rst_ratio": 0.002,
  "ack_ratio": 0.65,
  "is_https": 1.0,
  "is_mqtt": 0.0,
  "is_coap": 0.0,
  "is_mdns": 0.0,
  "is_ntp": 0.0,
  "dns_query_count": 3.0,
  "well_known_port_ratio": 0.95,
  "is_encrypted": 1.0,
  "upload_bytes": 25000000.0,
  "download_bytes": 3000000.0,
  "upload_download_ratio": 8.0,
  "unique_dest_ports": 2.0,
  "unique_dest_ips": 3.0,
  "port_entropy": 0.5,
  "ip_entropy": 0.8,
  "well_known_ports_count": 2.0,
  "mean_dest_port": 443.0,
  "std_dest_port": 10.0
}
```

3. Click **Execute**

**Expected Response:**
```json
{
  "device_type": "smart_camera",
  "confidence": 0.99,
  "is_known": true,
  "model_used": "random_forest"
}
```

**What to say:** *"The model identified this as a smart camera with 99% confidence — just from network traffic. HTTPS on port 443, high packet rate, large packet size, high upload ratio — these are the camera's fingerprint."*

---

### STEP 4 — Demo 2: Anomaly Detection (Normal vs Attack)

#### STEP 4A — Normal Traffic (Score should be LOW)
**What to say:** *"Now let me check if this camera is behaving normally."*

**Action:**
1. Click **POST /anomaly/score** → Click **"Try it out"**
2. Use this body:

```json
{
  "features": {
    "flow_duration": 10.0,
    "mean_iat": 0.0025,
    "std_iat": 0.001,
    "min_iat": 0.001,
    "max_iat": 0.01,
    "packet_count": 4000.0,
    "byte_count": 28000000.0,
    "packet_rate": 400.0,
    "byte_rate": 2800000.0,
    "mean_pkt_size": 1400.0,
    "std_pkt_size": 80.0,
    "min_pkt_size": 64.0,
    "max_pkt_size": 1500.0,
    "tcp_ratio": 0.95,
    "udp_ratio": 0.05,
    "syn_ratio": 0.01,
    "fin_ratio": 0.008,
    "rst_ratio": 0.002,
    "ack_ratio": 0.65,
    "is_https": 1.0,
    "is_mqtt": 0.0,
    "is_coap": 0.0,
    "is_mdns": 0.0,
    "is_ntp": 0.0,
    "dns_query_count": 3.0,
    "well_known_port_ratio": 0.95,
    "is_encrypted": 1.0,
    "upload_bytes": 25000000.0,
    "download_bytes": 3000000.0,
    "upload_download_ratio": 8.0,
    "unique_dest_ports": 2.0,
    "unique_dest_ips": 3.0,
    "port_entropy": 0.5,
    "ip_entropy": 0.8,
    "well_known_ports_count": 2.0,
    "mean_dest_port": 443.0,
    "std_dest_port": 10.0
  },
  "device_type": "smart_camera",
  "source_ip": "192.168.1.45"
}
```

3. Click **Execute**

**Expected Response:**
```json
{
  "device_type": "smart_camera",
  "anomaly_score": 0.0,
  "is_anomalous": false,
  "severity": null,
  "threshold": 0.75
}
```

**What to say:** *"Score is 0.0 — perfectly normal. No alert. This is what the camera looks like during regular operation."*

---

#### STEP 4B — Attack Traffic / Data Exfiltration (Score should be HIGH)
**What to say:** *"Now I will simulate a Mirai data exfiltration attack — the same camera suddenly uploading gigabytes of data."*

**Action:**
1. Stay on **POST /anomaly/score** → **"Try it out"**
2. Replace body with this (notice: upload_bytes massive, ratio 120):

```json
{
  "features": {
    "flow_duration": 10.0,
    "mean_iat": 0.0001,
    "std_iat": 0.00005,
    "min_iat": 0.00001,
    "max_iat": 0.001,
    "packet_count": 150000.0,
    "byte_count": 1680000000.0,
    "packet_rate": 15000.0,
    "byte_rate": 168000000.0,
    "mean_pkt_size": 1500.0,
    "std_pkt_size": 10.0,
    "min_pkt_size": 1400.0,
    "max_pkt_size": 1500.0,
    "tcp_ratio": 0.98,
    "udp_ratio": 0.02,
    "syn_ratio": 0.001,
    "fin_ratio": 0.001,
    "rst_ratio": 0.0,
    "ack_ratio": 0.9,
    "is_https": 1.0,
    "is_mqtt": 0.0,
    "is_coap": 0.0,
    "is_mdns": 0.0,
    "is_ntp": 0.0,
    "dns_query_count": 1.0,
    "well_known_port_ratio": 0.99,
    "is_encrypted": 1.0,
    "upload_bytes": 1680000000.0,
    "download_bytes": 14000000.0,
    "upload_download_ratio": 120.0,
    "unique_dest_ports": 1.0,
    "unique_dest_ips": 1.0,
    "port_entropy": 0.1,
    "ip_entropy": 0.1,
    "well_known_ports_count": 1.0,
    "mean_dest_port": 443.0,
    "std_dest_port": 0.0
  },
  "device_type": "smart_camera",
  "source_ip": "192.168.1.45"
}
```

3. Click **Execute**

**Expected Response:**
```json
{
  "device_type": "smart_camera",
  "anomaly_score": 0.806,
  "is_anomalous": true,
  "severity": "HIGH",
  "threshold": 0.75
}
```

**What to say:** *"Score jumped to 0.806 — HIGH severity alert. The upload-to-download ratio went from 8 to 120. The camera is uploading 1.68 gigabytes — this is classic Mirai data exfiltration behavior. The system caught it immediately."*

---

### STEP 5 — Demo 3: SHAP Explainability
**What to say:** *"Now I will show why the model made this decision — using SHAP explainability."*

**Action:**
1. Click **POST /explain** → Click **"Try it out"**
2. Use this body (same attack traffic):

```json
{
  "flow_duration": 10.0,
  "mean_iat": 0.0001,
  "std_iat": 0.00005,
  "min_iat": 0.00001,
  "max_iat": 0.001,
  "packet_count": 150000.0,
  "byte_count": 1680000000.0,
  "packet_rate": 15000.0,
  "byte_rate": 168000000.0,
  "mean_pkt_size": 1500.0,
  "std_pkt_size": 10.0,
  "min_pkt_size": 1400.0,
  "max_pkt_size": 1500.0,
  "tcp_ratio": 0.98,
  "udp_ratio": 0.02,
  "syn_ratio": 0.001,
  "fin_ratio": 0.001,
  "rst_ratio": 0.0,
  "ack_ratio": 0.9,
  "is_https": 1.0,
  "is_mqtt": 0.0,
  "is_coap": 0.0,
  "is_mdns": 0.0,
  "is_ntp": 0.0,
  "dns_query_count": 1.0,
  "well_known_port_ratio": 0.99,
  "is_encrypted": 1.0,
  "upload_bytes": 1680000000.0,
  "download_bytes": 14000000.0,
  "upload_download_ratio": 120.0,
  "unique_dest_ports": 1.0,
  "unique_dest_ips": 1.0,
  "port_entropy": 0.1,
  "ip_entropy": 0.1,
  "well_known_ports_count": 1.0,
  "mean_dest_port": 443.0,
  "std_dest_port": 0.0
}
```

3. Click **Execute**

**Expected Response (top features):**
```json
{
  "device_type": "smart_camera",
  "confidence": 0.99,
  "explanation": [
    { "feature": "upload_download_ratio", "direction": "toward", "abs_impact": 0.18 },
    { "feature": "packet_rate",           "direction": "toward", "abs_impact": 0.15 },
    { "feature": "byte_rate",             "direction": "toward", "abs_impact": 0.13 },
    { "feature": "upload_bytes",          "direction": "toward", "abs_impact": 0.11 },
    ...
  ]
}
```

**What to say:** *"SHAP tells us exactly which features drove the decision. upload_download_ratio had the highest impact — 120 is 15 times higher than normal. packet_rate is 15,000 per second — normally it is 400. This is not a black-box — the model can explain every single prediction."*

---

### BONUS — Show Live Dashboard (if time allows)
**Action:** Open → `https://mdghufran-iot-fingerprinting.hf.space/dashboard/`

**What panel will see:**
- Live anomaly timeline chart
- Severity distribution chart
- Recent alerts table
- SHAP feature importance panel

**What to say:** *"This is the live monitoring dashboard built with Plotly Dash. All the API calls we just made are reflected here as alerts in real time."*

---

## IF INTERNET FAILS — Backup Plan

Run locally:
```bash
python run.py
```
Then open: `http://localhost:7860/docs`

Use the same JSON payloads above — everything works identically on local.

---

## QUICK REFERENCE — Key Numbers to Remember

| Metric | Value |
|--------|-------|
| Fingerprinting Accuracy | 100% |
| Best Anomaly AUC | 0.8773 (smart_doorbell) |
| API Latency | ~40 ms |
| Number of Devices | 8 |
| Number of Features | 37 |
| Normal Traffic Score | 0.0 |
| Attack Traffic Score | 0.806 (HIGH) |
| Alert Threshold | 0.75 |
| SHAP Response Time | < 30 ms |

---

## PANEL QUESTIONS DURING DEMO — Quick Answers

**"Can we test it ourselves?"**
Yes — show them the `/docs` page, they can type any values and click Execute.

**"What if the device is unknown?"**
Change `is_mqtt`, `is_coap`, `is_https` all to 0.5 — confidence will drop below 60% and it returns `"device_type": "unknown"`.

**"What is the threshold based on?"**
Trained on real N-BaIoT data — 0.75 gives zero false positives on normal traffic while catching all tested attack patterns.

**"How fast is it?"**
Ask them to watch the response time shown at the bottom of the Swagger UI after clicking Execute — it will show approximately 40ms.

---
*Demo guide for panel defense — NIELIT Srinagar, May 2026*
