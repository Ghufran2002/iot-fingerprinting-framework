# Presentation Script — Simple English
**IoT Device Fingerprinting & Anomaly Detection Framework**
Md Ghufran Alam | NDU202400038 | M.Tech Cyber Forensics | NIELIT Srinagar

---

## SLIDE 1 — Title Slide

"Good morning, respected panel members.

My name is **Md Ghufran Alam**, Roll Number **NDU202400038**.
I am a student of M.Tech in Cyber Forensics at NIELIT Srinagar, Session 2024–2026.

Today I am presenting my dissertation:
**'Design of a Framework for IoT Device Fingerprinting and Anomaly Detection for Smart Home using Machine Learning.'**

This work is supervised by **Dr. Syed Nisar Hussain Bukhari**, NDU Coordinator, Department of CSE, NIELIT Srinagar.

The system I have built is **live and running right now** — the link is visible on this slide. I will demonstrate it live during the presentation.

Let me begin."

---

## SLIDE 2 — Problem Statement

"Let me start with the problem I am solving.

IoT devices — smart cameras, thermostats, doorbells, smart bulbs — are everywhere in homes today. But they have a serious security problem.

In **2016, the Mirai botnet** infected over **600,000 IoT devices** and launched a massive attack. It generated **620 Gigabits per second** of traffic and took down **Twitter, Netflix, Reddit, and GitHub** — all at the same time.

This happened because of three core reasons:
- Smart devices **cannot run antivirus software** — they don't have enough processing power
- Traditional firewalls only see IP addresses and ports — they **don't know what device** they are protecting
- There is **no baseline** for what normal behavior looks like for a smart camera or thermostat

So my framework answers three fundamental questions:
1. **Which device is this** on my network? — Device Fingerprinting
2. **Is it behaving normally** right now? — Anomaly Detection
3. **Why did the model flag it?** — SHAP Explainability"

---

## SLIDE 3 — System Architecture

"This slide shows the end-to-end pipeline of my framework.

**Input:** Network traffic is captured and **37 features** are extracted — things like packet rate, byte count, TCP/UDP ratio, and destination ports.

These features are first **normalized using RobustScaler** to handle outliers.

Then the pipeline splits into **three parallel modules:**

**Left — Device Fingerprinting:**
A Random Forest model identifies which type of device this is. It outputs a device label and a confidence percentage.

**Center — Anomaly Detection:**
An ensemble of Isolation Forest and One-Class SVM decides whether the device is behaving normally. It outputs an anomaly score between 0 and 1.

**Right — SHAP Explainability:**
For every prediction, the top 10 features that influenced the decision are explained — so a security analyst knows exactly why the model flagged something.

**At the bottom:**
All results go to an Alert Manager, a FastAPI REST API, and a live HTML dashboard with real-time Plotly.js charts.

Everything runs inside a single Docker container on one port."

---

## SLIDE 4 — Dataset & Feature Engineering

"For training this framework, I used the **N-BaIoT dataset** from the UCI Machine Learning Repository, ID number 442.

This dataset was collected from **9 real physical IoT devices** — not simulated. It includes:
- Normal traffic from each device
- **Mirai botnet** attack traffic — 5 variants: ack, scan, syn, udp, udpplain
- **BASHLITE/Gafgyt** attack traffic — 5 variants: combo, junk, scan, tcp, udp

The original dataset had **115 features**. I carefully selected and mapped them to **37 meaningful features** that actually describe device behavior.

These 37 features fall into 7 categories:
1. **Temporal** — flow duration, inter-arrival times
2. **Volume** — packet count, byte count, packet rate
3. **Packet Size** — mean, min, max, standard deviation
4. **Protocol** — TCP, UDP, SYN, FIN, ACK ratios
5. **Application Layer** — HTTPS, MQTT, CoAP, DNS queries
6. **Direction** — upload bytes, download bytes, ratio
7. **Destination** — unique ports, unique IPs, port entropy

The most important insight here is that **protocol features are the most discriminative.** A smart camera always uses HTTPS with large packets. A thermostat always uses MQTT with tiny packets. A smart bulb uses CoAP. These patterns do not overlap — that is what makes fingerprinting possible."

---

## SLIDE 5 — Machine Learning Models

"My framework has two ML modules.

**Module 1 — Device Fingerprinting** (supervised classification):

I trained and compared four models:
- **Random Forest** — 100 trees, balanced class weights — achieved **100% accuracy**
- **Gradient Boosting** — 100 trees, learning rate 0.1 — **100% accuracy**
- **SVM with RBF kernel** — **94.89% accuracy**
- **Voting Ensemble** — combination of all three — **100% accuracy**

Training used **SMOTE balancing** so that rare device types are not underrepresented. A confidence threshold of **60%** is set — if the model is less than 60% confident, the device is marked as 'Unknown', which itself is a security signal.

---

**Module 2 — Anomaly Detection** (unsupervised):

The approach here is completely different. I built a **separate model for each device type** — because normal traffic for a camera is completely different from normal traffic for a thermostat.

**The models are trained only on normal traffic** — no attack data is given during training. This is realistic because in real deployments, attack patterns are unknown in advance.

Each device gets an ensemble of:
- **Isolation Forest** — isolates anomalies using random trees
- **One-Class SVM** — learns a boundary around normal data

The final anomaly score is a weighted average. The **threshold is 0.75:**
- Below 0.75 → Normal
- 0.50–0.65 → LOW alert
- 0.65–0.80 → MEDIUM alert
- 0.80–0.90 → HIGH alert
- 0.90 and above → CRITICAL"

---

## SLIDE 6 — Results: Device Fingerprinting

"The fingerprinting results are very strong.

From the table:
- **Random Forest, Gradient Boosting, and Voting Ensemble** all achieved **100% test accuracy, ROC-AUC of 1.0, and F1-score of 1.0**
- **SVM** achieved 94.89% — which is also excellent

Looking at the per-device breakdown — all 8 device categories achieved 100% accuracy, 1.0 precision, and 1.0 recall. There was not a single misclassification.

**The key insight for the panel:**
This level of accuracy is possible because each IoT device type has a unique protocol fingerprint. A smart camera always sends large HTTPS packets at high rates. A thermostat sends tiny MQTT messages at very low rates. A smart bulb uses CoAP on port 5683. These signatures do not overlap.

Most importantly — **no hardware access, no credentials, no agent installed on any device.** Everything is inferred purely from network traffic — just like a fingerprint identifies a person."

---

## SLIDE 7 — Results: Anomaly Detection

"For anomaly detection, the AUC-ROC scores are:
- **Smart Doorbell** — best performer at **AUC 0.8773**
- **Smart Thermostat** — **0.8590**
- Other devices range from 0.71 to 0.79

**The panel may ask — why is the F1 score lower than AUC-ROC?**

The answer is this:

Mirai and BASHLITE were specifically **designed to blend with normal IoT traffic.** They mimic legitimate device behavior to avoid detection. This is their core design goal.

My model was **trained only on normal traffic** — it never saw any attack data. Despite that, it achieved AUC up to 0.877 — which means it correctly learned the boundary of normal behavior.

**AUC-ROC is the right metric for this task** because it is threshold-independent. F1 score depends on the threshold — in a real deployment, the threshold can be tuned to improve F1 based on the use case.

In my live demo — **zero false positives on normal traffic** and **100% detection rate on all three injected attack types.**"

---

## SLIDE 8 — SHAP Explainability

"Now let me explain the third component — SHAP Explainability.

**Why does explainability matter in security?**

A black-box alert that only says 'anomaly detected' is not useful for a security analyst. The analyst needs to know **why** the model flagged something — which feature triggered it, how unusual it is, and whether it makes sense.

SHAP — SHapley Additive exPlanations — gives exactly that. For every prediction, it shows the **top 10 features** that influenced the decision and in which direction.

The example on this slide shows an **Unknown device with only 46% confidence:**
- **tcp_ratio** — Red — pushing the score away from any known device type
- **udp_ratio** — Red — too high for the predicted class
- **is_mqtt** — Green — partially supports the classification
- **mean_dest_port** — Red — port profile does not match any known device

This allows an analyst to verify the alert **in seconds instead of minutes.**

**Implementation details:**
- I used **TreeExplainer** — which is 10x faster than KernelExplainer for tree-based models
- It runs on the Random Forest model
- Available at the **POST /explain** endpoint
- Also shown live in the monitoring dashboard
- Response time is **under 30 milliseconds**"

---

## SLIDE 9 — Live Deployment

"My framework is not just a prototype — it is **deployed and publicly accessible right now.**

**Platform:** HuggingFace Spaces using Docker SDK — free tier, public visibility.

**Architecture:** FastAPI serves everything on a **single port — 7860** — including the REST API, live dashboard, and Swagger UI. This is important because HuggingFace Spaces exposes only one port.

**Available URLs:**
- Live Dashboard — main monitoring interface with real-time charts
- API Docs — Swagger UI with all endpoints documented and testable
- Status Page — health check page

**8 API endpoints are available:**
- GET: /health, /devices, /metrics
- POST: /fingerprint, /anomaly/score, /analyze, /explain, /alerts/recent

The **/analyze** endpoint is the most powerful — it does fingerprinting and anomaly detection in a **single API call.**

**Performance:**
- API latency: approximately **40 milliseconds**
- Fingerprinting accuracy: **100%** across all 8 device types
- System is live and healthy"

---

## SLIDE 10 — Demo: Device Fingerprinting

"This slide shows the fingerprinting demo — 8 different devices identified from network traffic alone.

- **192.168.1.45** → Smart Camera — 99% confidence — HTTPS traffic, 400 packets per second, large packets on port 443
- **192.168.1.22** → Smart Thermostat — 98% — MQTT, only 2 packets per second, 80-byte packets on port 1883
- **192.168.1.10** → Smart TV — 97% — video streaming, 695 MB download, 18 unique destination IPs
- **192.168.1.77** → Smart Bulb — 96% — CoAP protocol, only 4 packets, port 5683
- **192.168.1.99** → Motion Sensor — 95% — event-driven traffic, MQTT and CoAP
- **192.168.1.55** → Smart Plug — 97% — MQTT, port 8883
- **192.168.1.33** → Smart Speaker — 98% — HTTPS, voice streaming pattern, 5 cloud IPs
- **192.168.1.88** → Smart Doorbell — 96% — camera and audio burst, 2.5 MB upload

**The key point:**
No hardware access. No device credentials. No software installed on any device. The model reads only network traffic — and correctly identifies every single device."

---

## SLIDE 11 — Demo: Anomaly Detection

"This slide shows the anomaly detection demo with four test cases.

**Test 1 — Normal Camera Traffic:**
Score: **0.0000 — NORMAL**
The camera was sending 400 packets per second, 28 MB upload, upload-to-download ratio of 2 — which is its normal behavior. The model correctly classified it as normal. Zero false positives.

**Test 2 — Data Exfiltration (Mirai attack):**
Score: **0.8060 — HIGH ALERT**
The same camera suddenly uploaded **1.68 Gigabytes**. The upload-to-download ratio jumped from 2 to **120**. The model immediately flagged this as a HIGH severity anomaly.

**Test 3 — Port Scan / Reconnaissance:**
Score: **0.7745 — MEDIUM ALERT**
A thermostat was scanning **1200 ports across 250 IP addresses** — port entropy reached 9.5. This is completely impossible for a normal thermostat. The model flagged it as MEDIUM severity.

**Test 4 — Combined /analyze Endpoint:**
Score: **0.8060 — HIGH**
A single API call automatically identified the device as a camera and detected the exfiltration — both in one request.

**Summary: Zero false positives on normal traffic. All three attack types detected with correct severity levels.**"

---

## SLIDE 12 — Conclusion & Contributions

"To conclude, this dissertation delivers eight concrete contributions:

1. **Fingerprinting** — 100% accuracy on 8 IoT device types using only network traffic. No device access required.

2. **Anomaly Detection** — Per-device unsupervised ensemble detects Mirai and BASHLITE with AUC up to 0.877.

3. **Explainability** — SHAP TreeExplainer provides real-time top-10 feature contributions for every single prediction.

4. **Production Deployment** — Live on HuggingFace Spaces, publicly accessible, sub-40ms latency.

5. **REST API** — 8 FastAPI endpoints including the combined /analyze and /explain endpoints.

6. **Dashboard** — Live HTML/Plotly.js monitoring dashboard with anomaly timeline, severity chart, and real-time alert feed.

7. **Dataset** — Trained on real N-BaIoT data with real Mirai and BASHLITE attack traffic — not simulated.

8. **Open Source** — Full code on GitHub, MIT licensed, fully reproducible.

**The most important point — this system is live right now.** It is not a theoretical model. It is a working, deployed, publicly accessible security framework."

---

## SLIDE 13 — Thank You

"Thank you, respected panel members, for your time and attention.

I am happy to answer your questions."

---

## EXPECTED PANEL QUESTIONS

**Q1: Why is the F1 score low for anomaly detection?**
Mirai and BASHLITE are specifically designed to mimic normal IoT traffic patterns. My model was trained only on normal data and never saw any attacks. Despite this, it achieved AUC of 0.877. AUC-ROC is the correct metric for anomaly detection because it is threshold-independent. F1 depends on the threshold and can be tuned per deployment.

**Q2: 100% fingerprinting accuracy — is this overfitting?**
No. The dataset contains physically different device types with genuinely non-overlapping protocol signatures. A camera always uses HTTPS, a thermostat always uses MQTT, a bulb always uses CoAP. The train-test split was proper. The 100% accuracy reflects real separability in the data, not overfitting.

**Q3: How would this work on a real network?**
Traffic is captured from a network tap or mirror port. The 37 features are extracted from each flow and sent to the POST /fingerprint or POST /analyze endpoint. The system can be deployed at the edge — it is lightweight enough to run on a Raspberry Pi.

**Q4: Why SHAP and not LIME?**
TreeExplainer is native to tree-based models like Random Forest and is approximately 10x faster than LIME. LIME is approximation-based. SHAP computes exact Shapley values, making it more mathematically rigorous and consistent.

**Q5: Is there a gap between the dataset and real-world traffic?**
N-BaIoT was captured from real physical devices — not simulated. However, new device types not present in the dataset would require retraining. This is acknowledged as future work in the dissertation.

**Q6: How does HuggingFace Spaces handle production load?**
The free tier provides 16 GB RAM and 2 vCPUs — sufficient for this use case. Models are loaded from PKL files at startup with a cold start of approximately 10 seconds. All inference is in-memory after that.

---
*Script for panel defense — NIELIT Srinagar, May 2026*
