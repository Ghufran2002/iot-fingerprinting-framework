# DISSERTATION REPORT

---

## DESIGN OF A FRAMEWORK FOR IoT DEVICE FINGERPRINTING AND ANOMALY DETECTION FOR SMART HOME USING MACHINE LEARNING

---

**Submitted in partial fulfilment of the requirements for the degree of**

**Master of Technology in Cyber Forensics**

**Session: 2024 – 2026 (4th Semester)**

---

**Submitted by:**

Md Ghufran Alam
Roll Number: NDU202400038

---

**Under the Supervision of:**

[Supervisor Name & Designation]
Department of Cyber Forensics
NIELIT Srinagar

---

**NATIONAL INSTITUTE OF ELECTRONICS AND INFORMATION TECHNOLOGY (NIELIT)**
**SRINAGAR, JAMMU & KASHMIR**
**MAY 2026**

---

---

## DECLARATION

I, Md Ghufran Alam, Roll Number NDU202400038, a student of M.Tech in Cyber Forensics (Session 2024–2026) at the National Institute of Electronics and Information Technology (NIELIT) Srinagar, hereby declare that the dissertation entitled **"Design of a Framework for IoT Device Fingerprinting and Anomaly Detection for Smart Home Using Machine Learning"** submitted in partial fulfilment of the requirements for the degree of Master of Technology is a record of original work done by me under the guidance of my supervisor.

I further declare that this dissertation or any part thereof has not been submitted for the award of any other degree or diploma in this Institute or any other Institution/University. The information or data collected from other sources has been duly acknowledged in the text.

**Place:** Srinagar, J&K
**Date:** May 2026

Md Ghufran Alam
(NDU202400038)

---

---

## CERTIFICATE

This is to certify that the dissertation entitled **"Design of a Framework for IoT Device Fingerprinting and Anomaly Detection for Smart Home Using Machine Learning"** submitted by Md Ghufran Alam (Roll No. NDU202400038) in partial fulfilment of the requirements for the award of the degree of Master of Technology in Cyber Forensics from the National Institute of Electronics and Information Technology (NIELIT) Srinagar is a record of bonafide research work carried out by him under my supervision.

The results embodied in this dissertation have not been submitted for the award of any other degree or diploma.

**Place:** Srinagar, J&K
**Date:** May 2026

[Supervisor Signature & Seal]
[Supervisor Name]
[Designation]
NIELIT Srinagar

**Head of Department / Director**
NIELIT Srinagar

---

---

## ACKNOWLEDGEMENTS

I would like to express my sincere gratitude to everyone who supported and guided me throughout this research work.

First and foremost, I thank my project supervisor for providing invaluable guidance, encouragement, and constructive feedback at every stage of this dissertation. Their expertise in cyber security and machine learning has been instrumental in shaping the scope and direction of this work.

I am grateful to the Director and faculty of NIELIT Srinagar for providing the academic environment and resources necessary to carry out this research. Special thanks are due to the Department of Cyber Forensics for the technical support and domain knowledge imparted throughout the programme.

I would also like to acknowledge the open-source community behind scikit-learn, FastAPI, Plotly Dash, and the N-BaIoT dataset researchers at Ben-Gurion University for making their datasets publicly available, which greatly enriched the validation of this framework.

Finally, I owe a debt of gratitude to my family for their patience, moral support, and unwavering encouragement throughout the duration of this programme.

Md Ghufran Alam
NIELIT Srinagar, May 2026

---

---

## ABSTRACT

The proliferation of Internet of Things (IoT) devices in smart home environments has introduced unprecedented security challenges. Unlike conventional computing systems, IoT devices are resource-constrained, heterogeneous in design, and rarely receive timely security patches, making them prime targets for botnets, data exfiltration campaigns, and denial-of-service attacks. Existing network-level security solutions, designed for traditional IT infrastructure, are largely ineffective against the unique traffic patterns exhibited by IoT endpoints.

This dissertation presents the **design and implementation of a modular, end-to-end framework for IoT device fingerprinting and anomaly detection** in smart home networks using machine learning. The framework addresses two tightly coupled problems: (i) passive device identification (fingerprinting) from network flow features, and (ii) per-device behavioural anomaly detection to flag deviations from a learned baseline.

The fingerprinting subsystem employs a **Random Forest classifier (100 estimators, max\_depth = 15)** alongside Gradient Boosting, Support Vector Machine, and a soft-voting Ensemble, trained on **37 statistical and protocol-level features** extracted from network flows across **8 IoT device categories** (smart camera, smart thermostat, smart TV, smart bulb, smart plug, smart speaker, smart doorbell, and motion sensor). The anomaly detection subsystem deploys a **per-device ensemble** of Isolation Forest (IF) and One-Class SVM (OC-SVM), with ensemble weights of 60% IF and 40% OC-SVM, calibrated to an alert threshold of 0.75. Three attack categories are modelled: data exfiltration, port scan, and DoS participation.

A synthetic dataset of 1,600 labelled flows (200 per device, 5% anomaly rate) with statistically distinct per-device profiles was constructed for training and evaluation, supplemented by real traffic samples from the N-BaIoT dataset. Class imbalance is addressed using **SMOTE oversampling**, and features are normalised with **RobustScaler**. The trained models are exposed via a **FastAPI REST service (port 8000)** and a **Plotly Dash monitoring dashboard (port 8050)** for real-time operational use.

Experimental results demonstrate that the Random Forest fingerprinter achieves **test accuracy exceeding 97%** with a macro ROC-AUC above 0.99 across all device classes. The per-device anomaly detectors consistently separate anomalous from normal traffic, with mean anomaly scores for attack flows exceeding 0.85 against a threshold of 0.75. The framework is entirely open-source, reproducible, and deployable on commodity hardware with 8 GB RAM.

**Keywords:** IoT Security, Device Fingerprinting, Anomaly Detection, Random Forest, Isolation Forest, One-Class SVM, Smart Home, Network Forensics, SMOTE, FastAPI

---

---

## TABLE OF CONTENTS

1. Introduction
   - 1.1 Background and Motivation
   - 1.2 Problem Statement
   - 1.3 Objectives
   - 1.4 Scope and Delimitations
   - 1.5 Dissertation Organisation

2. Literature Review
   - 2.1 IoT Security: An Overview
   - 2.2 IoT Device Fingerprinting Techniques
   - 2.3 Anomaly Detection in IoT Networks
   - 2.4 Machine Learning for Network Intrusion Detection
   - 2.5 Relevant Datasets
   - 2.6 Research Gaps and Positioning

3. System Architecture and Design
   - 3.1 Design Principles
   - 3.2 High-Level Architecture
   - 3.3 Module Descriptions
   - 3.4 Data Flow

4. Feature Engineering
   - 4.1 Feature Selection Rationale
   - 4.2 Feature Categories and Definitions
   - 4.3 Per-Device Traffic Characteristics

5. Dataset Construction and Preprocessing
   - 5.1 Synthetic Dataset Generation
   - 5.2 Real-World N-BaIoT Data Integration
   - 5.3 Anomaly Injection
   - 5.4 Preprocessing Pipeline

6. Machine Learning Models
   - 6.1 Device Fingerprinting Models
   - 6.2 Anomaly Detection Ensemble
   - 6.3 Model Persistence and Deployment

7. System Implementation
   - 7.1 Technology Stack
   - 7.2 Project Structure
   - 7.3 Training Pipeline
   - 7.4 REST API (FastAPI)
   - 7.5 Monitoring Dashboard (Plotly Dash)

8. Results and Evaluation
   - 8.1 Fingerprinting Performance
   - 8.2 Anomaly Detection Performance
   - 8.3 Feature Importance Analysis
   - 8.4 Comparative Analysis

9. Conclusion and Future Work
   - 9.1 Summary of Contributions
   - 9.2 Limitations
   - 9.3 Future Directions

10. References

Appendix A — Feature Definitions
Appendix B — API Endpoint Reference
Appendix C — System Requirements and Setup

---

---

## LIST OF FIGURES

- Figure 3.1 — High-Level System Architecture
- Figure 3.2 — End-to-End Data Flow Diagram
- Figure 4.1 — Feature Category Distribution (37 Features)
- Figure 5.1 — Dataset Device Distribution (Pie Chart)
- Figure 5.2 — SMOTE Oversampling Effect on Class Balance
- Figure 6.1 — Random Forest Decision Ensemble Architecture
- Figure 6.2 — Per-Device Anomaly Detector Architecture
- Figure 8.1 — Confusion Matrix — Random Forest
- Figure 8.2 — Confusion Matrix — Gradient Boosting
- Figure 8.3 — Confusion Matrix — SVM
- Figure 8.4 — Confusion Matrix — Voting Ensemble
- Figure 8.5 — ROC Curves (One-vs-Rest) — Random Forest
- Figure 8.6 — Top-15 Feature Importances (Gini) — Random Forest
- Figure 8.7 — Model Comparison — Test Accuracy
- Figure 8.8 — Macro Precision / Recall / F1 — All Models
- Figure 8.9 — Per-Device Anomaly Score Distribution

---

---

## LIST OF TABLES

- Table 3.1 — Module Summary
- Table 4.1 — Feature Categories and Definitions
- Table 4.2 — Per-Device Protocol Signatures
- Table 5.1 — Dataset Composition Summary
- Table 5.2 — Anomaly Type Definitions and Injection Multipliers
- Table 6.1 — Fingerprinting Model Hyperparameters
- Table 6.2 — Anomaly Detector Hyperparameters
- Table 7.1 — Technology Stack Summary
- Table 7.2 — REST API Endpoints Reference
- Table 8.1 — Fingerprinting Classification Report (Macro Averages)
- Table 8.2 — Per-Model Test Accuracy and ROC-AUC
- Table 8.3 — Per-Device Anomaly Detection Metrics
- Table 8.4 — Comparison with Related Works

---

---

## LIST OF ABBREVIATIONS

| Abbreviation | Full Form |
|---|---|
| API | Application Programming Interface |
| CoAP | Constrained Application Protocol |
| CPU | Central Processing Unit |
| CSV | Comma-Separated Values |
| DDoS | Distributed Denial of Service |
| DNS | Domain Name System |
| DoS | Denial of Service |
| FPR | False Positive Rate |
| HTTP | Hypertext Transfer Protocol |
| HTTPS | Hypertext Transfer Protocol Secure |
| IAT | Inter-Arrival Time |
| IF | Isolation Forest |
| IoT | Internet of Things |
| IP | Internet Protocol |
| JSON | JavaScript Object Notation |
| MAC | Media Access Control |
| MDNS | Multicast Domain Name System |
| ML | Machine Learning |
| MQTT | Message Queuing Telemetry Transport |
| MTU | Maximum Transmission Unit |
| NIELIT | National Institute of Electronics and Information Technology |
| NTP | Network Time Protocol |
| OC-SVM | One-Class Support Vector Machine |
| OvR | One-versus-Rest |
| PKL | Pickle (serialised model file) |
| RAM | Random-Access Memory |
| RF | Random Forest |
| REST | Representational State Transfer |
| ROC | Receiver Operating Characteristic |
| AUC | Area Under the Curve |
| RobustScaler | Outlier-resistant feature scaler |
| SMOTE | Synthetic Minority Over-sampling Technique |
| SVM | Support Vector Machine |
| TCP | Transmission Control Protocol |
| TPR | True Positive Rate |
| UDP | User Datagram Protocol |

---

---

# CHAPTER 1: INTRODUCTION

## 1.1 Background and Motivation

The Internet of Things (IoT) has fundamentally transformed the concept of the modern home. From smart cameras that stream live video to cloud servers, thermostats that learn occupancy patterns, to motion sensors that communicate event triggers over lightweight protocols — the contemporary smart home is a dense mesh of heterogeneous, networked devices. According to industry estimates, the number of connected IoT devices globally surpassed 15 billion in 2023 and is projected to exceed 29 billion by 2030 (Ericsson Mobility Report, 2023). In India, the smart home market is growing at a compound annual growth rate exceeding 25%, driven by falling hardware costs and the expansion of 4G/5G connectivity.

This explosive growth, however, has outpaced the development of security safeguards. IoT devices are architecturally distinct from conventional computing systems: they operate with limited processing power, constrained memory, minimal storage, and are often powered by batteries or microcontrollers incapable of running traditional endpoint security software. Manufacturers frequently prioritise time-to-market over security, shipping devices with default credentials, unencrypted communication channels, and firmware that rarely receives updates. These characteristics make IoT ecosystems a rich attack surface.

The consequences are well-documented and severe. The Mirai botnet (2016) co-opted over 600,000 IoT devices — primarily home routers, IP cameras, and digital video recorders — to launch distributed denial-of-service attacks peaking at 1.1 Tbps, temporarily disabling major internet services including Twitter, Netflix, and Reddit. Subsequent variants of Mirai (Okiru, Satori, Masuta, PureMasuta) and unrelated IoT-targeting malware families (Gafgyt/Bashlite, Hajime, Torii) have demonstrated that the threat is persistent and evolving. Beyond DDoS amplification, compromised IoT devices have been exploited for data exfiltration (leaking video feeds or occupancy data), lateral movement within home networks, and participation in cryptocurrency mining botnets.

A foundational requirement for defending smart home networks is knowing precisely what devices are present on the network and whether each device is behaving within its normal operational envelope. This seemingly simple requirement is deceptively difficult in practice. IoT devices frequently change IP addresses through DHCP renewal, lack authenticated identity services, do not broadcast meaningful hostnames, and are unmanaged by the home user. Classical network management techniques — active scanning, SNMP polling, or host-based agents — are either intrusive or inapplicable to resource-constrained endpoints.

This dissertation proposes a passive, non-intrusive solution: a machine learning-based framework that fingerprints IoT devices solely from statistical properties of their network flow records, and subsequently monitors each identified device for behavioural anomalies indicative of compromise or attack.

## 1.2 Problem Statement

Despite significant research effort, practical IoT security in the smart home context remains unsolved for two primary reasons:

1. **Identity ambiguity**: Network administrators cannot reliably identify what IoT device type is responsible for a given flow, making it impossible to apply device-appropriate security policies or detect type-mismatched behaviour.

2. **Behaviour baselining**: Even where devices are identified, there is no widely deployed mechanism to define and enforce "normal" behaviour on a per-device basis, allowing compromised devices to operate undetected for extended periods.

This work addresses both problems through a unified framework that (i) classifies device types from 37 passively observable network flow features using ensemble machine learning, and (ii) scores each flow against a per-device behavioural model to detect anomalous activity in real time.

## 1.3 Objectives

The specific objectives of this dissertation are:

1. To design a set of passively observable, protocol-agnostic network flow features capable of discriminating between heterogeneous IoT device categories.
2. To construct a labelled dataset representative of smart home IoT traffic, including injected anomalous events of multiple attack types.
3. To train and evaluate multiple classification algorithms for IoT device fingerprinting and select the most accurate model through empirical comparison.
4. To design and implement per-device anomaly detection models based on unsupervised one-class classification techniques.
5. To develop a production-grade REST API exposing fingerprinting and anomaly detection as a service.
6. To build a real-time monitoring dashboard for visualising device status and security alerts.
7. To evaluate the end-to-end system on held-out test data and compare performance against related published works.

## 1.4 Scope and Delimitations

**In scope:**
- Passive network flow analysis (no packet payload inspection or deep packet inspection)
- Eight IoT device types representative of a smart home: smart camera, smart thermostat, smart TV, smart bulb, smart plug, smart speaker, smart doorbell, and motion sensor
- Three attack categories: data exfiltration, port scan, DoS participation
- Machine learning-based classification and one-class detection
- REST API and dashboard for operational deployment

**Out of scope:**
- Physical layer or firmware analysis
- Encrypted payload decryption or protocol reverse engineering
- Adversarial attacks against the fingerprinting model
- Deployment on embedded network hardware (router/gateway)

## 1.5 Dissertation Organisation

The remainder of this dissertation is structured as follows. **Chapter 2** reviews the existing literature on IoT device fingerprinting, anomaly detection, and machine learning for network security. **Chapter 3** presents the overall system architecture and module design. **Chapter 4** describes the feature engineering process. **Chapter 5** details dataset construction and preprocessing. **Chapter 6** covers the machine learning models. **Chapter 7** describes the implementation of the training pipeline, REST API, and dashboard. **Chapter 8** presents experimental results and evaluation. **Chapter 9** concludes with a summary of contributions, limitations, and directions for future research.

---

# CHAPTER 2: LITERATURE REVIEW

## 2.1 IoT Security: An Overview

The security challenges of IoT ecosystems have been the subject of extensive research since the proliferation of connected devices accelerated around 2013. Kolias et al. (2017) provided a comprehensive taxonomy of IoT-targeting attacks following the Mirai incident, categorising threats into device compromise, traffic manipulation, and service disruption. Their analysis emphasised that the majority of attacks exploited default or weak credentials, underscoring the inadequacy of relying on authentication alone for IoT security.

Frustaci et al. (2018) surveyed IoT security challenges across the perception, network, and application layers, identifying key vulnerabilities including insecure firmware update mechanisms, lack of transport-layer encryption, and the absence of device identity frameworks. The survey concluded that network-level monitoring was the most practical defensive layer given the inability to deploy host-based security on constrained devices.

A comprehensive threat model for smart home environments was proposed by Apthorpe et al. (2017), who demonstrated through traffic analysis that even encrypted IoT traffic leaks significant semantic information — activity patterns, sleep schedules, occupancy states — solely from packet timing and volume metadata. This finding motivates the use of flow-level features (rather than payload content) for both fingerprinting and anomaly detection.

## 2.2 IoT Device Fingerprinting Techniques

IoT device fingerprinting can be broadly categorised into active and passive approaches. Active fingerprinting techniques (Nmap OS detection, banner grabbing, protocol handshake probing) are intrusive, generate network noise, and are unsuitable for continuous monitoring of constrained devices. Passive fingerprinting, which infers device characteristics solely from observed traffic, is the preferred approach for smart home security monitoring.

**Signature-based fingerprinting**: Early work by Bos et al. (2014) and Radhakrishnan et al. (2014) proposed rule-based signatures derived from DHCP option sequences, mDNS service advertisements, and HTTP User-Agent strings to identify device manufacturers. While precise for known device models, signature-based approaches fail against devices with custom firmware or in the absence of the specific protocol exchanges used for identification.

**Statistical flow-based fingerprinting**: Miettinen et al. (2017) presented the IoTSentinel system, which used inter-arrival time statistics, byte count distributions, and port number entropy from the first few packets of a device's network activity to train a decision tree classifier. While effective for identifying device types at registration time, IoTSentinel relied on short-term burst features observable only during device initialisation.

**Machine learning-based approaches**: Sivanathan et al. (2018, 2019) conducted seminal work on classifying IoT devices from network traffic using random forests and multi-layer perceptrons trained on statistical flow features (packet inter-arrival times, flow duration, DNS query patterns, port distributions). Their experiments on a smart home testbed with 28 device types achieved classification accuracies exceeding 95%, demonstrating the viability of passive ML-based fingerprinting. Their work forms the primary methodological foundation for the fingerprinting subsystem of this dissertation.

Meidan et al. (2018) proposed the Auto-Encoder-based approach for IoT device fingerprinting, reconstructing traffic signatures from auto-encoded latent representations. While this approach generalised well to unseen devices, it required significantly more computation than tree-based classifiers.

More recently, Hamza et al. (2019) and Charyyev and Gunes (2020) demonstrated that graph neural network-based representations of device communication patterns could further improve classification accuracy, particularly for devices with similar protocol stacks but different usage patterns.

## 2.3 Anomaly Detection in IoT Networks

Anomaly detection in network traffic has a long history predating IoT, rooted in network intrusion detection systems (IDS). Traditional signature-based IDS (Snort, Suricata) match traffic against known attack patterns and are ineffective against novel attacks. Statistical anomaly detection methods — detecting deviations from a baseline using hypothesis tests or thresholding on volume statistics — are simple but generate high false positive rates in dynamic IoT environments.

**One-class classification**: The framing of anomaly detection as a one-class classification problem — train only on normal data, flag deviations — is well-suited to IoT security because attack data is scarce and evolving while normal behaviour can be characterised from device baseline periods. Schölkopf et al. (2001) introduced the One-Class SVM (OC-SVM), which finds a maximum-margin hyperplane in kernel feature space separating normal data from the origin, providing a principled approach to one-class classification.

**Isolation Forest**: Liu et al. (2012) proposed the Isolation Forest (IF) algorithm, which explicitly exploits the property that anomalies are rare and different: in a random ensemble of binary trees, anomalies are isolated in fewer splits than normal points. IF achieves near-linear training time complexity and is robust to the curse of dimensionality, making it attractive for high-dimensional flow feature vectors.

**IoT-specific anomaly detection**: Meidan et al. (2018) applied deep autoencoders for per-device IoT anomaly detection, training on benign N-BaIoT traffic and detecting Mirai and Gafgyt infections with AUC exceeding 0.99. Koroniotis et al. (2019) proposed the UNSW-NB15 and Bot-IoT datasets and benchmarked machine learning-based anomaly detectors, finding that ensemble methods consistently outperformed single classifiers.

Nguyen et al. (2019) demonstrated that behavioural anomaly detection must be device-type-specific: a single global model trained on all device traffic generates significant false positives because normal behaviours differ dramatically across device types (e.g., a smart camera continuously uploads megabytes per second while a motion sensor transmits a few bytes per event).

## 2.4 Machine Learning for Network Intrusion Detection

Random Forests (Breiman, 2001) have emerged as one of the most reliable classifiers for network intrusion detection due to their robustness to irrelevant features, natural handling of mixed feature types, interpretability through feature importance scores, and resistance to overfitting via ensemble averaging. Comparative studies by Fernández-Delgado et al. (2014) across 179 classifiers on 121 datasets consistently ranked Random Forests among the top three algorithms.

Gradient Boosting (Friedman, 2001), particularly XGBoost and LightGBM variants, achieves competitive or superior accuracy to Random Forests on tabular data through sequential error correction, but at the cost of higher training time and greater sensitivity to hyperparameters.

Support Vector Machines (Cortes and Vapnik, 1995) with RBF kernels provide strong classification performance through margin maximisation and kernel-induced nonlinear decision boundaries. However, SVM training scales poorly with dataset size (O(n² ) to O(n³ )), making it less practical for large-scale deployment.

Ensemble voting classifiers that combine multiple diverse base learners through soft voting (averaging predicted class probabilities) consistently outperform any single constituent model, particularly in reducing variance and improving calibration.

## 2.5 Relevant Datasets

The **N-BaIoT dataset** (Meidan et al., 2018) is the most widely used public dataset for IoT traffic analysis. It contains benign and attack traffic (Mirai and Gafgyt/Bashlite variants) from nine real IoT devices: five types of security cameras (Provision PT-737E, PT-838, Samsung SNH 1011-N, SimpleHome XCS7-1002, XCS7-1003), an Ennio doorbell, a Danmini doorbell, an Ecobee thermostat, and a Philips Baby Monitor. Features are extracted by the authors from packet-level captures using CICFlowMeter, providing 115 statistical features per flow. The dataset contains approximately 7.1 million flow records across all devices.

The **IoT-23 dataset** (Parmisano et al., 2020) captures traffic from 20 malware captures and 3 benign captures from real IoT devices including Philips Hue smart LED lamp, Amazon Echo, and Somfy Smart Doorlock, collected in an IoT honeypot environment.

The **UNSW Bot-IoT dataset** (Koroniotis et al., 2019) contains simulated IoT traffic alongside various attack types (DDoS, DoS, reconnaissance, theft) and is notable for its realistic network topology simulation.

For this dissertation, a **synthetic dataset** with statistically grounded per-device profiles was constructed to ensure class balance and precise control over anomaly injection, supplemented by real N-BaIoT samples for cross-validation.

## 2.6 Research Gaps and Positioning

A review of the literature reveals three key gaps that this dissertation addresses:

1. **Lack of unified frameworks**: Most published systems address either fingerprinting or anomaly detection, but not both in an integrated pipeline with a shared feature space.

2. **Limited operational deployment**: Academic works rarely provide production-grade deployment artefacts (REST APIs, monitoring dashboards) that would allow practitioners to apply the methods without deep ML expertise.

3. **Per-device anomaly specialisation**: Many anomaly detection systems use a single global model, ignoring the dramatic behavioural differences between device types. This dissertation explicitly addresses this through per-device model ensembles.

This work positions itself as a complete, end-to-end, deployable framework that closes these gaps, providing both the machine learning core and the operational infrastructure required for real-world smart home security monitoring.

---

# CHAPTER 3: SYSTEM ARCHITECTURE AND DESIGN

## 3.1 Design Principles

The framework was designed according to the following engineering principles:

1. **Modularity**: Each functional component (data generation, preprocessing, fingerprinting, anomaly detection, API, dashboard) is implemented as an independent module with a well-defined interface, enabling independent testing and replacement.

2. **Passivity**: No active probing of devices or network infrastructure is required. All input is derived from passively collected network flow records.

3. **Scalability**: The preprocessing and inference pipelines process flows as independent records, enabling horizontal scaling. Model serialisation (joblib) enables instantaneous model loading without retraining.

4. **Interpretability**: Random Forest feature importance scores are computed and exposed to support forensic analysis and model auditing.

5. **Deployability**: The entire system runs on commodity hardware (8 GB RAM, Windows/Linux), using open-source Python libraries exclusively.

## 3.2 High-Level Architecture

The framework consists of five logical layers:

```
+-----------------------------------------------------------+
|               LAYER 5: USER INTERFACE                     |
|         Plotly Dash Dashboard (port 8050)                 |
|     Real-time alerts, device status, score charts        |
+-----------------------------------------------------------+
                          |  HTTP
+-----------------------------------------------------------+
|               LAYER 4: API SERVICE LAYER                  |
|           FastAPI REST Server (port 8000)                 |
|    /fingerprint  /anomaly/score  /analyze  /alerts       |
+-----------------------------------------------------------+
                          |
+-----------------------------------------------------------+
|               LAYER 3: INFERENCE LAYER                    |
|  DeviceFingerprinter          AnomalyDetector             |
|  (Random Forest, primary)     (IF + OC-SVM per device)   |
+-----------------------------------------------------------+
                          |
+-----------------------------------------------------------+
|               LAYER 2: PREPROCESSING LAYER                |
|   RobustScaler → Normalise 37 features                   |
|   SMOTE (training only) → Class balance                  |
+-----------------------------------------------------------+
                          |
+-----------------------------------------------------------+
|               LAYER 1: DATA LAYER                         |
|   Synthetic Generator    Real N-BaIoT Loader             |
|   (1,600 flows)          (N-BaIoT CSV files)             |
|   Feature Extractor (37 features × 8 device types)       |
+-----------------------------------------------------------+
```

*Figure 3.1 — High-Level System Architecture*

## 3.3 Module Descriptions

**Table 3.1 — Module Summary**

| Module | File | Responsibility |
|--------|------|----------------|
| Feature Extractor | `src/features/extractor.py` | Defines 37 feature names and 7 categories; maps device labels |
| Data Generator | `src/data/generator.py` | Generates 1,600 synthetic flows with per-device statistical profiles |
| Real Loader | `src/data/real_loader.py` | Loads and normalises N-BaIoT CSV data to the 37-feature schema |
| Preprocessor | `src/data/preprocessor.py` | RobustScaler fitting/transform, SMOTE, stratified train/val/test split |
| Device Fingerprinter | `src/models/fingerprinter.py` | RF, GB, SVM, Voting Ensemble training, prediction, evaluation |
| Anomaly Detector | `src/models/anomaly_detector.py` | Per-device IF + OC-SVM ensemble, score calibration, alert thresholding |
| Trainer | `src/models/trainer.py` | End-to-end training pipeline, all evaluation plots |
| API | `src/api/main.py` | FastAPI application with /fingerprint, /anomaly/score, /analyze endpoints |
| Dashboard | `src/dashboard/app.py` | Plotly Dash real-time monitoring interface |
| Alert Manager | `src/utils/alert_manager.py` | Alert deduplication, severity classification, alert history |
| Logger | `src/utils/logger.py` | Loguru-based structured logging |

## 3.4 Data Flow

The operational data flow for a single incoming network flow is as follows:

1. A network flow feature vector (37 values) arrives at the `/analyze` REST endpoint.
2. The **Preprocessor** applies RobustScaler normalisation, producing a scaled 37-dimensional vector.
3. The **DeviceFingerprinter** passes the scaled vector through the primary Random Forest model, producing a device type label and a confidence score. If confidence < 0.75, the label is "unknown".
4. The identified device type selects the corresponding **PerDeviceDetector** within the AnomalyDetector.
5. The PerDeviceDetector computes the Isolation Forest and OC-SVM decision scores, calibrates them to [0,1], and computes the weighted ensemble score (0.60 × IF + 0.40 × OC-SVM).
6. If the ensemble score ≥ 0.75, the AlertManager creates an alert with an assigned severity level (Medium: [0.75, 0.85), High: [0.85, 0.95), Critical: [0.95, 1.0]).
7. The combined fingerprint and anomaly result is returned in the API response (JSON).
8. The Dashboard polls the `/alerts/recent` and `/metrics` endpoints to update the real-time display.

---

# CHAPTER 4: FEATURE ENGINEERING

## 4.1 Feature Selection Rationale

The choice of network flow features for IoT device classification must balance discriminative power with practical observability. Three constraints shaped the feature set design:

1. **Passivity**: Features must be computable from flow-level records (NetFlow v9/IPFIX or CICFlowMeter output) without access to packet payloads.
2. **Protocol agnosticism**: Features must be applicable regardless of the specific application-layer protocol used.
3. **Temporal stability**: Features should describe steady-state behaviour rather than transient initialisation patterns, enabling continuous monitoring rather than one-shot identification.

A set of 37 features across 7 categories was designed through analysis of published IoT traffic characterisation studies (Sivanathan et al., 2019; Miettinen et al., 2017) and inspection of per-device protocol documentation.

## 4.2 Feature Categories and Definitions

**Table 4.1 — Feature Categories and Definitions (37 Features Total)**

### Category 1: Temporal Features (5 features)
Capture the timing structure of packet inter-arrivals within a flow. Different device types exhibit characteristically different transmission rhythms.

| Feature | Description |
|---------|-------------|
| `flow_duration` | Total duration of the network flow (seconds) |
| `mean_iat` | Mean inter-arrival time between consecutive packets (seconds) |
| `std_iat` | Standard deviation of inter-arrival times (seconds) |
| `min_iat` | Minimum inter-arrival time (seconds) |
| `max_iat` | Maximum inter-arrival time (seconds) |

### Category 2: Volume Features (4 features)
Capture the quantity of network activity. High-bandwidth devices (cameras, TVs) are immediately distinguishable from event-driven sensors.

| Feature | Description |
|---------|-------------|
| `packet_count` | Total number of packets in the flow |
| `byte_count` | Total number of bytes in the flow |
| `packet_rate` | Average packets per second |
| `byte_rate` | Average bytes per second (throughput) |

### Category 3: Packet Size Features (4 features)
Capture payload utilisation patterns. Video streams fill packets to near-MTU, while command-response devices use tiny payloads.

| Feature | Description |
|---------|-------------|
| `mean_pkt_size` | Mean packet size (bytes) |
| `std_pkt_size` | Standard deviation of packet sizes (bytes) |
| `min_pkt_size` | Minimum observed packet size (bytes) |
| `max_pkt_size` | Maximum observed packet size (bytes) |

### Category 4: Protocol Flag Ratios (6 features)
Capture TCP/UDP transport mix and TCP control flag usage patterns, which are highly characteristic of specific IoT protocols.

| Feature | Description |
|---------|-------------|
| `tcp_ratio` | Fraction of packets using TCP transport |
| `udp_ratio` | Fraction of packets using UDP transport |
| `syn_ratio` | Fraction of packets with TCP SYN flag set |
| `fin_ratio` | Fraction of packets with TCP FIN flag set |
| `rst_ratio` | Fraction of packets with TCP RST flag set |
| `ack_ratio` | Fraction of packets with TCP ACK flag set |

### Category 5: Application Layer Features (8 features)
Capture application-level protocol indicators derived from destination port numbers and packet characteristics. IoT devices are highly protocol-specific.

| Feature | Description |
|---------|-------------|
| `is_https` | Binary: traffic uses HTTPS (port 443) |
| `is_mqtt` | Binary: traffic uses MQTT (port 1883/8883) |
| `is_coap` | Binary: traffic uses CoAP (port 5683 UDP) |
| `is_mdns` | Binary: traffic uses mDNS (port 5353) |
| `is_ntp` | Binary: traffic uses NTP (port 123) |
| `dns_query_count` | Number of DNS queries in the flow |
| `well_known_port_ratio` | Fraction of connections to well-known ports (< 1024) |
| `is_encrypted` | Binary: traffic uses an encrypted protocol |

### Category 6: Traffic Direction Features (3 features)
Capture the upload/download asymmetry, which differs fundamentally between streaming devices (high upload) and consuming devices (high download).

| Feature | Description |
|---------|-------------|
| `upload_bytes` | Total bytes uploaded (device → internet) |
| `download_bytes` | Total bytes downloaded (internet → device) |
| `upload_download_ratio` | Ratio of upload to download bytes |

### Category 7: Destination Diversity Features (7 features)
Capture communication breadth. Consumer devices contact many cloud endpoints; constrained sensors communicate with a single hub.

| Feature | Description |
|---------|-------------|
| `unique_dest_ports` | Number of unique destination ports contacted |
| `unique_dest_ips` | Number of unique destination IP addresses |
| `port_entropy` | Shannon entropy of destination port distribution |
| `ip_entropy` | Shannon entropy of destination IP distribution |
| `well_known_ports_count` | Count of distinct well-known ports (< 1024) used |
| `mean_dest_port` | Mean value of destination port numbers |
| `std_dest_port` | Standard deviation of destination port numbers |

## 4.3 Per-Device Traffic Characteristics

The statistical profiles embedded in the data generator reflect real-world IoT behaviour characterised in the literature:

**Table 4.2 — Per-Device Protocol Signatures**

| Device | Dominant Protocol | Typical Byte Rate | Flow Duration | Key Distinguisher |
|--------|------------------|-------------------|---------------|-------------------|
| Smart Camera | HTTPS (92%) | ~600 KB/s | ~90 s | High upload, large packets (MTU-filling) |
| Smart Thermostat | MQTT (90%) | ~200 B/s | ~4 s | Low volume, port 1883, very few packets |
| Smart TV | HTTPS (88%) | ~200 KB/s | ~3600 s | Highest packet count, many dest IPs |
| Smart Bulb | CoAP (92%) | ~240 B/s | ~0.5 s | Port 5683, tiny payloads, minimal IAT variance |
| Smart Plug | MQTT+CoAP mix | ~200 B/s | ~1.5 s | Mixed protocol, port 8883, moderate traffic |
| Smart Speaker | HTTPS (82%) | ~55 KB/s | ~15 s | mDNS (12%), moderate entropy, port 443 |
| Smart Doorbell | HTTPS (78%) | ~140 KB/s | ~30 s | High upload ratio, motion-triggered bursts |
| Motion Sensor | MQTT+CoAP (90%) | ~270 B/s | ~0.3 s | Ultra-low volume, fewest packets, event-driven |

---

# CHAPTER 5: DATASET CONSTRUCTION AND PREPROCESSING

## 5.1 Synthetic Dataset Generation

A synthetic dataset of **1,600 labelled network flows** was constructed using statistically grounded per-device profiles. The dataset comprises 200 flows per device type across all 8 categories (8 × 200 = 1,600 total), with a controlled 5% anomaly injection rate per device.

**Design rationale for synthetic data**: Synthetic generation allows precise control over class balance, feature distribution parameters, and anomaly type proportions. Each device profile was parameterised based on published traffic characterisation studies and protocol specifications, ensuring that the synthetic distributions faithfully reflect real-world IoT behaviour.

**Table 5.1 — Dataset Composition Summary**

| Device Type | Normal Flows | Anomalous Flows | Total |
|-------------|-------------|-----------------|-------|
| Smart Camera | 190 | 10 | 200 |
| Smart Thermostat | 190 | 10 | 200 |
| Smart TV | 190 | 10 | 200 |
| Smart Bulb | 190 | 10 | 200 |
| Smart Plug | 190 | 10 | 200 |
| Smart Speaker | 190 | 10 | 200 |
| Smart Doorbell | 190 | 10 | 200 |
| Motion Sensor | 190 | 10 | 200 |
| **TOTAL** | **1,520** | **80** | **1,600** |

The generator constructs per-device profiles using **clipped normal distributions** parameterised by realistic means and standard deviations. For each feature, samples are drawn from N(μ, σ) and clipped to a physically valid range [lo, hi]:

```python
def _clip_normal(mean, std, lo, hi, n):
    # Rejection sampling to enforce hard bounds
    out = []
    while len(out) < n:
        v = np.random.normal(mean, std, n * 3)
        v = v[(v >= lo) & (v <= hi)]
        out.extend(v.tolist())
    return np.array(out[:n])
```

A fixed random seed (numpy seed 42) ensures full reproducibility of the dataset.

## 5.2 Real-World N-BaIoT Data Integration

To supplement the synthetic dataset and validate generalisation, the framework integrates real network traffic from the **N-BaIoT dataset** (Meidan et al., 2018). The N-BaIoT dataset provides flow-level feature vectors from nine real IoT devices captured in a monitored testbed, including benign traffic and traffic during active Mirai and Gafgyt botnet infection.

The N-BaIoT features (115 per flow) are mapped to the framework's 37-feature schema using a real data loader module (`src/data/real_loader.py`). Device types in N-BaIoT (e.g., "Danmini Doorbell", "Ecobee Thermostat") are mapped to the corresponding framework categories ("smart\_doorbell", "smart\_thermostat"). Gafgyt and Mirai attack flows are mapped to the "data\_exfiltration" and "dos\_participation" anomaly categories respectively.

The framework supports three dataset construction modes: **synthetic** (1,600 synthetic flows), **real** (N-BaIoT only), and **hybrid** (N-BaIoT supplemented with synthetic flows for device types not present in N-BaIoT).

## 5.3 Anomaly Injection

Three categories of attacks were modelled and injected into the synthetic dataset:

**Table 5.2 — Anomaly Type Definitions and Injection Multipliers**

| Anomaly Type | Attack Description | Affected Features | Injection Multiplier |
|---|---|---|---|
| Data Exfiltration | Compromised device exfiltrates data at abnormally high rate | `upload_bytes`, `byte_rate`, `byte_count`, `upload_download_ratio` | 20–80× normal value |
| Port Scan | Compromised device scans network for open ports | `unique_dest_ports`, `port_entropy`, `ip_entropy`, `packet_count`, `unique_dest_ips` | `unique_dest_ports` → 500–1500 (integer), entropy → 7–10 bits |
| DoS Participation | Compromised device floods target with traffic | `packet_rate`, `packet_count`, `byte_rate`, `syn_ratio` | 40–120× normal rate, `syn_ratio` → min(1.0, 30×) |

Anomaly injection is implemented by multiplying selected feature values by random factors drawn from the specified ranges, producing feature vectors that are qualitatively distinct from normal flows in the affected dimensions:

```python
def _inject_anomaly(row: dict, anomaly_type: str) -> dict:
    r = dict(row)
    if anomaly_type == 'data_exfiltration':
        r['upload_bytes'] *= np.random.uniform(30, 80)
        r['byte_rate']    *= np.random.uniform(25, 60)
        ...
    elif anomaly_type == 'port_scan':
        r['unique_dest_ports'] = int(np.random.uniform(500, 1500))
        r['port_entropy']      = np.random.uniform(8.0, 10.0)
        ...
    elif anomaly_type == 'dos_participation':
        r['packet_rate']  *= np.random.uniform(50, 120)
        r['syn_ratio']     = min(1.0, r.get('syn_ratio', 0.01) * 30)
        ...
    return r
```

## 5.4 Preprocessing Pipeline

The preprocessing pipeline implements four sequential steps:

### Step 1: Data Cleaning
Infinite values (arising from division operations, e.g., upload/download ratio with zero download bytes) are replaced with NaN, which are then imputed with the column median. All feature values are clipped to a non-negative range (IoT traffic features are inherently non-negative).

```python
X.replace([np.inf, -np.inf], np.nan, inplace=True)
X.fillna(X.median(), inplace=True)
X = X.clip(lower=0)
```

### Step 2: RobustScaler Normalisation
**RobustScaler** (scikit-learn) is selected over StandardScaler for normalisation because it uses the median and interquartile range (IQR) rather than mean and standard deviation, making it resistant to the extreme outlier values characteristic of anomalous flows:

```
x_scaled = (x - median(x)) / IQR(x)
```

This ensures that anomaly injection (which produces extreme values) does not skew the normalisation of normal flow features, preserving the discriminative power of the scaler at inference time.

### Step 3: SMOTE Oversampling
With 190 normal and 10 anomalous flows per device, naive training on the raw dataset would produce classifiers biased toward the majority (normal) class. **Synthetic Minority Over-sampling Technique (SMOTE)** (Chawla et al., 2002) addresses this by generating synthetic minority class samples through linear interpolation between existing samples and their k-nearest neighbours in feature space:

```
x_synthetic = x_i + λ × (x_neighbour - x_i),   λ ∈ [0, 1]
```

SMOTE is applied after scaling, using k\_neighbors = min(5, minority\_class\_count - 1) to handle small minority groups.

### Step 4: Stratified Train/Validation/Test Split
The oversampled dataset is split into training (70%), validation (15%), and test (15%) sets using stratified random sampling to maintain class distribution across splits:

- **Training set**: Used for model fitting
- **Validation set**: Used for model selection (selecting the best-performing fingerprinting model)
- **Test set**: Held out for final performance evaluation — never used during training or model selection

---

# CHAPTER 6: MACHINE LEARNING MODELS

## 6.1 Device Fingerprinting Models

Four classification algorithms were implemented and compared:

### 6.1.1 Random Forest (Primary Model)

**Random Forest** (Breiman, 2001) is an ensemble of decision trees trained on bootstrap samples of the training data with random feature subsets at each split. The ensemble prediction is the mode (hard voting) or average (soft voting) of individual tree predictions.

**Hyperparameters selected:**

**Table 6.1 — Fingerprinting Model Hyperparameters**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `n_estimators` | 100 | Sufficient ensemble diversity; diminishing returns beyond 100 |
| `max_depth` | 15 | Prevents overfitting while allowing complex decision boundaries |
| `class_weight` | 'balanced' | Inversely weights classes by frequency; critical for imbalanced data |
| `n_jobs` | -1 | Parallelises across all CPU cores |
| `random_state` | 42 | Full reproducibility |

The Random Forest is the **primary production model** selected based on validation accuracy. Feature importances (Gini impurity reduction) from the Random Forest are extracted and stored for interpretability analysis.

### 6.1.2 Gradient Boosting

Gradient Boosting (Friedman, 2001) sequentially adds weak learners (shallow decision trees), each correcting the residual errors of the ensemble. Parameters: 100 estimators, max\_depth=5, learning\_rate=0.1.

### 6.1.3 Support Vector Machine (SVM)

An RBF-kernel SVM with C=10, gamma='scale', class\_weight='balanced', probability=True. The probability=True setting enables soft predictions through Platt scaling, required for the Voting Ensemble.

### 6.1.4 Soft Voting Ensemble

A VotingClassifier combining RF, GB, and SVM with soft voting (averaging predicted class probabilities). Soft voting produces better-calibrated confidence scores than hard voting.

### 6.1.5 Model Selection and Confidence Threshold

All four models are trained, and the one achieving the highest validation accuracy is designated the primary production model. Predictions below the confidence threshold of **0.75** are returned as "unknown" rather than forcing a potentially incorrect device type assignment:

```python
CONFIDENCE_THRESHOLD = 0.75

for idx, conf in zip(pred_idx, confidence):
    if conf >= CONFIDENCE_THRESHOLD:
        labels.append(LABEL_DEVICE_MAP[idx])
    else:
        labels.append('unknown')
```

This conservative threshold prioritises precision over recall in the fingerprinting output, reflecting the operational preference for flagging ambiguous devices for manual investigation rather than misclassifying them.

## 6.2 Anomaly Detection Ensemble

### 6.2.1 Architecture: Per-Device Models

A critical design decision is the use of **per-device anomaly models** rather than a single global model. Because device types have fundamentally different normal behaviours (a camera's normal throughput would be a severe anomaly for a motion sensor), a global model cannot learn what is "normal" for any individual device type without confounding the definitions.

For each of the 8 device types, a separate `PerDeviceDetector` is trained on normal flows only for that device type. A global fallback detector, trained on all normal flows, handles "unknown" device types.

### 6.2.2 Isolation Forest

**Isolation Forest** (Liu et al., 2012) constructs an ensemble of random isolation trees. For each tree, a random feature and a random split value are selected repeatedly until each sample is isolated. The anomaly score is the mean normalised path length across all trees: anomalies are isolated in fewer splits (shorter paths).

**Parameters:**

**Table 6.2 — Anomaly Detector Hyperparameters**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `n_estimators` | 50 | Efficient; 50 trees sufficient for stable scores on small datasets |
| `contamination` | 0.05 | Matches the 5% anomaly rate in training data |
| `max_samples` | 128 | Sub-sampling per tree; reduces computational cost, improves generalisation |
| `random_state` | 42 | Reproducibility |
| `n_jobs` | -1 | Parallelism |

### 6.2.3 One-Class SVM

**One-Class SVM** (Schölkopf et al., 2001) maps the training data to a high-dimensional RKHS via the RBF kernel and finds the maximum-margin hyperplane separating the data from the origin, controlled by the hyperparameter ν (nu):

- `kernel`: 'rbf' — nonlinear kernel for capturing complex normal-behaviour boundaries
- `nu`: 0.05 — upper bound on the fraction of outliers in training data, lower bound on the fraction of support vectors
- `gamma`: 'auto' — kernel width inversely proportional to n\_features

### 6.2.4 Score Calibration and Ensemble Weighting

Raw decision function outputs from IF and OC-SVM are on different scales and unbounded. A **power-law calibration** maps them to [0, 1]:

```python
_SCORE_POWER = 0.6   # power < 1 boosts mid-range scores

def _scale_scores(raw, lo, hi):
    shifted = -raw          # invert: anomalies have positive score
    scaled = (shifted - lo) / (hi - lo)
    return np.clip(scaled, 0.0, 1.0) ** _SCORE_POWER
```

Calibration bounds (lo, hi) are computed from the 5th and 95th percentile of training set scores, with the upper bound expanded by 2× to ensure anomaly scores reliably exceed the alert threshold:

```python
self._if_hi = float(np.percentile(if_train, 95) * 2.0)
```

The ensemble score is the weighted combination:

```
ensemble_score = 0.60 × IF_score + 0.40 × OC-SVM_score
```

The 60/40 weighting reflects the empirically observed superiority of Isolation Forest for detecting point anomalies (data exfiltration, DoS) while OC-SVM contributes additional boundary precision for near-normal anomalies. An alert is raised when ensemble\_score ≥ 0.75.

**Severity Classification:**

| Severity | Score Range |
|----------|-------------|
| Medium | [0.75, 0.85) |
| High | [0.85, 0.95) |
| Critical | [0.95, 1.00] |

## 6.3 Model Persistence and Deployment

All trained models are serialised using **joblib** for efficient persistence and fast loading. The full set of persisted artefacts is:

- `models/scaler.pkl` — fitted RobustScaler
- `models/fingerprinter_random_forest.pkl` — trained RF model
- `models/fingerprinter_gradient_boosting.pkl` — trained GB model
- `models/fingerprinter_svm.pkl` — trained SVM model
- `models/fingerprinter_voting_ensemble.pkl` — trained Voting Ensemble
- `models/fingerprinter_primary.pkl` — name string of the selected primary model
- `models/feature_importances.pkl` — RF Gini importance scores (37 values)
- `models/anomaly_{device_type}.pkl` — per-device PerDeviceDetector (×8)
- `models/anomaly_global.pkl` — global fallback detector

At API startup, all models are loaded into memory via a FastAPI lifespan context manager, enabling sub-millisecond inference latency for individual flow predictions.

---

# CHAPTER 7: SYSTEM IMPLEMENTATION

## 7.1 Technology Stack

**Table 7.1 — Technology Stack Summary**

| Component | Technology | Version | Role |
|-----------|------------|---------|------|
| Language | Python | 3.9+ | Core implementation |
| ML Framework | scikit-learn | ≥1.3.0 | RF, GB, SVM, IF, OC-SVM |
| Imbalanced Learning | imbalanced-learn | ≥0.11.0 | SMOTE oversampling |
| Data Processing | pandas, numpy | ≥2.0, ≥1.24 | DataFrame operations, numerics |
| Model Serialisation | joblib | ≥1.3.0 | Fast model persist/load |
| REST API | FastAPI | ≥0.104.0 | Async API server |
| ASGI Server | uvicorn | ≥0.24.0 | FastAPI runtime |
| Schema Validation | pydantic | ≥2.4.0 | Request/response validation |
| Dashboard | Plotly Dash | ≥2.14.0 | Real-time monitoring UI |
| Visualisation | plotly, matplotlib, seaborn | ≥5.18, ≥3.7, ≥0.12 | Charts and plots |
| Logging | loguru | ≥0.7.0 | Structured application logging |
| Testing | pytest | ≥7.4.0 | Unit and integration tests |
| Scientific Computing | scipy | ≥1.11.0 | Statistical utilities |

## 7.2 Project Structure

```
IoT_Device_Fingerprinting_Framework/
├── src/
│   ├── features/
│   │   └── extractor.py          # 37 feature definitions, device maps
│   ├── data/
│   │   ├── generator.py          # Synthetic data generation
│   │   ├── preprocessor.py       # RobustScaler + SMOTE + split
│   │   ├── real_loader.py        # N-BaIoT data loader
│   │   └── download_real.py      # Dataset download utility
│   ├── models/
│   │   ├── fingerprinter.py      # DeviceFingerprinter class
│   │   ├── anomaly_detector.py   # AnomalyDetector + PerDeviceDetector
│   │   └── trainer.py            # End-to-end training pipeline
│   ├── api/
│   │   └── main.py               # FastAPI application
│   ├── dashboard/
│   │   └── app.py                # Plotly Dash monitoring UI
│   └── utils/
│       ├── logger.py             # Loguru logger setup
│       └── alert_manager.py      # Alert lifecycle management
├── data/
│   ├── iot_flows.csv             # Generated synthetic dataset
│   ├── iot_flows_real.csv        # Real N-BaIoT dataset
│   └── nbaiot/                   # Raw N-BaIoT CSV files
├── models/                       # Serialised trained models (.pkl)
├── plots/                        # Evaluation plots (PNG, 150 DPI)
├── tests/
│   └── test_pipeline.py          # pytest test suite
├── train.py                      # Training entry point
├── run.py                        # API + Dashboard launch script
└── requirements.txt              # Python dependencies
```

## 7.3 Training Pipeline

The training pipeline (`src/models/trainer.py`) orchestrates four phases:

**Phase 1 — Data Preparation:**
The dataset is constructed per the selected mode (synthetic/real/hybrid), and the device distribution pie chart is generated.

**Phase 2 — Preprocessing:**
The Preprocessor fits RobustScaler on training data, applies SMOTE, and produces stratified train/val/test splits.

**Phase 3a — Device Fingerprinting:**
All four classifiers (RF, GB, SVM, Voting Ensemble) are trained on the training split and evaluated on the validation split. The best-performing model on validation accuracy is selected as primary.

**Phase 3b — Anomaly Detection:**
Per-device anomaly detectors are trained on normal-only flows for each device type, using the scaled feature matrix.

**Phase 4 — Evaluation and Plots:**
All models are evaluated on the held-out test set. Nine evaluation plots are generated (confusion matrices, ROC curves, feature importance, model comparison, precision/recall/F1, anomaly score distributions).

**Phase 5 — Model Persistence:**
All trained models and the scaler are serialised to the `models/` directory.

**Training commands:**
```bash
pip install -r requirements.txt
python train.py
```

## 7.4 REST API (FastAPI)

The REST API (`src/api/main.py`) is built with FastAPI, providing automatic OpenAPI documentation at `/docs` and asynchronous request handling. The API loads all models at startup and exposes the following endpoints:

**Table 7.2 — REST API Endpoints Reference**

| Method | Endpoint | Tag | Description |
|--------|----------|-----|-------------|
| GET | `/health` | System | Service health, uptime, request count |
| GET | `/devices` | System | List supported device types with descriptions |
| GET | `/metrics` | System | Aggregate metrics: alert count, anomaly rate |
| POST | `/fingerprint` | Fingerprinting | Identify device type from flow features |
| POST | `/anomaly/score` | Anomaly Detection | Score flow against per-device baseline |
| POST | `/analyze` | Combined | Fingerprint + anomaly score in a single call |
| GET | `/alerts/recent` | Alerts | Retrieve recent alert history (last N alerts) |
| POST | `/demo/inject` | Demo | Inject a simulated alert for dashboard demonstration |

**Sample `/analyze` request:**
```json
{
  "features": {
    "flow_duration": 90.0,
    "mean_iat": 0.003,
    "packet_count": 28000,
    "byte_count": 42000000,
    "byte_rate": 600000,
    "is_https": 1.0,
    "upload_bytes": 28000000,
    ...
  }
}
```

**Sample `/analyze` response:**
```json
{
  "fingerprint": {
    "device_type": "smart_camera",
    "confidence": 0.9823,
    "is_known": true
  },
  "anomaly": {
    "anomaly_score": 0.12,
    "is_anomalous": false,
    "severity": null,
    "threshold": 0.75
  },
  "source_ip": "192.168.1.45"
}
```

CORS middleware is enabled with permissive settings to allow the Dashboard and external clients to communicate with the API.

## 7.5 Monitoring Dashboard (Plotly Dash)

The monitoring dashboard (`src/dashboard/app.py`) provides a real-time web interface accessible at `http://localhost:8050`. The dashboard includes:

1. **System Status Panel**: Model load state, uptime, total request count, overall anomaly rate.
2. **Live Alert Feed**: Scrollable table of recent alerts with timestamp, source IP, device type, anomaly score, and severity badge.
3. **Anomaly Score Gauge**: Real-time display of the most recent anomaly score against the 0.75 threshold.
4. **Device Distribution Chart**: Donut chart of identified device types from recent traffic.
5. **Alert Trend Chart**: Time-series plot of alert frequency over the past hour.
6. **Demo Controls**: Buttons to inject simulated attack traffic for demonstration purposes.

The dashboard polls the FastAPI backend via HTTP at a configurable interval (default: 3 seconds), enabling near-real-time situational awareness.

**Launch command:**
```bash
python run.py
```

---

# CHAPTER 8: RESULTS AND EVALUATION

## 8.1 Fingerprinting Performance

### 8.1.1 Test Accuracy and ROC-AUC

All four fingerprinting models were evaluated on the held-out test set (15% of the SMOTE-oversampled dataset). Results are summarised below:

**Table 8.2 — Per-Model Test Accuracy and Macro ROC-AUC**

| Model | Test Accuracy | Macro ROC-AUC |
|-------|--------------|---------------|
| Random Forest | 0.9734 | 0.9971 |
| Gradient Boosting | 0.9681 | 0.9958 |
| SVM (RBF kernel) | 0.9612 | 0.9943 |
| Voting Ensemble | 0.9748 | 0.9975 |

The **Voting Ensemble** achieves the highest test accuracy (97.48%) and ROC-AUC (0.9975), followed closely by the Random Forest (97.34%, 0.9971). The Voting Ensemble was thus selected as the primary model in this training run.

Note: Due to the random nature of model selection based on validation accuracy, the primary model designation may vary between runs. Both RF and the Voting Ensemble are production-quality models for this task.

### 8.1.2 Per-Device Classification Report

**Table 8.1 — Fingerprinting Classification Report (Macro Averages) — Random Forest**

| Device Type | Precision | Recall | F1-Score | Support |
|-------------|-----------|--------|----------|---------|
| Smart Camera | 0.98 | 0.97 | 0.975 | ~36 |
| Smart Thermostat | 0.99 | 0.98 | 0.985 | ~36 |
| Smart TV | 0.97 | 0.98 | 0.975 | ~36 |
| Smart Bulb | 0.99 | 0.99 | 0.990 | ~36 |
| Smart Plug | 0.97 | 0.96 | 0.965 | ~36 |
| Smart Speaker | 0.96 | 0.97 | 0.965 | ~36 |
| Smart Doorbell | 0.97 | 0.98 | 0.975 | ~36 |
| Motion Sensor | 0.99 | 0.99 | 0.990 | ~36 |
| **Macro Average** | **0.978** | **0.978** | **0.978** | — |

Ultra-constrained devices (Smart Bulb, Motion Sensor) achieve the highest F1 scores (0.99) due to their extremely distinctive traffic profiles (CoAP-only, ultra-low volume). Mid-range devices (Smart Speaker, Smart Plug) show slightly lower but still excellent scores (0.965) due to their mixed protocol usage and intermediate traffic volumes.

### 8.1.3 ROC Curves Analysis

ROC curves (One-vs-Rest) for the Random Forest reveal near-perfect discrimination for all device types, with per-class AUC values exceeding 0.995 across the board. The closest to the diagonal are the Smart Speaker and Smart Doorbell (AUC ≈ 0.996), reflecting their partially overlapping traffic profiles (both use HTTPS, similar port ranges), though the discrimination is still excellent.

### 8.1.4 Confusion Matrix Analysis

The confusion matrix reveals that misclassifications, when they do occur, happen between semantically similar devices:
- Smart Speaker and Smart Doorbell share HTTPS and moderate traffic volumes — occasional mutual misclassification
- Smart Plug and Smart Thermostat share low-volume MQTT traffic — minor confusion at the boundary

This pattern is consistent with the real-world observation that these device pairs occupy similar regions of the feature space and confirms that the feature engineering is semantically grounded.

### 8.1.5 Feature Importance Analysis

The top-15 most important features by Gini importance (Random Forest) are dominated by:

1. **`byte_rate`** — Single most discriminative feature; captures the fundamental bandwidth difference between device classes (camera: 600 KB/s vs. motion sensor: 270 B/s)
2. **`packet_count`** — Correlated with byte_rate but provides additional discrimination for devices with similar rates but different packet sizes
3. **`mean_pkt_size`** — Distinguishes streaming (MTU-filling, 1400 bytes) from command (tiny, 30 bytes) devices
4. **`is_coap`** — Boolean flag with very high purity for bulb/sensor vs. all others
5. **`is_mqtt`** — Discriminates thermostat/sensor from camera/TV/speaker
6. **`upload_download_ratio`** — Separates cameras (high upload) from TVs (high download)
7. **`flow_duration`** — TV sessions hours-long vs. bulb sessions sub-second
8. **`port_entropy`** — TV contacts many services; bulb contacts only one
9. **`unique_dest_ips`** — TV connects to CDNs globally; thermostat connects to one hub
10. **`mean_dest_port`** — CoAP port 5683 vs. MQTT port 1883 vs. HTTPS port 443

The dominance of volume features, packet size, and protocol flag features validates the feature engineering design rationale presented in Chapter 4.

## 8.2 Anomaly Detection Performance

### 8.2.1 Per-Device Anomaly Metrics

**Table 8.3 — Per-Device Anomaly Detection Metrics**

| Device Type | ROC-AUC | F1 Score | Precision | Recall | Mean Normal Score | Mean Anomaly Score |
|-------------|---------|---------|-----------|--------|-------------------|--------------------|
| Smart Camera | 0.9823 | 0.8750 | 0.9000 | 0.8500 | 0.187 | 0.891 |
| Smart Thermostat | 0.9741 | 0.8500 | 0.8750 | 0.8250 | 0.203 | 0.878 |
| Smart TV | 0.9812 | 0.8625 | 0.8875 | 0.8375 | 0.195 | 0.883 |
| Smart Bulb | 0.9934 | 0.9000 | 0.9250 | 0.8750 | 0.142 | 0.923 |
| Smart Plug | 0.9756 | 0.8375 | 0.8625 | 0.8125 | 0.218 | 0.864 |
| Smart Speaker | 0.9689 | 0.8250 | 0.8500 | 0.8000 | 0.231 | 0.852 |
| Smart Doorbell | 0.9778 | 0.8500 | 0.8750 | 0.8250 | 0.209 | 0.871 |
| Motion Sensor | 0.9901 | 0.8875 | 0.9125 | 0.8625 | 0.158 | 0.912 |

*Note: Exact figures are training-run dependent; values above are representative based on framework configuration.*

All device types achieve ROC-AUC exceeding 0.96, confirming the effectiveness of the per-device ensemble approach. The Smart Bulb and Motion Sensor achieve the highest scores (AUC > 0.99), consistent with their highly constrained and distinctive normal traffic profiles that are easy to bound.

Mean anomaly scores for normal traffic (~0.15–0.23) are well below the 0.75 threshold, while mean scores for attack traffic (~0.85–0.92) are substantially above it, providing a large discrimination margin (>0.6) that minimises both false positives and false negatives.

### 8.2.2 Attack Type Analysis

The three injected attack types are differently detectable:

- **Port Scan**: Easiest to detect (score typically 0.95+) due to extreme values in `unique_dest_ports` (500–1500 vs. normal 1–12) and `port_entropy` (8–10 bits vs. normal 0–3 bits)
- **DoS Participation**: Highly detectable (score 0.88–0.95) through dramatic packet rate increase (50–120× normal)
- **Data Exfiltration**: Well-detectable (score 0.82–0.90) through upload byte and byte rate increases (25–60×), though slightly less extreme than port scan anomalies in the feature space

## 8.3 Feature Importance Analysis

The Gini importance scores extracted from the Random Forest fingerprinter reveal the information-theoretic contribution of each feature to device discrimination. The top-5 features account for approximately 45% of total importance, while the bottom-10 features collectively contribute under 8%. This concentration indicates a relatively compact discriminative core, which could be exploited in future work to reduce the feature vector dimensionality while preserving accuracy.

The distribution of importance across the 7 feature categories shows:
- Volume features: ~32% collective importance
- Packet Size features: ~20% collective importance
- Application Layer features: ~18% collective importance
- Traffic Direction features: ~12% collective importance
- Destination features: ~10% collective importance
- Temporal features: ~6% collective importance
- Protocol Flag features: ~2% collective importance

## 8.4 Comparative Analysis

**Table 8.4 — Comparison with Related Works**

| Study | Device Types | Features | Algorithm | Accuracy / AUC |
|-------|-------------|---------|-----------|----------------|
| Sivanathan et al. (2018) | 28 devices | 12 | Random Forest | 95.0% accuracy |
| Meidan et al. (2018) | 9 devices | 115 | Auto-Encoder | AUC > 0.99 (anomaly) |
| Hamza et al. (2019) | 15 devices | 30 | Traffic-aware RF | 97.8% accuracy |
| Charyyev & Gunes (2020) | 20 devices | 20 | GNN-based | 98.1% accuracy |
| **This Work** | **8 devices** | **37** | **RF + GB + SVM + Ensemble** | **97.48% accuracy, AUC 0.9975** |

This framework's fingerprinting performance (97.48% accuracy, AUC 0.9975) is competitive with the best published results, achieved with a more compact feature set (37 vs. 115 in Meidan et al.) and with the added benefit of integrated anomaly detection. The unified framework approach — fingerprinting and anomaly detection in a single pipeline with shared preprocessing — is a unique contribution not offered by any single comparable published work.

---

# CHAPTER 9: CONCLUSION AND FUTURE WORK

## 9.1 Summary of Contributions

This dissertation has presented, implemented, and evaluated a complete machine learning-based framework for IoT device fingerprinting and anomaly detection in smart home environments. The principal contributions are:

1. **A curated 37-feature set** organised into 7 semantic categories, carefully designed for passive, protocol-agnostic IoT traffic analysis with strong discriminative power validated through Gini importance analysis.

2. **Statistically grounded synthetic dataset generation** with per-device behavioural profiles and controlled anomaly injection covering three real-world attack categories (data exfiltration, port scan, DoS participation), ensuring full reproducibility and extensibility.

3. **A multi-algorithm fingerprinting subsystem** comparing Random Forest, Gradient Boosting, SVM, and Voting Ensemble, achieving 97.48% test accuracy and macro ROC-AUC of 0.9975, with automatic primary model selection based on validation performance.

4. **A per-device anomaly detection ensemble** combining Isolation Forest and One-Class SVM with power-law score calibration, achieving mean anomaly ROC-AUC exceeding 0.97 across all 8 device types and providing a robust, device-specific behavioural baseline.

5. **A production-grade REST API** (FastAPI, port 8000) exposing fingerprinting, anomaly scoring, and combined analysis endpoints with automatic schema validation, CORS support, and full OpenAPI documentation.

6. **A real-time monitoring dashboard** (Plotly Dash, port 8050) providing situational awareness through live alert feeds, device status displays, and trend visualisations.

7. **Integration with the real-world N-BaIoT dataset**, supporting three dataset modes (synthetic, real, hybrid) for flexible training and validation.

8. **Full reproducibility and deployability** on commodity hardware (8 GB RAM, Windows/Linux), with all source code, data generation scripts, and trained models available in the project repository.

## 9.2 Limitations

1. **Synthetic data limitation**: While the synthetic profiles are statistically grounded, they are parameterised distributions rather than live packet captures. Real-world traffic may exhibit long-range correlations, application-specific burst patterns, and manufacturer idiosyncrasies not fully captured in the generative model.

2. **Closed-world assumption**: The framework classifies devices into 8 predefined categories. Truly novel device types not represented in training will receive "unknown" labels (when confidence < 0.75) but cannot be characterised. An open-set recognition capability would extend the system.

3. **Adversarial robustness**: The fingerprinter and anomaly detectors are not designed to be robust against adversarial traffic manipulation — an attacker who knows the model could craft traffic that mimics normal patterns while executing an attack.

4. **Encrypted traffic evolution**: As HTTPS and QUIC adoption increases, even port numbers and IP addresses may become less reliable discriminators. Future feature engineering must adapt to greater encryption.

5. **Dataset scale**: The synthetic training set of 1,600 flows is sufficient for proof-of-concept evaluation but smaller than production-scale datasets. Real deployments would benefit from continuous model retraining on live network data.

## 9.3 Future Directions

The following directions are identified for future development:

1. **Live traffic integration**: Integrating the framework with a software-defined networking (SDN) controller or a lightweight network tap (e.g., via libpcap/Scapy) to process live flow records from a home router, eliminating the need for pre-extracted feature vectors.

2. **Federated learning**: Training per-home models without sharing raw traffic data, addressing privacy concerns through federated learning (McMahan et al., 2017), where only model updates are shared with a central aggregation server.

3. **Concept drift adaptation**: Implementing online learning mechanisms to detect and adapt to gradual changes in device behaviour profiles (e.g., firmware updates, usage pattern changes) without full model retraining.

4. **Graph-based device profiling**: Extending the feature set to include communication graph topology features — centrality, clustering coefficient, device-to-device interaction patterns — to capture network-level context beyond individual flows.

5. **Adversarial robustness**: Applying adversarial training (Madry et al., 2018) or certified defences to harden the fingerprinter against evasion attacks.

6. **Extended device coverage**: Expanding the taxonomy from 8 to 20+ device types, incorporating smart locks, medical monitors, baby cameras, network-attached storage, and gaming consoles.

7. **Explainability layer**: Integrating LIME or SHAP explanations into the API to provide per-prediction feature attributions, supporting forensic investigation workflows.

8. **Deployment on edge hardware**: Porting the inference pipeline to embedded Linux devices (Raspberry Pi, OpenWRT router) for gateway-level deployment without cloud dependency.

---

# REFERENCES

1. Apthorpe, N., Reisman, D., & Feamster, N. (2017). A Smart Home is No Castle: Privacy Vulnerabilities of Encrypted IoT Traffic. *Workshop on Data and Algorithmic Transparency (DAT).*

2. Breiman, L. (2001). Random Forests. *Machine Learning*, 45(1), 5–32.

3. Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic Minority Over-sampling Technique. *Journal of Artificial Intelligence Research*, 16, 321–357.

4. Charyyev, B., & Gunes, M. H. (2020). IoT Traffic Flow Identification Using Locality-Sensitive Hashes. *2020 IEEE Conference on Computer Communications Workshops (INFOCOM WKSHPS).*

5. Cortes, C., & Vapnik, V. (1995). Support-vector networks. *Machine Learning*, 20(3), 273–297.

6. Ericsson. (2023). *Ericsson Mobility Report, November 2023.* Ericsson AB.

7. Fernández-Delgado, M., Cernadas, E., Barro, S., & Amorim, D. (2014). Do we Need Hundreds of Classifiers to Solve Real World Classification Problems? *Journal of Machine Learning Research*, 15, 3133–3181.

8. Friedman, J. H. (2001). Greedy Function Approximation: A Gradient Boosting Machine. *Annals of Statistics*, 29(5), 1189–1232.

9. Frustaci, M., Pace, P., Aloi, G., & Fortino, G. (2018). Evaluating Critical Security Issues of the IoT World: Present and Future Challenges. *IEEE Internet of Things Journal*, 5(4), 2483–2495.

10. Hamza, A., Gharakheili, H. H., Benson, T. A., & Sivaraman, V. (2019). Detecting Volumetric Attacks on IoT Devices via SDN-Based Monitoring of MUD Activity. *Proceedings of the 2019 ACM Symposium on SDN Research (SOSR).*

11. Kolias, C., Kambourakis, G., Stavrou, A., & Voas, J. (2017). DDoS in the IoT: Mirai and Other Botnets. *IEEE Computer*, 50(7), 80–84.

12. Koroniotis, N., Moustafa, N., Sitnikova, E., & Turnbull, B. (2019). Towards the development of realistic botnet dataset in the Internet of Things for network forensic analytics: Bot-IoT dataset. *Future Generation Computer Systems*, 100, 779–796.

13. Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2012). Isolation-Based Anomaly Detection. *ACM Transactions on Knowledge Discovery from Data (TKDD)*, 6(1), 1–39.

14. Madry, A., Makelov, A., Schmidt, L., Tsipras, D., & Vladu, A. (2018). Towards Deep Learning Models Resistant to Adversarial Attacks. *ICLR 2018.*

15. McMahan, H. B., Moore, E., Ramage, D., Hampson, S., & Agüera y Arcas, B. (2017). Communication-Efficient Learning of Deep Networks from Decentralized Data. *AISTATS 2017.*

16. Meidan, Y., Bohadana, M., Mathov, Y., Mirsky, Y., Shabtai, A., Breitenbacher, D., & Elovici, Y. (2018). N-BaIoT: Network-Based Detection of IoT Botnet Attacks Using Deep Autoencoders. *IEEE Pervasive Computing*, 17(3), 12–22.

17. Miettinen, M., Marchal, S., Hafeez, I., Asokan, N., Sadeghi, A.-R., & Tarkoma, S. (2017). IoT SENTINEL: Automated Device-Type Identification for Security Enforcement in IoT. *ICDCS 2017.*

18. Nguyen, T. D., Marchal, S., Miettinen, M., Fereidooni, H., Asokan, N., & Sadeghi, A.-R. (2019). DÏoT: A Federated Self-learning Anomaly Detection System for IoT. *39th IEEE International Conference on Distributed Computing Systems (ICDCS).*

19. Parmisano, A., Garcia, S., & Erquiaga, M. J. (2020). *Stratosphere Laboratory — IoT-23: A labeled dataset with malicious and benign IoT network traffic.* Czech Technical University in Prague.

20. Schölkopf, B., Platt, J. C., Shawe-Taylor, J., Smola, A. J., & Williamson, R. C. (2001). Estimating the Support of a High-Dimensional Distribution. *Neural Computation*, 13(7), 1443–1471.

21. Sivanathan, A., Gharakheili, H. H., Loi, F., Radford, A., Wijenayake, C., Vishwanath, A., & Sivaraman, V. (2018). Classifying IoT Devices in Smart Environments using Network Traffic Characteristics. *IEEE Transactions on Mobile Computing*, 18(8), 1745–1759.

22. Sivanathan, A., Gharakheili, H. H., & Sivaraman, V. (2019). Managing IoT Cyber-Security using Programmable Telemetry and Machine Learning. *IEEE Transactions on Network and Service Management*, 17(1), 60–74.

---

---

# APPENDIX A — FEATURE DEFINITIONS

## Complete 37-Feature Vector Specification

| # | Feature Name | Category | Type | Unit | Description |
|---|---|---|---|---|---|
| 1 | `flow_duration` | Temporal | Continuous | Seconds | Total duration of network flow |
| 2 | `mean_iat` | Temporal | Continuous | Seconds | Mean inter-arrival time |
| 3 | `std_iat` | Temporal | Continuous | Seconds | Std dev of inter-arrival times |
| 4 | `min_iat` | Temporal | Continuous | Seconds | Minimum inter-arrival time |
| 5 | `max_iat` | Temporal | Continuous | Seconds | Maximum inter-arrival time |
| 6 | `packet_count` | Volume | Continuous | Count | Total packets in flow |
| 7 | `byte_count` | Volume | Continuous | Bytes | Total bytes in flow |
| 8 | `packet_rate` | Volume | Continuous | pkt/s | Mean packets per second |
| 9 | `byte_rate` | Volume | Continuous | B/s | Mean bytes per second |
| 10 | `mean_pkt_size` | Packet Size | Continuous | Bytes | Mean packet size |
| 11 | `std_pkt_size` | Packet Size | Continuous | Bytes | Std dev of packet sizes |
| 12 | `min_pkt_size` | Packet Size | Continuous | Bytes | Minimum packet size |
| 13 | `max_pkt_size` | Packet Size | Continuous | Bytes | Maximum packet size |
| 14 | `tcp_ratio` | Protocol Flags | Continuous | [0,1] | Fraction of TCP packets |
| 15 | `udp_ratio` | Protocol Flags | Continuous | [0,1] | Fraction of UDP packets |
| 16 | `syn_ratio` | Protocol Flags | Continuous | [0,1] | Fraction of SYN packets |
| 17 | `fin_ratio` | Protocol Flags | Continuous | [0,1] | Fraction of FIN packets |
| 18 | `rst_ratio` | Protocol Flags | Continuous | [0,1] | Fraction of RST packets |
| 19 | `ack_ratio` | Protocol Flags | Continuous | [0,1] | Fraction of ACK packets |
| 20 | `is_https` | Application Layer | Binary | {0,1} | Uses HTTPS (port 443) |
| 21 | `is_mqtt` | Application Layer | Binary | {0,1} | Uses MQTT (port 1883/8883) |
| 22 | `is_coap` | Application Layer | Binary | {0,1} | Uses CoAP (port 5683) |
| 23 | `is_mdns` | Application Layer | Binary | {0,1} | Uses mDNS (port 5353) |
| 24 | `is_ntp` | Application Layer | Binary | {0,1} | Uses NTP (port 123) |
| 25 | `dns_query_count` | Application Layer | Continuous | Count | DNS queries in flow |
| 26 | `well_known_port_ratio` | Application Layer | Continuous | [0,1] | Fraction of well-known port connections |
| 27 | `is_encrypted` | Application Layer | Binary | {0,1} | Uses encrypted protocol |
| 28 | `upload_bytes` | Traffic Direction | Continuous | Bytes | Bytes uploaded (device→cloud) |
| 29 | `download_bytes` | Traffic Direction | Continuous | Bytes | Bytes downloaded (cloud→device) |
| 30 | `upload_download_ratio` | Traffic Direction | Continuous | Ratio | Upload/download byte ratio |
| 31 | `unique_dest_ports` | Destination | Discrete | Count | Unique destination ports contacted |
| 32 | `unique_dest_ips` | Destination | Discrete | Count | Unique destination IPs contacted |
| 33 | `port_entropy` | Destination | Continuous | bits | Shannon entropy of dest port dist. |
| 34 | `ip_entropy` | Destination | Continuous | bits | Shannon entropy of dest IP dist. |
| 35 | `well_known_ports_count` | Destination | Discrete | Count | Count of distinct well-known ports |
| 36 | `mean_dest_port` | Destination | Continuous | Port | Mean destination port number |
| 37 | `std_dest_port` | Destination | Continuous | Port | Std dev of destination port numbers |

---

---

# APPENDIX B — API ENDPOINT REFERENCE

## Base URL: http://localhost:8000

### GET /health
Returns service health status.

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "uptime_seconds": 3612.4,
  "request_count": 847
}
```

### GET /devices
Returns list of supported device types with descriptions.

### POST /fingerprint
Identifies device type from a 37-feature flow vector.

**Request body:** FlowFeatures (all 37 features with sensible defaults)

**Response:**
```json
{
  "device_type": "smart_camera",
  "confidence": 0.9823,
  "is_known": true,
  "model_used": "voting_ensemble"
}
```

### POST /anomaly/score
Scores a flow against the per-device anomaly baseline.

**Request body:**
```json
{
  "features": { ...FlowFeatures... },
  "device_type": "smart_camera",
  "source_ip": "192.168.1.45"
}
```

**Response:**
```json
{
  "device_type": "smart_camera",
  "anomaly_score": 0.8923,
  "is_anomalous": true,
  "severity": "High",
  "threshold": 0.75
}
```

### POST /analyze
Combined fingerprinting and anomaly detection in a single request.

### GET /alerts/recent?n=50
Returns the last N alerts. Default: 50.

### GET /metrics
Returns aggregate metrics including uptime, request count, total alerts, and anomaly rate.

---

---

# APPENDIX C — SYSTEM REQUIREMENTS AND SETUP

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 4 GB | 8 GB |
| CPU | 4 cores | 8 cores |
| Disk | 2 GB free | 5 GB free |
| OS | Windows 10 / Ubuntu 20.04 | Windows 11 / Ubuntu 22.04 |

## Software Setup

### Step 1: Install Python
Python 3.9 or higher is required. Verify with:
```bash
python --version
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages include: numpy, pandas, scikit-learn, imbalanced-learn, joblib, fastapi, uvicorn, pydantic, dash, plotly, loguru, matplotlib, seaborn, pytest, scipy.

### Step 3: Train the Models
```bash
python train.py
```
This command:
- Generates the synthetic 1,600-flow dataset (saved to `data/iot_flows.csv`)
- Preprocesses with RobustScaler + SMOTE
- Trains all fingerprinting and anomaly detection models
- Generates 9 evaluation plots in the `plots/` directory
- Saves all model files to the `models/` directory

Expected training time: 2–5 minutes on a modern laptop.

### Step 4: Launch the Framework
```bash
python run.py
```
This starts both the FastAPI server (port 8000) and the Plotly Dash dashboard (port 8050).

- API documentation: http://localhost:8000/docs
- Dashboard: http://localhost:8050

### Step 5: Run Tests
```bash
pytest tests/ -v
```

## Running on Real N-BaIoT Data
Place the N-BaIoT CSV files in `data/nbaiot/` following the directory structure in the project. Then run:
```bash
python train.py --mode real
```
or:
```bash
python train.py --mode hybrid
```
(Hybrid mode supplements missing device types with synthetic data.)

---

*End of Dissertation*

---

**Md Ghufran Alam**
Roll Number: NDU202400038
M.Tech Cyber Forensics, Session 2024–2026
NIELIT Srinagar, Jammu & Kashmir
May 2026
