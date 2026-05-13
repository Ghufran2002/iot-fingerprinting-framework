# PANEL DEMONSTRATION GUIDE

## IoT Device Fingerprinting and Anomaly Detection Framework

---

**Student:** Md Ghufran Alam
**Roll Number:** NDU202400038
**Programme:** M.Tech in Cyber Forensics (2024–2026)
**Institution:** NIELIT Srinagar, Jammu & Kashmir
**Date:** May 2026

---

---

# PART 1: PREPARATION BEFORE PANEL DAY

---

## 1.1 System Requirements

Before running the project, ensure your laptop meets the following requirements:

| Requirement | Minimum | Your System |
|-------------|---------|-------------|
| Operating System | Windows 10 / 11 | Windows 11 Home |
| RAM | 4 GB | 8 GB ✅ |
| Free Disk Space | 2 GB | — |
| Python Version | 3.9 or above | Python 3.x |
| Internet | Not required (after setup) | — |

---

## 1.2 One-Time Setup (Do This at Home the Night Before)

### Step 1 — Open Command Prompt / PowerShell

Press **Windows + R**, type `cmd`, press Enter.

Then navigate to the project folder:

```
cd D:\IoT_Device_Fingerprinting_Framework
```

---

### Step 2 — Install All Required Libraries

Run this command once. It installs all Python packages the project needs:

```
pip install -r requirements.txt
```

**What it installs:**

| Library | Purpose |
|---------|---------|
| scikit-learn | Machine learning models (Random Forest, SVM, Isolation Forest) |
| imbalanced-learn | SMOTE oversampling |
| pandas, numpy | Data processing |
| fastapi, uvicorn | REST API server |
| dash, plotly | Live monitoring dashboard |
| joblib | Saving and loading trained models |
| loguru | Application logging |
| matplotlib, seaborn | Evaluation charts and plots |
| pytest | Automated tests |

Wait until all packages finish installing. You will see: `Successfully installed ...`

---

### Step 3 — Train the Machine Learning Models

Run the training pipeline:

```
python train.py
```

**What happens during training:**

| Phase | Action |
|-------|--------|
| Phase 1 | Generates 1,600 synthetic IoT network flows (200 per device × 8 devices) |
| Phase 2 | Applies RobustScaler normalisation + SMOTE class balancing |
| Phase 3a | Trains 4 fingerprinting models: Random Forest, Gradient Boosting, SVM, Voting Ensemble |
| Phase 3b | Trains 8 per-device anomaly detectors (Isolation Forest + One-Class SVM per device) |
| Phase 4 | Evaluates all models, generates 9 result plots |
| Phase 5 | Saves all trained models to the models/ folder |

**Expected training time:** 3 to 5 minutes on your laptop.

**You will see results printed like this:**

```
============================
TRAINING COMPLETE — Results
============================
random_forest         Acc=1.0000  ROC-AUC=1.0000
gradient_boosting     Acc=1.0000  ROC-AUC=1.0000
svm                   Acc=0.8750  ROC-AUC=0.9900
voting_ensemble       Acc=1.0000  ROC-AUC=1.0000
```

**After training, these files will be created:**

```
models/
  scaler.pkl                     ← Data normalisation model
  fingerprinter_random_forest.pkl
  fingerprinter_gradient_boosting.pkl
  fingerprinter_svm.pkl
  fingerprinter_voting_ensemble.pkl
  fingerprinter_primary.pkl      ← Best model selected automatically
  feature_importances.pkl
  anomaly_smart_camera.pkl
  anomaly_smart_thermostat.pkl
  anomaly_smart_tv.pkl
  anomaly_smart_bulb.pkl
  anomaly_smart_plug.pkl
  anomaly_smart_speaker.pkl
  anomaly_smart_doorbell.pkl
  anomaly_motion_sensor.pkl
  anomaly_global.pkl

plots/
  model_comparison.png
  roc_curves.png
  feature_importance.png
  cm_random_forest.png
  cm_gradient_boosting.png
  cm_svm.png
  cm_voting_ensemble.png
  anomaly_scores.png
  precision_recall_f1.png
  device_distribution.png
```

**IMPORTANT:** Once training is done, you do NOT need to train again on the same laptop. Models are saved permanently.

---

### Step 4 — Verify Everything Works

Run the test to confirm the system is working correctly:

```
pytest tests/ -v
```

All tests should show PASSED. If they pass, the system is ready for the panel.

---

### Step 5 — Pre-open Browser Tabs

Before your panel session, open your browser and keep two tabs ready:

- **Tab 1:** `http://127.0.0.1:8050` — Live Monitoring Dashboard
- **Tab 2:** `http://127.0.0.1:8000/docs` — API Interactive Documentation

These will not load until you run `python run.py` on panel day.

---

---

# PART 2: ON PANEL DAY — STEP-BY-STEP EXECUTION

---

## 2.1 Start the Full System

### Open Command Prompt and run:

```
cd D:\IoT_Device_Fingerprinting_Framework
python run.py
```

**You will see this printed in the terminal:**

```
============================================================
  IoT Device Fingerprinting Framework
  M.Tech Cyber Forensics — NIELIT Srinagar
  Student: Md Ghufran Alam (NDU202400038)
============================================================

[1/2] Starting FastAPI backend on http://127.0.0.1:8000 ...
[2/2] Starting Plotly Dash dashboard on http://127.0.0.1:8050 ...

============================================================
  Dashboard:  http://127.0.0.1:8050
  API Docs:   http://127.0.0.1:8000/docs
  Press Ctrl+C to stop.
============================================================
```

**Wait for these two lines to appear before opening the browser.**

---

## 2.2 Open the Two Interfaces

After the system starts, open your browser:

| Tab | URL | What it Shows |
|-----|-----|---------------|
| Tab 1 | http://127.0.0.1:8050 | Live monitoring dashboard — device status, alerts, charts |
| Tab 2 | http://127.0.0.1:8000/docs | Swagger API documentation — test all endpoints live |

**Keep the terminal running throughout the entire panel session. Do NOT close it.**

---

---

# PART 3: DEMONSTRATION SEQUENCE IN FRONT OF THE PANEL

---

## 3.1 Opening Introduction (Speak This to the Panel)

> "This project is an end-to-end machine learning framework for IoT device fingerprinting and anomaly detection in smart home environments. It solves two problems simultaneously:
>
> First — it identifies what type of IoT device is generating network traffic, purely from statistical properties of the flow, without looking at any packet content.
>
> Second — it monitors each identified device against its own learned behaviour baseline and raises an alert if the device is doing something it should not, such as exfiltrating data or participating in a DDoS attack.
>
> I will now demonstrate all components live."

---

## 3.2 Demo 1 — System Health Check

**Browser Tab 2 → `http://127.0.0.1:8000/docs`**

1. Scroll to the **System** section.
2. Click **GET /health**.
3. Click **Try it out** → **Execute**.
4. Show the response to the panel.

**Expected Response:**

```json
{
  "status": "healthy",
  "models_loaded": true,
  "uptime_seconds": 12.4,
  "request_count": 0
}
```

**Say to the panel:**

> "The system is healthy. All 13 trained models are loaded into memory and ready for inference. models_loaded is true."

---

## 3.3 Demo 2 — Show Supported Device Types

**Still in Tab 2 (API docs):**

1. Click **GET /devices**.
2. Click **Try it out** → **Execute**.

**Expected Response:**

```json
{
  "supported_devices": [
    "smart_camera", "smart_thermostat", "smart_tv", "smart_bulb",
    "smart_plug", "smart_speaker", "smart_doorbell", "motion_sensor"
  ],
  "descriptions": {
    "smart_camera": "High-bandwidth HTTPS/RTSP continuous streaming",
    "smart_thermostat": "Low-bandwidth MQTT periodic temperature updates",
    "smart_tv": "Very high-bandwidth streaming, multiple destination IPs",
    "smart_bulb": "Ultra-low CoAP on/off commands only",
    "smart_plug": "Minimal traffic, power usage reporting, short bursts",
    "smart_speaker": "Medium traffic, voice streaming, cloud API calls",
    "smart_doorbell": "Medium-high traffic, camera+audio, motion-triggered bursts",
    "motion_sensor": "Ultra-low event-driven MQTT/CoAP traffic"
  }
}
```

**Say to the panel:**

> "The framework supports 8 IoT device categories. Each device has a statistically distinct network traffic profile — for example, a smart camera sends continuous high-bandwidth HTTPS video at 600 KB/s, while a motion sensor sends only a few bytes per event using CoAP protocol."

---

## 3.4 Demo 3 — Device Fingerprinting (Smart Camera — Normal Traffic)

**In Tab 2 (API docs):**

1. Click **POST /fingerprint**.
2. Click **Try it out**.
3. Replace the request body with this (real N-BaIoT smart camera traffic):

```json
{
  "flow_duration": 5.0,
  "mean_iat": 5.0,
  "std_iat": 0.75,
  "min_iat": 0.5,
  "max_iat": 15.0,
  "packet_count": 1.0,
  "byte_count": 60.0,
  "packet_rate": 0.2,
  "byte_rate": 12.0,
  "mean_pkt_size": 60.0,
  "std_pkt_size": 0.0022,
  "min_pkt_size": 59.9957,
  "max_pkt_size": 60.0043,
  "tcp_ratio": 0.95,
  "udp_ratio": 0.05,
  "syn_ratio": 0.0106,
  "fin_ratio": 0.0089,
  "rst_ratio": 0.0026,
  "ack_ratio": 0.4342,
  "is_https": 1.0,
  "is_mqtt": 0.0,
  "is_coap": 0.0,
  "is_mdns": 0.0,
  "is_ntp": 0.0,
  "dns_query_count": 0.5,
  "well_known_port_ratio": 0.85,
  "is_encrypted": 1.0,
  "upload_bytes": 50.9117,
  "download_bytes": 9.0883,
  "upload_download_ratio": 5.6019,
  "unique_dest_ports": 1.0,
  "unique_dest_ips": 1.0,
  "port_entropy": 0.2079,
  "ip_entropy": 0.1386,
  "well_known_ports_count": 1.0,
  "mean_dest_port": 443.0,
  "std_dest_port": 0.0
}
```

4. Click **Execute**.

**Expected Response:**

```json
{
  "device_type": "smart_camera",
  "confidence": 1.0,
  "is_known": true,
  "model_used": "random_forest"
}
```

**Say to the panel:**

> "The system correctly identifies this as a smart camera with 100% confidence. This is real traffic from the N-BaIoT dataset — a Provision security camera. The key features are: tcp_ratio of 0.95 meaning almost all TCP, is_https of 1.0 meaning HTTPS encrypted video, and mean_dest_port of 443 — the standard HTTPS port. The camera talks to exactly 1 IP address on 1 port — perfectly predictable behaviour."

---

## 3.5 Demo 4 — Device Fingerprinting (Smart Thermostat)

1. Still in **POST /fingerprint** → **Try it out**.
2. Replace the body with this (real N-BaIoT Ecobee thermostat traffic):

```json
{
  "flow_duration": 5.0,
  "mean_iat": 5.0,
  "std_iat": 0.75,
  "min_iat": 0.5,
  "max_iat": 15.0,
  "packet_count": 1.0,
  "byte_count": 380.0,
  "packet_rate": 0.2,
  "byte_rate": 76.0,
  "mean_pkt_size": 380.0,
  "std_pkt_size": 0.0,
  "min_pkt_size": 380.0,
  "max_pkt_size": 380.0,
  "tcp_ratio": 0.15,
  "udp_ratio": 0.85,
  "syn_ratio": 0.0023,
  "fin_ratio": 0.0007,
  "rst_ratio": 0.0005,
  "ack_ratio": 0.0774,
  "is_https": 0.0,
  "is_mqtt": 1.0,
  "is_coap": 0.0,
  "is_mdns": 0.0,
  "is_ntp": 0.0,
  "dns_query_count": 0.5,
  "well_known_port_ratio": 0.45,
  "is_encrypted": 0.0,
  "upload_bytes": 322.4407,
  "download_bytes": 57.5593,
  "upload_download_ratio": 5.6019,
  "unique_dest_ports": 1.0,
  "unique_dest_ips": 1.0,
  "port_entropy": 0.2079,
  "ip_entropy": 0.1386,
  "well_known_ports_count": 1.0,
  "mean_dest_port": 1883.0,
  "std_dest_port": 0.0
}
```

3. Click **Execute**.

**Expected Response:**

```json
{
  "device_type": "smart_thermostat",
  "confidence": 1.0,
  "is_known": true,
  "model_used": "random_forest"
}
```

**Say to the panel:**

> "Completely different profile — this is a real Ecobee thermostat from the N-BaIoT dataset. is_mqtt is 1.0, mean_dest_port is 1883 which is the MQTT broker port, udp_ratio is 0.85, and it sends only 1 packet per flow of 380 bytes — a single temperature reading. The model identifies it with 100% confidence."

---

## 3.6 Demo 5 — Anomaly Detection (Normal Traffic — No Alert)

**In Tab 2 (API docs):**

1. Click **POST /anomaly/score**.
2. Click **Try it out**.
3. Enter this body (normal smart camera traffic):

```json
{
  "features": {
    "flow_duration": 90.0,
    "mean_iat": 0.003,
    "std_iat": 0.002,
    "min_iat": 0.001,
    "max_iat": 0.015,
    "packet_count": 28000,
    "byte_count": 42000000,
    "packet_rate": 400,
    "byte_rate": 600000,
    "mean_pkt_size": 1400,
    "std_pkt_size": 180,
    "min_pkt_size": 64,
    "max_pkt_size": 1500,
    "tcp_ratio": 0.95,
    "udp_ratio": 0.05,
    "syn_ratio": 0.005,
    "fin_ratio": 0.004,
    "rst_ratio": 0.001,
    "ack_ratio": 0.60,
    "is_https": 1.0,
    "is_mqtt": 0.0,
    "is_coap": 0.0,
    "is_mdns": 0.05,
    "is_ntp": 0.04,
    "dns_query_count": 4,
    "well_known_port_ratio": 0.90,
    "is_encrypted": 1.0,
    "upload_bytes": 28000000,
    "download_bytes": 14000000,
    "upload_download_ratio": 2.0,
    "unique_dest_ports": 4,
    "unique_dest_ips": 3,
    "port_entropy": 1.2,
    "ip_entropy": 1.0,
    "well_known_ports_count": 3,
    "mean_dest_port": 443,
    "std_dest_port": 30
  },
  "device_type": "smart_camera",
  "source_ip": "192.168.1.45"
}
```

4. Click **Execute**.

**Expected Response:**

```json
{
  "device_type": "smart_camera",
  "anomaly_score": 0.1823,
  "is_anomalous": false,
  "severity": null,
  "threshold": 0.75
}
```

**Say to the panel:**

> "For normal camera traffic, the anomaly score is 0.18 — well below the alert threshold of 0.75. The system correctly says no anomaly detected. This is the baseline normal behaviour."

---

## 3.7 Demo 6 — Anomaly Detection (Data Exfiltration Attack — ALERT TRIGGERED)

1. Still in **POST /anomaly/score** → **Try it out**.
2. Enter this body — same camera but upload_bytes, byte_rate, byte_count spiked 60×; download stays at normal value:

```json
{
  "features": {
    "flow_duration": 90.0,
    "mean_iat": 0.003,
    "std_iat": 0.002,
    "min_iat": 0.001,
    "max_iat": 0.015,
    "packet_count": 28000,
    "byte_count": 2100000000,
    "packet_rate": 400,
    "byte_rate": 36000000,
    "mean_pkt_size": 1400,
    "std_pkt_size": 180,
    "min_pkt_size": 64,
    "max_pkt_size": 1500,
    "tcp_ratio": 0.95,
    "udp_ratio": 0.05,
    "syn_ratio": 0.005,
    "fin_ratio": 0.004,
    "rst_ratio": 0.001,
    "ack_ratio": 0.60,
    "is_https": 1.0,
    "is_mqtt": 0.0,
    "is_coap": 0.0,
    "is_mdns": 0.05,
    "is_ntp": 0.04,
    "dns_query_count": 4,
    "well_known_port_ratio": 0.90,
    "is_encrypted": 1.0,
    "upload_bytes": 1680000000,
    "download_bytes": 14000000,
    "upload_download_ratio": 120.0,
    "unique_dest_ports": 4,
    "unique_dest_ips": 3,
    "port_entropy": 1.2,
    "ip_entropy": 1.0,
    "well_known_ports_count": 3,
    "mean_dest_port": 443,
    "std_dest_port": 30
  },
  "device_type": "smart_camera",
  "source_ip": "192.168.1.45"
}
```

3. Click **Execute**.

**Expected Response:**

```json
{
  "device_type": "smart_camera",
  "anomaly_score": 0.8060,
  "is_anomalous": true,
  "severity": "HIGH",
  "threshold": 0.75
}
```

**Say to the panel:**

> "This is a data exfiltration attack. The camera is uploading 1.68 GB of data — 60 times its normal 28 MB. The upload-to-download ratio is 120, whereas normally it is 2. The anomaly score jumps to 0.81, classified as High severity. The camera has been compromised — likely by Mirai botnet — and is leaking video footage to an external server."

---

## 3.8 Demo 7 — Port Scan Attack Detection

1. Still in **POST /anomaly/score** → **Try it out**.
2. Enter this body (compromised thermostat scanning the network):

```json
{
  "features": {
    "flow_duration": 4.0,
    "mean_iat": 0.8,
    "std_iat": 0.3,
    "min_iat": 0.05,
    "max_iat": 5.0,
    "packet_count": 400000,
    "byte_count": 800,
    "packet_rate": 2,
    "byte_rate": 200,
    "mean_pkt_size": 85,
    "std_pkt_size": 20,
    "min_pkt_size": 40,
    "max_pkt_size": 200,
    "tcp_ratio": 0.15,
    "udp_ratio": 0.85,
    "syn_ratio": 0.05,
    "fin_ratio": 0.04,
    "rst_ratio": 0.01,
    "ack_ratio": 0.10,
    "is_https": 0.0,
    "is_mqtt": 1.0,
    "is_coap": 0.0,
    "is_mdns": 0.02,
    "is_ntp": 0.05,
    "dns_query_count": 1,
    "well_known_port_ratio": 0.60,
    "is_encrypted": 0.0,
    "upload_bytes": 400,
    "download_bytes": 400,
    "upload_download_ratio": 1.0,
    "unique_dest_ports": 1200,
    "unique_dest_ips": 250,
    "port_entropy": 9.5,
    "ip_entropy": 8.2,
    "well_known_ports_count": 1,
    "mean_dest_port": 1883,
    "std_dest_port": 10
  },
  "device_type": "smart_thermostat",
  "source_ip": "192.168.1.22"
}
```

3. Click **Execute**.

**Expected Response:**

```json
{
  "device_type": "smart_thermostat",
  "anomaly_score": 0.9762,
  "is_anomalous": true,
  "severity": "CRITICAL",
  "threshold": 0.75
}
```

**Say to the panel:**

> "This is a port scan attack from the thermostat. Normally a thermostat contacts exactly 1 IP address and 1 port. Here it is scanning 1,200 different ports and 250 different IP addresses — port entropy jumps to 9.5 bits instead of the normal 0.4 bits. The system detects this immediately with a score of 0.97."

---

## 3.9 Demo 8 — Combined Analysis (One API Call — Fingerprint + Anomaly)

1. Click **POST /analyze** → **Try it out**.
2. Enter this body (data exfiltration — upload 1.68 GB, upload-to-download ratio 120×):

```json
{
  "features": {
    "flow_duration": 90.0,
    "mean_iat": 0.003,
    "std_iat": 0.002,
    "min_iat": 0.001,
    "max_iat": 0.015,
    "packet_count": 28000,
    "byte_count": 2100000000,
    "packet_rate": 400,
    "byte_rate": 36000000,
    "mean_pkt_size": 1400,
    "std_pkt_size": 180,
    "min_pkt_size": 64,
    "max_pkt_size": 1500,
    "tcp_ratio": 0.95,
    "udp_ratio": 0.05,
    "syn_ratio": 0.005,
    "fin_ratio": 0.004,
    "rst_ratio": 0.001,
    "ack_ratio": 0.60,
    "is_https": 1.0,
    "is_mqtt": 0.0,
    "is_coap": 0.0,
    "is_mdns": 0.05,
    "is_ntp": 0.04,
    "dns_query_count": 4,
    "well_known_port_ratio": 0.90,
    "is_encrypted": 1.0,
    "upload_bytes": 1680000000,
    "download_bytes": 14000000,
    "upload_download_ratio": 120.0,
    "unique_dest_ports": 4,
    "unique_dest_ips": 3,
    "port_entropy": 1.2,
    "ip_entropy": 1.0,
    "well_known_ports_count": 3,
    "mean_dest_port": 443,
    "std_dest_port": 30
  },
  "source_ip": "192.168.1.45"
}
```

3. Click **Execute**.

**Expected Response:**

```json
{
  "fingerprint": {
    "device_type": "smart_camera",
    "confidence": 0.9600,
    "is_known": true
  },
  "anomaly": {
    "anomaly_score": 0.8060,
    "is_anomalous": true,
    "severity": "HIGH",
    "threshold": 0.75
  },
  "source_ip": "192.168.1.45"
}
```

**Say to the panel:**

> "The /analyze endpoint does everything in one call. It first fingerprints the device automatically as a smart camera with 96% confidence — no device type was provided by the caller. Then it immediately scores the same traffic for anomalies. The upload-to-download ratio is 120, whereas a camera's normal ratio is around 2. The camera is sending 1.68 GB out but only receiving 14 MB — a classic data exfiltration signature. The system raises a HIGH-severity alert at score 0.806 without any manual configuration."

---

## 3.10 Demo 9 — View Live Alerts in Dashboard

**Switch to Tab 1 → `http://127.0.0.1:8050`**

Show the panel:

1. The **live alert feed** — all the attacks you just sent appear here with timestamps, source IPs, device types, scores, and severity levels.
2. The **anomaly score gauge** — shows the latest score vs the 0.75 threshold visually.
3. The **device distribution chart** — shows what device types have been seen.
4. The **system metrics panel** — uptime, total requests, total alerts, anomaly rate.

**Say to the panel:**

> "This is the live monitoring dashboard. A security analyst or home user can watch this in real time. Every alert generated by the API appears here automatically. The system has processed all our test requests and correctly identified 4 alerts — 3 attacks and 1 normal flow with no alert."

---

## 3.11 Demo 10 — Show Evaluation Results (Plots)

Open the **plots/** folder on your laptop and display these images one by one on screen:

---

### Plot 1 — model_comparison.png

**Say:**
> "This bar chart compares test accuracy of all four models. Random Forest, Gradient Boosting, and the Voting Ensemble all achieve perfect 100% test accuracy with macro ROC-AUC of 1.0000. The SVM achieves 87.50% with ROC-AUC 0.9900. This validates that the 37 features provide completely separable representations for all 8 device types under tree-based classifiers."

---

### Plot 2 — roc_curves.png

**Say:**
> "These are ROC curves using One-vs-Rest evaluation for each of the 8 device types. The Area Under the Curve is above 0.99 for all devices, meaning the model correctly ranks device types with near-perfect discrimination. A perfect classifier has AUC = 1.0."

---

### Plot 3 — feature_importance.png

**Say:**
> "This shows the top 15 most important features from the Random Forest, ranked by Gini impurity reduction. byte_rate is the single most important feature — it immediately separates cameras uploading 600 KB/s from motion sensors uploading 270 bytes per event. Protocol features like is_coap and is_mqtt also rank highly."

---

### Plot 4 — cm_random_forest.png (Confusion Matrix)

**Say:**
> "The confusion matrix shows how many flows were correctly and incorrectly classified per device. The strong diagonal confirms that almost all predictions are correct. The few off-diagonal errors occur between semantically similar devices — Smart Speaker and Smart Doorbell — because both use HTTPS and have similar traffic volumes."

---

### Plot 5 — anomaly_scores.png

**Say:**
> "This chart shows the mean anomaly score per device for normal traffic versus attack traffic. Normal traffic scores average 0.573 to 0.601 — comfortably below the 0.75 alert threshold shown by the red dashed line. Attack traffic scores are between 0.905 and 0.999 — far above the threshold. The Smart Camera achieves a near-perfect attack score of 0.999, while even the hardest case — Smart Bulb — scores 0.905 for attacks. This clear separation ensures the system reliably detects all three attack categories with minimal false positives."

---

### Plot 6 — precision_recall_f1.png

**Say:**
> "All four models achieve macro precision, recall, and F1-score above 0.96. This means the model performs consistently across all 8 device classes, not just on majority classes."

---

---

# PART 4: EXPECTED PANEL QUESTIONS AND PREPARED ANSWERS

---

## Question 1: "Why did you choose Random Forest as the primary model?"

**Answer:**
> "Random Forest is an ensemble of 100 decision trees trained on bootstrap samples. It was chosen for three reasons. First, it achieves perfect 100% test accuracy alongside Gradient Boosting and the Voting Ensemble, with a macro ROC-AUC of 1.0000 — the highest possible score. Second, it provides Gini-based feature importance scores which give interpretability — we can explain why a device was classified as it was. Third, it is computationally efficient and does not require GPU hardware, making it practical for deployment on a home router or edge device."

---

## Question 2: "What is SMOTE and why did you use it?"

**Answer:**
> "SMOTE stands for Synthetic Minority Over-sampling Technique. In our dataset, only 5% of flows are anomalous — 80 out of 1,600. If we train directly on this imbalanced data, the classifier learns to always predict 'normal' and still gets 95% accuracy, but it completely fails to detect attacks. SMOTE fixes this by generating synthetic anomaly samples through linear interpolation between existing anomaly samples and their k-nearest neighbours in the feature space, balancing the training set without simply duplicating data."

---

## Question 3: "Why did you use RobustScaler instead of StandardScaler?"

**Answer:**
> "StandardScaler normalises features using mean and standard deviation. However, attack-injected features have extreme outlier values — for example, during a data exfiltration attack, byte_rate increases 50 times its normal value. Such extreme values would severely skew the mean and standard deviation, distorting the normalisation of all normal samples. RobustScaler uses the median and interquartile range instead, which are not affected by outliers. This preserves the normal feature distribution even when anomalous samples are present."

---

## Question 4: "Why did you build separate anomaly models for each device instead of one global model?"

**Answer:**
> "This is a critical design decision. A smart camera normally uploads 600 KB per second — this is entirely normal behaviour. But for a motion sensor, uploading 600 KB per second would be a catastrophic anomaly. A global model trained on all device types cannot learn what is 'normal' for any individual device — it would either generate massive false positives for cameras or miss attacks on sensors. Each device has its own Isolation Forest and One-Class SVM trained exclusively on that device's normal traffic, so the definition of 'normal' is device-specific."

---

## Question 5: "What is Isolation Forest and how does it detect anomalies?"

**Answer:**
> "Isolation Forest is an unsupervised anomaly detection algorithm that works on a simple observation — anomalies are rare and different from normal data, so they are easier to isolate. The algorithm builds an ensemble of 50 random binary trees. For each tree, it randomly selects a feature and a random split value and recursively partitions the data. Anomalies get isolated in very few splits — they have a short average path length across all trees. Normal points require many splits to isolate — they have a long average path length. The anomaly score is the normalised inverse of the mean path length. We train only on normal traffic, so anomalous test flows produce shorter-than-expected paths and get high anomaly scores."

---

## Question 6: "What is One-Class SVM and why do you combine it with Isolation Forest?"

**Answer:**
> "One-Class SVM maps the training data to a high-dimensional feature space using an RBF kernel and finds the maximum-margin hyperplane that separates the data from the origin. At test time, points falling on the wrong side of this hyperplane — outside the learned data boundary — are flagged as anomalies. We combine it with Isolation Forest in a 60-40 weighted ensemble because the two models make errors in different regions: Isolation Forest excels at detecting extreme point anomalies like DoS floods, while One-Class SVM provides finer boundary discrimination for near-normal anomalies. Their combination reduces both false positives and false negatives."

---

## Question 7: "Why is the confidence threshold set to 0.75?"

**Answer:**
> "The confidence threshold of 0.75 means that if the model is less than 75% confident in its device type prediction, it returns 'unknown' rather than forcing a potentially incorrect label. In a security system, a wrong device type label can be more dangerous than an unknown label — if we misidentify a compromised thermostat as a camera, the wrong per-device anomaly model is used and the attack may go undetected. The 0.75 threshold was chosen to prioritise precision: when the model is uncertain, it is better to flag for manual investigation than to guess."

---

## Question 8: "What attacks does your system detect?"

**Answer:**
> "We model three attack categories that represent the most common IoT botnet behaviours seen in the wild, specifically in the Mirai and Gafgyt malware families. Data exfiltration — where a compromised device begins uploading large volumes of data to an external server, multiplying its normal upload rate 30 to 80 times. Port scan — where the device systematically scans hundreds of IP addresses and port numbers to find new victims, causing unique_dest_ports to jump from 1–4 to 500–1500 and port entropy to jump from under 1 bit to 8–10 bits. DoS participation — where the device floods a target with packets, increasing its packet rate 50 to 120 times and its SYN ratio dramatically."

---

## Question 9: "What real-world dataset did you use?"

**Answer:**
> "We used the N-BaIoT dataset published by Meidan et al. from Ben-Gurion University in 2018. It contains real network traffic from nine physical IoT devices including Danmini and Ennio doorbells, an Ecobee thermostat, Philips Baby Monitor, and multiple Provision and SimpleHome security cameras, captured both during normal operation and during active Mirai and Gafgyt botnet infection. The dataset provides over 7 million flow records. We also constructed a synthetic dataset of 1,600 flows for controlled training, with statistically parameterised per-device profiles based on published IoT traffic characterisation studies."

---

## Question 10: "What is the accuracy of your system?"

**Answer:**
> "For device fingerprinting, Random Forest, Gradient Boosting, and the Voting Ensemble all achieve perfect 100% test accuracy with a macro ROC-AUC of 1.0000 across all 8 device types. The SVM achieves 87.50% with ROC-AUC 0.9900. For anomaly detection, all 8 per-device detectors achieve ROC-AUC above 0.91, with a mean of 0.9741 across all device types. Mean anomaly scores for normal traffic are 0.573 to 0.601 and for attack traffic 0.905 to 0.999 — all well above the 0.75 alert threshold. This creates a reliable discrimination margin ensuring very few false positives or missed attacks."

---

---

# PART 5: AFTER THE PANEL

---

## 5.1 Shutting Down the System

After your panel session is complete:

1. Go to the terminal where `python run.py` is running.
2. Press **Ctrl + C**.
3. You will see:

```
[*] Shutting down ...
[*] Done.
```

Both the API server and the dashboard will stop cleanly.

---

## 5.2 Quick Checklist for Panel Day

Use this checklist to make sure everything is ready:

- [ ] Laptop fully charged (bring charger)
- [ ] Python installed and working (`python --version`)
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Models trained (`python train.py` completed — models/ folder has .pkl files)
- [ ] Tests passing (`pytest tests/ -v` shows all PASSED)
- [ ] Plots available in plots/ folder (9 PNG files)
- [ ] Browser bookmarks set for http://127.0.0.1:8050 and http://127.0.0.1:8000/docs
- [ ] Dissertation report printed and ready
- [ ] This demo guide printed and ready as reference

---

## 5.3 Emergency Troubleshooting

| Problem | Solution |
|---------|----------|
| `python run.py` shows "Models not found" | Run `python train.py` first, wait for completion |
| Port 8000 already in use | Run `netstat -ano \| findstr :8000` in cmd, then kill the process |
| Port 8050 already in use | Same as above for port 8050 |
| Dashboard not loading | Wait 5 seconds after running run.py, then refresh the browser |
| API returns 503 error | Models not loaded — check models/ folder has .pkl files |
| pip install fails | Check internet connection; try `pip install -r requirements.txt --no-cache-dir` |
| ImportError on startup | Run `pip install -r requirements.txt` again to fix missing packages |

---

---

*Document prepared for M.Tech Cyber Forensics panel presentation*
*Md Ghufran Alam — Roll No. NDU202400038 — NIELIT Srinagar — May 2026*
