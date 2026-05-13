# PRESENTATION SCRIPT — Slide-by-Slide
**Md Ghufran Alam | NDU202400038 | M.Tech Cyber Forensics | NIELIT Srinagar**

---

## SLIDE 1 — Title Slide

> "Good morning respected panel members. I am Md Ghufran Alam, Roll Number NDU202400038, pursuing M.Tech in Cyber Forensics from NIELIT Srinagar, Batch 2024 to 2026.
>
> My thesis is titled: *Design of a Framework for IoT Device Fingerprinting and Anomaly Detection for Smart Home Using Machine Learning.*
>
> Today I will present the complete system — the problem it solves, the architecture, results, and a live demonstration."

---

## SLIDE 2 — Problem Statement

> "The problem I am addressing is the growing security gap in smart home IoT environments.
>
> By 2030, there will be over 30 billion IoT devices globally, yet 70% of them lack even basic security controls. The attack surface has grown 10 times in the last five years, resulting in over 1.5 trillion rupees in annual losses worldwide.
>
> The core issue is this — IoT devices have no built-in identity. A router cannot tell whether the device at IP 192.168.1.45 is a smart camera or a compromised device pretending to be one.
>
> Furthermore, these devices use heterogeneous protocols — MQTT, CoAP, HTTPS — making unified monitoring difficult. Traditional IDS systems are not designed for constrained IoT environments, and there is no per-device baseline to distinguish normal traffic spikes from actual attacks.
>
> My framework solves exactly this problem."

---

## SLIDE 3 — Objectives

> "I defined six clear objectives for this project.
>
> First — design a passive, non-intrusive framework that does not interfere with device operation.
>
> Second — extract 37 statistical and protocol-level features from network flows, without requiring deep packet inspection or payload access.
>
> Third — classify 8 distinct smart home device types with accuracy above 95%.
>
> Fourth — detect three classes of real-world attacks using a per-device ensemble of Isolation Forest and One-Class SVM.
>
> Fifth — expose all this through a production-ready REST API built with FastAPI and a live monitoring dashboard.
>
> Sixth — establish per-device behavioural baselines so that a camera uploading 600 KB per second is normal, but a motion sensor doing the same is flagged immediately."

---

## SLIDE 4 — System Architecture

> "The system follows a six-stage pipeline.
>
> Stage one — data generation. I generate 1,600 synthetic IoT network flows, 200 per device, parameterised from the real N-BaIoT dataset.
>
> Stage two — feature extraction. From each flow, 37 features are computed across seven categories — temporal, volume, packet size, protocol flags, application layer, traffic direction, and destination.
>
> Stage three — preprocessing. Features are normalised using RobustScaler — which handles outliers better than StandardScaler — and the training set is balanced using SMOTE to handle the 5% anomaly minority.
>
> Stage four — device fingerprinting using Random Forest as the primary model, with Gradient Boosting, SVM, and a Voting Ensemble for comparison.
>
> Stage five — anomaly detection using per-device Isolation Forest and One-Class SVM ensemble.
>
> Stage six — a FastAPI REST API on port 8000 and a Plotly Dash live monitoring dashboard on port 8050."

---

## SLIDE 5 — Dataset Description

> "The dataset consists of 1,600 total flows — 200 flows per device, across 8 device types, with 5% anomaly injection — that is 80 attack flows in total, representing three attack categories.
>
> The dataset is split 70-15-15 — 1,120 flows for training, 240 for validation, and 240 for testing. SMOTE oversampling is applied only on the training set to avoid data leakage."

---

## SLIDE 6 — Feature Engineering

> "This is the core of the framework — 37 features across 7 categories, all computed passively from flow statistics.
>
> Temporal features capture inter-arrival timing patterns. Volume features capture packet and byte rates. Packet size features reveal payload distribution. Protocol flags reveal TCP handshake behaviour. Application layer flags identify HTTPS, MQTT, and CoAP — which are near-unique identifiers for specific devices. Traffic direction features reveal upload-to-download ratio. Destination features — particularly port entropy and unique destination IPs — are the most powerful anomaly indicators.
>
> Critically — no payload inspection is required. All features come from flow-level metadata."

---

## SLIDE 7 — Device Fingerprinting Module

> "The primary fingerprinting model is a Random Forest with 100 trees, maximum depth 15, balanced class weights, and a confidence threshold of 0.75 — meaning if the model is less than 75% confident, it returns 'unknown' rather than forcing a wrong label.
>
> Three comparison models were also trained — Gradient Boosting, SVM with RBF kernel, and a soft-voting Ensemble of all three.
>
> The training pipeline is fully automated — data generation, scaling, SMOTE, parallel model training, automatic best-model selection by validation accuracy, and final evaluation on the held-out test set."

---

## SLIDE 8 — Model Explainability (SHAP)

> "A key contribution of this project is explainability using SHAP — SHapley Additive exPlanations.
>
> SHAP quantifies the contribution of each feature to every individual prediction — not just global averages.
>
> The findings are intuitive. tcp_ratio and udp_ratio are the strongest fingerprints because protocol choice is device-specific by design. ack_ratio reveals TCP handshake frequency. mean_dest_port alone separates cameras on port 443, thermostats on port 1883, and smart bulbs on port 5683. is_coap is a near-perfect separator for smart bulbs — no other device in the dataset uses CoAP.
>
> This means the model is not a black box — every prediction is fully auditable."

---

## SLIDE 9 — Per-Device SHAP Heatmap

> "This heatmap shows which features matter most per device. Brighter means more influential.
>
> For the smart camera — tcp_ratio and is_https are dominant, which makes sense — cameras stream HTTPS video continuously.
>
> For the thermostat — is_mqtt and mean_dest_port 1883 dominate — single MQTT message per flow.
>
> For the smart bulb — is_coap completely dominates — CoAP port 5683 is its unique signature.
>
> For the motion sensor — the lowest byte_count and ack_ratio indicate ultra-low event-driven traffic.
>
> This heatmap visually proves that each device has a distinct, learnable fingerprint."

---

## SLIDE 10 — Anomaly Detection Module

> "For anomaly detection, I trained 8 independent models — one per device — plus a global fallback.
>
> Each per-device model is a weighted ensemble: 60% Isolation Forest plus 40% One-Class SVM.
>
> Isolation Forest uses 50 trees trained only on normal flows. It detects anomalies because rare data points are isolated in fewer random splits — giving them a short average path length.
>
> One-Class SVM with RBF kernel maps normal training data into a high-dimensional space and finds a boundary. Test points outside that boundary are anomalies.
>
> The combination works because the two models make errors in different regions — IF is better for extreme anomalies like DoS floods, while OC-SVM is better for subtle near-boundary anomalies.
>
> The alert threshold is 0.75. Above that, alerts are classified as Low, Medium, High, or Critical."

---

## SLIDE 11 — Anomaly Types Detected

> "The system detects three real-world IoT attack patterns, based on Mirai and Gafgyt botnet behaviours documented in the N-BaIoT paper.
>
> Data Exfiltration — a compromised device starts uploading massive amounts of data. upload_bytes and byte_rate spike 30 to 80 times above normal. For example, a smart camera uploading 1.5 GB instead of its normal 28 MB per flow.
>
> Port Scan — a compromised device probes the local network for victims. unique_dest_ports jumps from 1-4 to 500-1500, and port entropy rises from under 1 bit to 8-10 bits. For example, a smart bulb scanning 800 ports instead of its normal 1 to 3.
>
> DoS Participation — a botnet-infected device floods a target. packet_rate and syn_ratio spike 50 to 120 times. For example, a motion sensor sending 150,000 packets per second instead of its normal 10."

---

## SLIDE 12 — REST API & Dashboard

> "The system exposes a complete REST API with 9 endpoints through FastAPI on port 8000.
>
> The key endpoints are: POST /fingerprint for device identification, POST /anomaly/score for anomaly scoring, POST /analyze for combined fingerprint plus anomaly in one call, POST /explain for live SHAP feature contribution, and POST /demo/inject to simulate attack events.
>
> All endpoints are documented through Swagger UI at /docs.
>
> The Plotly Dash dashboard on port 8050 shows a live anomaly score timeline updated every 5 seconds, device traffic breakdown, alert severity distribution, a score gauge with coloured severity zones, the recent alerts table, and a live SHAP explainability panel that visually shows why the model made each prediction."

---

## SLIDE 13 — Results

> "The results are strong across all metrics.
>
> For device fingerprinting — Random Forest, Gradient Boosting, and the Voting Ensemble all achieve perfect 100% test accuracy with a macro ROC-AUC of 1.0000 across all 8 device classes. The SVM model achieves 87.50% accuracy with ROC-AUC 0.9900. The 37-feature set provides completely separable representations for all device types under tree-based models.
>
> For anomaly detection — all 8 per-device detectors achieve ROC-AUC above 0.91, with a mean of 0.9741 across all device types. Normal traffic anomaly scores average 0.573 to 0.601 — well below the 0.75 alert threshold. Attack traffic scores average 0.905 to 0.999 — far above the threshold. This gives a discrimination margin of over 0.30 score units around the alert boundary, ensuring reliable detection with minimal false positives.
>
> API response time is under 50 milliseconds — suitable for real-time deployment."

---

## SLIDE 14 — Technology Stack

> "The complete system is built in Python 3.9+.
>
> Machine learning uses scikit-learn for all models — Random Forest, Gradient Boosting, SVM, Isolation Forest, and One-Class SVM. SHAP provides explainability. imbalanced-learn provides SMOTE. FastAPI with Uvicorn provides the asynchronous REST API. Plotly Dash provides the live monitoring dashboard. joblib serialises all trained models. pytest covers unit and integration testing.
>
> The entire system runs on a standard Windows 11 laptop with 8 GB RAM — no GPU required."

---

## SLIDE 15 — Conclusion & Future Work

> "To summarise what was achieved —
>
> A complete, passive, non-intrusive ML framework for IoT device fingerprinting and anomaly detection was designed and implemented. 37 carefully engineered features capture distinct device behavioural signatures. The classifier achieves over 97% accuracy across all 8 device types. The per-device ensemble outperforms a single global anomaly detector. Three real-world attack patterns are successfully detected. SHAP explainability makes every prediction auditable. A production-ready REST API with 9 endpoints enables real-time deployment. The live dashboard with SHAP panel provides full transparency for security analysts.
>
> For future work — I plan to capture real traffic using Wireshark on a physical smart home network, explore LSTM and Autoencoder models for temporal pattern learning, implement Federated Learning across multiple homes for privacy-preserving detection, and deploy on a Raspberry Pi gateway for on-premise edge inference."

---

## SLIDE 16 — Thank You

> "This concludes my presentation.
>
> The complete system — training pipeline, REST API, live dashboard, and all 9 evaluation plots — is fully operational and ready for live demonstration.
>
> I am now open for questions. Thank you."

---

## AFTER QUESTIONS END

> "Thank you for your valuable questions and feedback. It was an honour to present my work before this panel."

---

*Total speaking time estimate: 12–15 minutes*
*Demo time: 10–12 minutes*
*Q&A: 10–15 minutes*
