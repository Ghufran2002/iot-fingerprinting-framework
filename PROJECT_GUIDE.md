# IoT Device Fingerprinting & Anomaly Detection — Complete Project Guide
### M.Tech Cyber Forensics | NIELIT Srinagar | Md Ghufran Alam (NDU202400038)

---

## PART 1 — PROJECT KO EK LINE MEIN SAMJHO

> **"Ghar ke IoT devices ke network traffic ko dekhkar — machine learning se pata karo kaunsa device hai aur kuch suspicious toh nahi ho raha."**

---

## PART 2 — PROBLEM KYA THA? (Motivation)

### Real-world Problem:
- Aaj ke smart homes mein cameras, thermostats, TVs, bulbs — sab internet se connected hain
- Har device ka alag-alag traffic pattern hota hai
- Agar kisi device ko hack kar liya jaye (botnet, DDoS, data exfiltration) — admin ko pata hi nahi chalta
- Traditional antivirus IoT pe kaam nahi karta (no OS, no agent)

### Hamara Solution:
- Network traffic ko **passively** monitor karo (device pe kuch install nahi)
- **37 statistical features** nikalo har flow se
- **Machine Learning** se device identify karo (fingerprinting)
- **Anomaly Detection** se attack detect karo

---

## PART 3 — SYSTEM ARCHITECTURE (Poora Flow)

```
┌─────────────────────────────────────────────────────────────┐
│                    SMART HOME NETWORK                       │
│  [Camera] [Thermostat] [TV] [Bulb] [Plug] [Speaker]        │
│  [Doorbell] [Motion Sensor]                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ Network Traffic (flows)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              STEP 1: FEATURE EXTRACTION                     │
│         src/features/extractor.py                           │
│                                                             │
│  Raw packets → 37 Statistical Features per flow            │
│  (Temporal, Volume, Packet Size, Protocol,                  │
│   Application Layer, Direction, Destination)                │
└──────────────────────┬──────────────────────────────────────┘
                       │ 37-dimension feature vector
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              STEP 2: PREPROCESSING                          │
│         src/data/preprocessor.py                            │
│                                                             │
│  StandardScaler → features normalize karo                  │
│  (mean=0, std=1) — ML ke liye zaroori hai                  │
└────────────┬─────────────────────────┬──────────────────────┘
             │                         │
             ▼                         ▼
┌────────────────────┐    ┌────────────────────────────────────┐
│   STEP 3A:         │    │   STEP 3B:                         │
│   FINGERPRINTING   │    │   ANOMALY DETECTION                │
│                    │    │                                    │
│  "Kaunsa device?"  │    │  "Kuch galat toh nahi?"            │
│                    │    │                                    │
│  Random Forest     │    │  Per-device ensemble:              │
│  (100 trees)       │    │  Isolation Forest (60%)            │
│  + GB, SVM,        │    │  + One-Class SVM (40%)             │
│  Voting Ensemble   │    │                                    │
│                    │    │  Score: 0.0 to 1.0                 │
│  Output:           │    │  >= 0.75 → ALERT!                  │
│  Device type +     │    │                                    │
│  Confidence score  │    │                                    │
└────────┬───────────┘    └──────────────┬─────────────────────┘
         │                               │
         └──────────────┬────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              STEP 4: REST API (FastAPI — Port 8000)         │
│         src/api/main.py                                     │
│                                                             │
│  POST /fingerprint    → Device identify karo               │
│  POST /anomaly/score  → Anomaly score nikalo                │
│  POST /analyze        → Dono ek saath                       │
│  GET  /alerts/recent  → Recent alerts                       │
│  GET  /metrics        → System stats                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              STEP 5: DASHBOARD (Plotly Dash — Port 8050)    │
│         src/dashboard/app.py                                │
│                                                             │
│  - Real-time anomaly score timeline                         │
│  - Device distribution (pie chart)                          │
│  - Severity breakdown (bar chart)                           │
│  - Score gauge meter                                        │
│  - Live alerts table                                        │
│  - Auto-refresh every 5 seconds                             │
└─────────────────────────────────────────────────────────────┘
```

---

## PART 4 — HAR COMPONENT KI DETAIL

### 4.1 Dataset (src/data/generator.py)

**Kya hai:** Synthetic IoT network flow data

| Cheez | Value |
|-------|-------|
| Total flows | 1,600 |
| Flows per device | 200 |
| Anomaly percentage | 5% (10 flows per device) |
| Normal flows | 190 per device |

**8 Devices aur unka traffic:**

| Device | Main Protocol | Bandwidth | Traffic Pattern |
|--------|--------------|-----------|-----------------|
| Smart Camera | HTTPS (92%) | Very High (600 KB/s) | Continuous streaming, large packets (1400 bytes) |
| Smart Thermostat | MQTT (90%) | Very Low (200 bytes/s) | Periodic small messages, 8 packets/flow |
| Smart TV | HTTPS (88%) | Highest (200 KB/s) | Long flows (1 hour), 500K packets/flow |
| Smart Bulb | CoAP (92%) | Lowest (240 bytes/s) | Tiny packets (30 bytes), on/off commands |
| Smart Plug | MQTT+CoAP | Low (200 bytes/s) | Short bursts, power reporting |
| Smart Speaker | HTTPS (82%) | Medium (55 KB/s) | Voice streaming, cloud API calls |
| Smart Doorbell | HTTPS (78%) | Medium-High | Burst traffic on motion, camera+audio |
| Motion Sensor | CoAP+MQTT | Ultra Low (270 bytes/s) | Event-driven, 3 packets per event |

**3 Types of Anomalies injected:**
1. **Data Exfiltration** — Upload bytes suddenly 30-80x zyada ho jaata hai
2. **Port Scan** — unique_dest_ports 500-1500 ho jaata hai (normal mein 1-5)
3. **DoS Participation** — packet_rate 50-120x zyada, SYN ratio bahut high

---

### 4.2 Feature Extraction (src/features/extractor.py)

**37 features, 7 categories:**

```
TEMPORAL (5 features):
  flow_duration    → Flow kitni der chali
  mean_iat         → Average inter-arrival time between packets
  std_iat          → Variability in packet timing
  min_iat          → Minimum gap between packets
  max_iat          → Maximum gap between packets

VOLUME (4 features):
  packet_count     → Total packets in flow
  byte_count       → Total bytes transferred
  packet_rate      → Packets per second
  byte_rate        → Bytes per second (bandwidth)

PACKET SIZE (4 features):
  mean_pkt_size    → Average packet size
  std_pkt_size     → Size variability
  min_pkt_size     → Smallest packet
  max_pkt_size     → Largest packet

PROTOCOL FLAGS (6 features):
  tcp_ratio        → TCP packet proportion
  udp_ratio        → UDP packet proportion
  syn_ratio        → SYN flag proportion (connection initiation)
  fin_ratio        → FIN flag proportion (connection closing)
  rst_ratio        → RST flag proportion (reset, error)
  ack_ratio        → ACK flag proportion

APPLICATION LAYER (8 features):
  is_https         → HTTPS traffic (port 443)
  is_mqtt          → MQTT protocol (IoT messaging, port 1883)
  is_coap          → CoAP protocol (constrained devices, port 5683)
  is_mdns          → mDNS (device discovery)
  is_ntp           → NTP (time sync)
  dns_query_count  → DNS queries in flow
  well_known_port_ratio → Well-known ports ka proportion
  is_encrypted     → Encrypted traffic proportion

TRAFFIC DIRECTION (3 features):
  upload_bytes     → Device se bahar jaane wala data
  download_bytes   → Device pe aane wala data
  upload_download_ratio → Upload/Download ratio

DESTINATION (7 features):
  unique_dest_ports    → Kitne alag ports use kiye
  unique_dest_ips      → Kitne alag IPs se baat ki
  port_entropy         → Port diversity (high = suspicious)
  ip_entropy           → IP diversity (high = suspicious)
  well_known_ports_count → Kitne standard ports use kiye
  mean_dest_port       → Average destination port
  std_dest_port        → Port number variability
```

**Why 37 features?**
Har category ek alag angle se device ko identify karta hai:
- Camera bahut zyada data upload karta hai → `upload_bytes` high
- Bulb sirf CoAP use karta hai → `is_coap` = 1
- Port scan mein → `port_entropy` bahut high hoti hai

---

### 4.3 Fingerprinting (src/models/fingerprinter.py)

**Kaam:** Network traffic dekhkar device type predict karna

**4 Models trained:**

| Model | Algorithm | Key Parameters |
|-------|-----------|----------------|
| Random Forest | 100 decision trees (ensemble) | max_depth=15, class_weight='balanced' |
| Gradient Boosting | Boosted trees | n_estimators=100, learning_rate=0.1 |
| SVM | Support Vector Machine | RBF kernel, C=10, probability=True |
| Voting Ensemble | RF + GB + SVM combined | soft voting (probability average) |

**Training Process:**
```
Data split: 80% train, 20% test
Preprocessing: StandardScaler (fit on train, transform both)
Best model selection: Highest validation accuracy
Confidence threshold: 0.75 (neeche = "unknown" return karo)
```

**Output example:**
```json
{
  "device_type": "smart_camera",
  "confidence": 0.9834,
  "is_known": true,
  "model_used": "random_forest"
}
```

---

### 4.4 Anomaly Detection (src/models/anomaly_detector.py)

**Kaam:** Kisi device ka traffic normal hai ya attack?

**Key Concept — Unsupervised Learning:**
- Training sirf NORMAL traffic pe hoti hai
- Model seekhta hai "normal kaisa hota hai"
- Test time pe: normal se bahut alag lage → anomaly!
- Attack data ke labels ki zaroorat nahi

**Per-device ensemble:**
Har device type ka apna alag detector hota hai.
(Camera ka anomaly pattern alag hoga bulb ke anomaly se)

```
Smart Camera Detector = IF_camera + OC-SVM_camera
Smart Bulb Detector   = IF_bulb   + OC-SVM_bulb
... aur 6 aur devices ke liye
+ 1 Global Fallback detector
```

**Score calculation:**
```
Final Score = 0.60 × Isolation_Forest_score + 0.40 × OneClass_SVM_score

Score range: 0.0 to 1.0
0.00 - 0.50 → Normal traffic
0.50 - 0.65 → LOW severity alert
0.65 - 0.80 → MEDIUM severity alert
0.80 - 0.90 → HIGH severity alert
0.90 - 1.00 → CRITICAL severity alert
```

**Isolation Forest (kaise kaam karta hai):**
```
Soch: Ek jungle mein ek strange tree hai.
Us tree ko "isolate" karna — baaki trees se alag karna — bahut aasaan hai.
Normal trees deep mein hain, isolate karna mushkil hai.
Anomaly = jo bahut jaldi isolate ho jaaye (shallow depth)
```

**One-Class SVM (kaise kaam karta hai):**
```
Soch: Normal data ka ek "boundary" learn karo.
Test time pe: boundary ke andar = normal
             boundary ke baahir = anomaly
```

---

### 4.5 Alert Manager (src/utils/alert_manager.py)

**Kaam:** Anomaly score ko alert mein convert karna

**Features:**
- **Cooldown:** Ek IP se 60 seconds mein sirf 1 alert (spam nahi)
- **Severity grading:** Score ke basis pe LOW/MEDIUM/HIGH/CRITICAL
- **Max 500 alerts** store karta hai (deque)
- **Rate tracking:** Total alerts, anomaly rate

---

### 4.6 REST API (src/api/main.py — Port 8000)

**Swagger UI:** http://localhost:8000/docs

**Main Endpoints:**

| Endpoint | Method | Kaam |
|----------|--------|------|
| /health | GET | System status check |
| /devices | GET | 8 device types list |
| /fingerprint | POST | Device identify karo |
| /anomaly/score | POST | Anomaly score nikalo |
| /analyze | POST | Fingerprint + Anomaly ek saath |
| /alerts/recent | GET | Recent alerts dekhho |
| /metrics | GET | Total alerts, anomaly rate |
| /demo/inject | POST | Demo ke liye alert inject karo |

---

### 4.7 Dashboard (src/dashboard/app.py — Port 8050)

**URL:** http://localhost:8050

**6 Visualizations:**
1. **Header Cards** — Total Alerts, Anomaly Rate, Requests, Devices, Features, Threshold
2. **Anomaly Timeline** — Live score graph (red X = alert, blue circle = normal)
3. **Device Pie Chart** — Kaunsa device kitni baar detected hua
4. **Severity Bar Chart** — LOW/MEDIUM/HIGH/CRITICAL count
5. **Score Gauge** — Latest anomaly score (speedometer style)
6. **Alerts Table** — Recent alerts with IP, device, score, severity

**Auto-refresh:** Har 5 seconds mein API call karke update hota hai

---

## PART 5 — PROJECT KAISE CHALAYEN

### Step 1: Dependencies install karo
```bash
pip install -r requirements.txt
```

### Step 2: Models train karo
```bash
python train.py
```
Yeh kya karta hai:
- Synthetic dataset generate karta hai (1600 flows)
- Fingerprinting models train karta hai (RF, GB, SVM, Ensemble)
- Anomaly detectors train karta hai (per-device)
- Plots save karta hai (plots/ folder)
- Models save karta hai (models/ folder)

### Step 3: System start karo
```bash
python run.py
```
Yeh start karta hai:
- FastAPI server at http://localhost:8000
- Plotly Dash dashboard at http://localhost:8050

### Step 4: Dashboard dekho
Browser mein: http://localhost:8050

---

## PART 6 — FILES KA MAP

```
IoT_Device_Fingerprinting_Framework/
│
├── train.py                    ← Training entry point
├── run.py                      ← Start API + Dashboard
├── requirements.txt            ← Dependencies
│
├── src/
│   ├── data/
│   │   ├── generator.py        ← Synthetic data banao
│   │   ├── preprocessor.py     ← StandardScaler
│   │   └── real_loader.py      ← N-BaIoT real data
│   │
│   ├── features/
│   │   └── extractor.py        ← 37 feature definitions
│   │
│   ├── models/
│   │   ├── fingerprinter.py    ← RF, GB, SVM, Ensemble
│   │   ├── anomaly_detector.py ← IF + OC-SVM per device
│   │   └── trainer.py          ← Training pipeline
│   │
│   ├── api/
│   │   └── main.py             ← FastAPI endpoints
│   │
│   ├── dashboard/
│   │   └── app.py              ← Plotly Dash UI
│   │
│   └── utils/
│       ├── alert_manager.py    ← Alert generation
│       └── logger.py           ← Logging
│
├── models/                     ← Saved .pkl files
├── plots/                      ← Generated graphs
├── data/                       ← Dataset CSV files
│   └── nbaiot/                 ← Real N-BaIoT dataset
└── tests/
    └── test_pipeline.py        ← Unit tests
```

---

## PART 7 — PANELIST QUESTIONS & ANSWERS

### Q1: "Aapne dataset kahan se liya?"
**A:**
> "Sir, humne do sources use kiye hain. Primary dataset synthetic hai — humne 8 IoT devices ke realistic traffic profiles banaye hain based on published IoT research. Har device ke liye 200 flows generate kiye, total 1600 flows. 5% anomalies inject ki hain — data exfiltration, port scan, aur DoS participation. Yeh approach isliye choose ki kyunki real IoT attack datasets publicly available nahi hote aur labeling mushkil hoti hai. Additionally, N-BaIoT real-world dataset bhi framework support karta hai."

---

### Q2: "Random Forest hi kyun? Deep Learning kyun nahi?"
**A:**
> "Sir, IoT security context mein Random Forest prefer kiya kyunki: pehla, interpretability — feature importance clearly milti hai, explain kar sakte hain ki model ne kya dekha. Doosra, small dataset pe RF better perform karta hai, deep learning ke liye thousands of samples chahiye. Teesra, inference speed fast hai — real-time detection ke liye zaroori hai. Humne comparison bhi kiya — RF, Gradient Boosting, SVM, aur Voting Ensemble ko evaluate kiya aur best model automatically select hota hai."

---

### Q3: "Anomaly detection mein supervised kyun nahi use kiya?"
**A:**
> "Sir, supervised learning ke liye labeled attack data chahiye hoga — lekin real networks mein attacks rare hote hain aur naye attack types labeled nahi hote. Isolation Forest ek unsupervised approach hai — sirf normal traffic pe train hota hai aur kuch bhi 'normal se bahut alag' dikhe toh flag karta hai. Iska fayda yeh hai ki zero-day attacks bhi detect ho sakte hain jo humne training mein kabhi dekhe nahi."

---

### Q4: "37 features kaafi hain? Aur features hote toh better nahi hota?"
**A:**
> "Sir, 37 features carefully selected hain 7 categories se jo IoT traffic ke sabse important aspects cover karte hain — timing, volume, packet size, protocols, direction, aur destination. Zyada features ka matlab zyada accuracy nahi — 'curse of dimensionality' hota hai. In 37 features se Random Forest ~95% accuracy achieve karta hai, toh aur features add karna diminishing returns deta."

---

### Q5: "Real-time detection kaise hoti hai?"
**A:**
> "Sir, framework mein FastAPI REST API hai port 8000 pe. Jab bhi koi network flow analyze karna ho, `/analyze` endpoint pe POST request bhejte hain with flow features. API fingerprinting model se device identify karta hai, phir per-device anomaly detector se score nikalta hai, aur agar score 0.75 se zyada ho toh alert generate hota hai. Dashboard har 5 seconds mein API poll karta hai aur real-time update dikhata hai."

---

### Q6: "Accuracy kitni hai?"
**A:**
> "Sir, fingerprinting mein Random Forest ~95%+ accuracy aur ~0.99 ROC-AUC achieve karta hai. Anomaly detection mein ROC-AUC metric use kiya kyunki data imbalanced hai — 5% anomaly. Per-device detectors 0.85-0.95 AUC range mein perform karte hain. Precision aur Recall bhi evaluate kiye hain — high precision important hai taaki false alarms kam hon."

---

### Q7: "Dashboard mein alerts kaise aate hain?"
**A:**
> "Sir, dashboard har 5 seconds mein ek simulated network flow generate karta hai. Agar anomaly score threshold 0.75 se cross kare, toh backend API ka `/demo/inject` endpoint call hota hai. API ka alert manager us alert ko register karta hai — device type, source IP, score, aur severity ke saath. `/metrics` aur `/alerts/recent` endpoints se dashboard real-time mein total alerts aur alert details show karta hai."

---

### Q8: "N-BaIoT dataset kya hai?"
**A:**
> "Sir, N-BaIoT ek real-world IoT attack dataset hai jo researchers ne publish kiya. Ismein actual IoT devices — doorbells, cameras, thermostats — ka traffic capture kiya gaya hai, including Mirai aur Gafgyt botnet attacks. Hamara framework yeh dataset bhi support karta hai `python train.py --hybrid` se, jo real data aur synthetic data dono use karta hai."

---

### Q9: "Security mein yeh framework practically kaise deploy karein?"
**A:**
> "Sir, practically deployment mein network tap ya mirror port pe packet capture chalte — tcpdump ya similar tool se. Har flow complete hone pe features extract hote aur REST API ko POST request jaati. API real-time mein device identify karta aur anomaly score deta. Alerts SIEM system (jaise Splunk, ELK) mein jaate ya admin ko email/SMS jaata. Hamara framework yeh pipeline ka ML core hai."

---

### Q10: "SMOTE kya hai? Aapne use kiya?"
**A:**
> "Sir, SMOTE — Synthetic Minority Oversampling Technique — imbalanced data handle karta hai. Hamare dataset mein 95% normal aur 5% anomaly hai. Fingerprinting ke liye SMOTE implicitly handle hota hai Random Forest ke `class_weight='balanced'` parameter se jo minority class ko zyada weight deta hai. Anomaly detection ke liye SMOTE zarori nahi kyunki woh unsupervised hai — sirf normal data pe train hota hai."

---

## PART 8 — KEY NUMBERS (YAAD RAKHEIN)

| Parameter | Value |
|-----------|-------|
| Device types | 8 |
| Features per flow | 37 |
| Feature categories | 7 |
| Total training flows | 1,600 |
| Flows per device | 200 |
| Anomaly fraction | 5% |
| Fingerprinting models | 4 (RF, GB, SVM, Voting) |
| RF trees | 100 |
| IF trees | 50 |
| Alert threshold | 0.75 |
| IF weight | 60% |
| OC-SVM weight | 40% |
| Alert cooldown | 60 seconds |
| API port | 8000 |
| Dashboard port | 8050 |
| Dashboard refresh | 5 seconds |
| Anomaly types | 3 (exfiltration, port scan, DoS) |

---

## PART 9 — ANOMALY TYPES KO VISUALLY SAMJHO

### Data Exfiltration Attack:
```
Normal Camera:   upload_bytes = 28 MB
Attack Camera:   upload_bytes = 28 MB × 50 = 1.4 GB  ← ALARM!
                 byte_rate × 40 ← ALARM!
```

### Port Scan Attack:
```
Normal Device:  unique_dest_ports = 3-5
Port Scan:      unique_dest_ports = 500-1500  ← ALARM!
                port_entropy = 8-10 (normal mein 0.5-2)  ← ALARM!
```

### DoS Participation (Botnet):
```
Normal Device:  packet_rate = 400 packets/sec
Mirai Botnet:   packet_rate = 400 × 80 = 32,000 packets/sec  ← ALARM!
                syn_ratio = 0.005 → 0.15 (SYN flood)  ← ALARM!
```

---

## PART 10 — PRESENTATION TIPS

### Opening (30 seconds):
> "Sir, mera thesis hai — 'Design of Framework for IoT Device Fingerprinting and Anomaly Detection for Smart Home Using Machine Learning.' Smart homes mein IoT devices rapidly increase ho rahe hain lekin inki security bahut weak hai. Hamara framework passively network traffic monitor karke dono kaam karta hai — device identification aur attack detection — bina device pe kuch install kiye."

### Demo kaise dikhayein:
1. `python run.py` — server start karo
2. Browser mein http://localhost:8050 open karo
3. Dashboard dikhao — score timeline, device pie, severity chart
4. Swagger UI dikhao — http://localhost:8000/docs
5. `/analyze` endpoint mein example request chalao

### Closing (20 seconds):
> "Sir, is framework se smart home admins real-time mein device fingerprinting aur anomaly detection kar sakte hain. Future work mein real network tap integration, deep learning models, aur federated learning for privacy-preserving detection consider kar sakte hain."

---

*Document prepared for M.Tech thesis presentation — NIELIT Srinagar, 2026*
