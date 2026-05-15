# PRESENTATION SCRIPT — Panel Defense
**IoT Device Fingerprinting & Anomaly Detection Framework**
Md Ghufran Alam | NDU202400038 | M.Tech Cyber Forensics | NIELIT Srinagar

---

## SLIDE 1 — Title Slide
*(Jab slide aaye, ek second ruko, phir bolna shuru karo)*

"Respected panel members, good morning / good afternoon.

My name is **Md Ghufran Alam**, Roll Number **NDU202400038**, pursuing M.Tech in Cyber Forensics from NIELIT Srinagar, Session 2024–2026.

Today I am presenting my dissertation titled:
**'Design of a Framework for IoT Device Fingerprinting and Anomaly Detection for Smart Home using Machine Learning.'**

This work has been done under the supervision of **Dr. Syed Nisar Hussain Bukhari**, NDU Coordinator, Department of CSE, NIELIT Srinagar.

The framework is **live and publicly accessible** right now at the HuggingFace Spaces URL shown on the slide — I will demonstrate it during the presentation.

Please allow me to begin."

---

## SLIDE 2 — Problem Statement
*(Thodi urgency ke saath bolna — problem serious hai)*

"Let me start with the problem.

IoT yani Internet of Things devices — smart cameras, thermostats, doorbells, bulbs — aaj ghar ghar mein hain. Lekin **inki security ek badi problem hai**.

**2016 mein Mirai botnet** ne 600,000 se zyada IoT devices compromise kar liye. Usne ek massive DDoS attack kiya — **620 Gigabits per second** — jisne Twitter, Netflix, Reddit aur GitHub ko ek saath offline kar diya.

Yeh possible hua kyunki:
- Smart devices antivirus nahi chala sakte — unke paas processing power nahi hoti
- Traditional firewalls sirf port aur IP dekhte hain — unhe pata nahi hota ki **kaunsa device hai network pe**
- Network admin ke paas koi baseline nahi hoti ki ek camera ka normal traffic kaisa dikhta hai

**Toh teen fundamental questions the jo mujhe solve karne the:**
1. Yeh konsa device hai mere network pe? — **Device Fingerprinting**
2. Kya yeh device abhi normally behave kar raha hai? — **Anomaly Detection**
3. Model ne yeh alert kyun diya? — **SHAP Explainability**

Yahi is framework ka core objective hai."

---

## SLIDE 3 — System Architecture
*(Diagram ko point karte hue explain karo)*

"Ab main architecture explain karta hoon — end-to-end pipeline kaisi kaam karti hai.

**Input layer** mein network traffic aata hai — **37 network flow features** extract kiye jaate hain, jaise packet rate, byte count, TCP/UDP ratio, destination ports wagera.

Yeh features pehle **RobustScaler** se normalize hote hain — outliers se protect karne ke liye.

Phir yeh pipeline **teen parallel modules** mein jaati hai:

**Left — Device Fingerprinting:**
Random Forest model decide karta hai — yeh device kaunsi category ka hai. Output milta hai — device label aur confidence percentage.

**Center — Anomaly Detection:**
Isolation Forest aur One-Class SVM ka ensemble — decide karta hai ki yeh device normally behave kar raha hai ya nahi. Output mein anomaly score aata hai — 0 to 1 ke beech.

**Right — SHAP Explainability:**
Har prediction ke saath top-10 features explain hote hain — kaunsa feature ne decision pe kitna impact dala.

**Bottom layer** mein:
- Alert Manager alerts generate karta hai
- FastAPI REST API endpoints expose karta hai
- Live HTML dashboard hai monitoring ke liye — real-time Plotly.js charts ke saath

**Sab kuch ek hi Docker container mein deploy hai — single port 7860 pe.**"

---

## SLIDE 4 — Dataset & Feature Engineering
*(Confidently bolna — dataset ka knowledge dikhao)*

"Is framework ko train karne ke liye maine **N-BaIoT dataset** use kiya — jo UCI Machine Learning Repository pe available hai, ID #442.

Yeh dataset **real physical IoT devices** se capture kiya gaya hai:
- 9 alag alag devices the — Danmini Doorbell, Ecobee Thermostat, Security Cameras, Baby Monitor, Samsung Webcam wagera
- Dataset mein **normal traffic** bhi hai aur **actual attack traffic** bhi — Mirai ke 5 variants aur BASHLITE ke 5 variants

Dataset mein originally **115 features** the. Maine unhe carefully analyze karke **37 features** ka ek meaningful subset banaaya — jo actually device ke behavior ko capture karte hain.

**Yeh 37 features 7 categories mein divide hain:**
1. **Temporal** — flow duration, inter-arrival times
2. **Volume** — packet count, byte count, packet rate
3. **Packet Size** — mean, std, min, max packet size
4. **Protocol** — TCP, UDP, SYN, FIN, ACK ratios
5. **Application Layer** — HTTPS, MQTT, CoAP, mDNS, DNS queries
6. **Direction** — upload/download bytes aur ratio
7. **Destination** — unique ports, unique IPs, port entropy

**Key insight yeh hai ki Protocol aur Application Layer features sabse zyada discriminative hain** — ek smart camera mostly HTTPS use karta hai, ek thermostat MQTT use karta hai, ek smart bulb CoAP use karta hai. Yeh protocol fingerprint hi unhe alag karta hai."

---

## SLIDE 5 — Machine Learning Models
*(Dono modules clearly explain karo)*

"Ab models ki baat karte hain.

**Module 1 — Device Fingerprinting** (supervised classification):

Maine 4 models train kiye aur compare kiye:
- **Random Forest** — 100 trees, balanced class weights — **100% accuracy**
- **Gradient Boosting** — 100 trees, learning rate 0.1 — **100% accuracy**
- **SVM RBF kernel** — **94.89% accuracy**
- **Voting Ensemble** — teeno ka combination — **100% accuracy**

Training mein **SMOTE balancing** use kiya — taaki rare device types bhi properly represent hon. Aur **RobustScaler** se normalization ki.

Confidence threshold **60%** rakha hai — agar model 60% se kam confident ho toh device ko 'Unknown' mark karta hai — yeh bhi ek security signal hai.

---

**Module 2 — Anomaly Detection** (unsupervised):

Yahan approach bilkul alag hai. Maine **har device type ke liye alag model** banaya — kyunki ek camera ka normal traffic ek thermostat se bilkul alag hota hai.

**Sirf normal traffic pe train kiya** — koi attack data nahi diya training mein. Yeh approach zyada realistic hai real-world mein jahan attack patterns unknown hote hain.

Ensemble mein do algorithms hain:
- **Isolation Forest** — anomalies ko isolate karta hai tree structure se
- **One-Class SVM** — ek boundary seekhta hai normal data ke around

Final score dono ka weighted average hai. **Threshold 0.75** hai:
- 0.75 se kam → Normal
- 0.50–0.65 → LOW alert
- 0.65–0.80 → MEDIUM
- 0.80–0.90 → HIGH
- 0.90+ → CRITICAL"

---

## SLIDE 6 — Results: Device Fingerprinting
*(Numbers confidently bolna — yeh strong results hain)*

"Results dekhte hain — Fingerprinting module ke.

Main table mein clearly dikh raha hai:
- **Random Forest, Gradient Boosting, aur Voting Ensemble** — teeno ne **100% test accuracy, ROC-AUC 1.0, F1-score 1.0** achieve ki
- **SVM** ne 94.89% accuracy li — jo bhi excellent hai

**Per-device breakdown mein** — sab 8 device categories ne 100% accuracy, 1.0 precision aur 1.0 recall achieve ki. Koi ek bhi misclassification nahi.

**Key insight panel ke liye:**
Yeh accuracy is liye possible hai kyunki har IoT device type ka protocol fingerprint unique hota hai. Ek smart camera har waqt HTTPS pe large packets bhejta hai — ek thermostat sirf MQTT pe choti choti messages bhejta hai — yeh patterns overlapping nahi hote.

Aur important baat — **koi hardware access nahi, koi credentials nahi, koi agent install nahi** — sirf network traffic se device identify hoti hai."

---

## SLIDE 7 — Results: Anomaly Detection
*(F1 low kyun hai — yeh zaroor poochhenge, prepared raho)*

"Anomaly Detection ke results.

Bar chart mein AUC-ROC scores dikh rahe hain har device type ke liye:
- **Smart Doorbell** sabse best — **AUC 0.8773**
- **Smart Thermostat** — **0.8590**
- Baaki devices 0.71 to 0.79 ke beech hain

**Ab panel yeh zaroor poochhenge — F1 score low kyun hai?**

Mera jawab yeh hai:

Mirai aur BASHLITE specifically **IoT traffic ko mimic karne ke liye design kiye gaye hain**. Yeh normal traffic mein blend karte hain — yahi unki design objective thi.

Hamara model **sirf normal traffic pe trained hai** — usne kabhi attack traffic dekha hi nahi training mein. Phir bhi AUC 0.87 tak pahuncha — yeh batata hai ki model ne normal behavior ki boundary accurately seekh li hai.

**AUC-ROC is task ke liye sahi metric hai** — yeh threshold-independent hai. F1 score threshold pe depend karta hai — deployment mein threshold tune karke F1 bhi improve ho sakta hai.

**Live demo mein** — normal traffic pe zero false positives aaye, aur injected attacks pe 100% detection rate mili."

---

## SLIDE 8 — SHAP Explainability
*(XAI ka importance samjhao — yeh differentiator hai)*
*(Right side pe SHAP bar chart embedded hai slide mein — uski taraf point karo)*

"Ab ek aur important contribution — **SHAP Explainability**, yaani Explainable AI.

**Panel yeh pooch sakte hain — explainability kyun zaroori hai security mein?**

Jawab simple hai: ek black-box alert jo sirf bolta hai 'anomaly detected' — ek SOC analyst ke liye actionable nahi hai. Analyst ko yeh jaanna chahiye ki **kyun** flag hua.

SHAP — SHapley Additive exPlanations — har prediction ke liye bataata hai ki kaunsa feature ne decision ko kitna influence kiya aur kaunsi direction mein.

*(Right side bar chart ki taraf point karo)*
Slide pe bar chart dikh raha hai — ek **Unknown device** jo sirf 46% confidence pe tha:
- **tcp_ratio** — Red bar — matlab model se door le ja raha hai — high TCP usage is device profile se match nahi karta
- **udp_ratio** — Red bar — UDP ratio too high
- **is_mqtt** — Green bar — MQTT traffic partially support kar raha hai classification ko
- **mean_dest_port** — Red bar — port profile kisi bhi known device se match nahi karta

Green bars push karte hain prediction ko, Red bars pull karte hain door — ek glance mein sab clear.

Yeh information ek security analyst ko **seconds mein** manually verify karne deti hai.

**Implementation mein:**
- TreeExplainer use kiya — jo KernelExplainer se 10x fast hai
- POST /explain endpoint available hai
- Dashboard mein live SHAP panel bhi hai
- Response time **30ms se kam** hai"

---

## SLIDE 9 — Live Deployment
*(Yahan live demo ke liye taiyar raho)*

"Ab deployment ki baat karte hain — aur main chahta hoon ki yeh sirf slides pe na rahe, aap live dekh sakein.

**Platform:** HuggingFace Spaces — Docker SDK — publicly accessible, free tier pe.

**Architecture:** FastAPI **ek hi port pe** sab kuch serve karta hai — port 7860 — REST API, live dashboard, aur Swagger UI sab saath.

**Available URLs:**
- **Live Dashboard** — main monitoring interface
- **API Docs** — Swagger UI — sab endpoints documented
- **Status Page** — health check

**8 API Endpoints hain:**
- GET /health, /devices, /metrics
- POST /fingerprint, /anomaly/score, /analyze, /explain, /alerts/recent

**Performance:**
- API latency **~40ms** hai
- Fingerprinting accuracy **100%** hai 8 device categories pe
- System abhi live hai

*(Agar internet available ho toh browser kholo aur URL dikhao)*"

---

## SLIDE 10 — Demo: Device Fingerprinting
*(Calmly explain karo — yeh impressive slide hai)*
*(Slide ke bottom mein green banner hai — "Try live: .../docs → POST /fingerprint" — uski taraf point karo)*

"Is slide mein fingerprinting ka simulated demo hai — 8 devices ko network traffic se identify karte hue.

*(Bottom banner point karo)* "Aur yeh sirf simulation nahi — slide ke niche URL dikh raha hai — aap live Swagger UI pe jaake POST /fingerprint khud try kar sakte hain abhi."

Dekho — **koi device access nahi, koi login nahi, koi agent nahi**:

- **192.168.1.45** → Smart Camera — 99% confidence — HTTPS traffic, 400 packets/second, large packets, port 443
- **192.168.1.22** → Smart Thermostat — 98% — MQTT, sirf 2 packets/second, 80-byte small packets, port 1883
- **192.168.1.10** → Smart TV — 97% — streaming traffic, 695 MB download, 18 unique IPs
- **192.168.1.77** → Smart Bulb — 96% — CoAP protocol, sirf 4 packets, port 5683
- **192.168.1.99** → Motion Sensor — 95% — event-driven, MQTT + CoAP
- **192.168.1.55** → Smart Plug — 97% — MQTT, port 8883
- **192.168.1.33** → Smart Speaker — 98% — HTTPS, voice streaming pattern, 5 cloud IPs
- **192.168.1.88** → Smart Doorbell — 96% — camera + audio burst, 2.5 MB upload

**Bottom line** — jaise fingerprints se human identity hoti hai, waise hi network traffic patterns se IoT device identity possible hai."

---

## SLIDE 11 — Demo: Anomaly Detection
*(Yahan attack scenarios clearly explain karo)*
*(Slide ke bottom mein green banner hai — "Try live: .../docs → POST /anomaly/score & POST /analyze" — uski taraf point karo)*

"Anomaly detection ka demo — 4 test cases:

*(Bottom banner point karo)* "Yeh bhi live test kar sakte hain — POST /anomaly/score aur POST /analyze dono endpoints Swagger pe available hain."

**Test 1 — Normal Camera Traffic:**
Score: **0.0000 — NORMAL**
Camera 400 packets/second bhej rahi thi, 28MB upload, upload-download ratio normal 2:1 tha. Model ne correctly normal classify kiya. **Zero false positive.**

**Test 2 — Data Exfiltration (Mirai attack):**
Score: **0.8060 — HIGH ALERT**
Same camera suddenly **1.68 Gigabytes** upload kar rahi thi — ratio 2 se bhadh ke **120** ho gaya. Model ne HIGH alert generate kiya. Yeh Mirai ka typical data exfiltration behavior hai.

**Test 3 — Port Scan / Reconnaissance:**
Score: **0.7745 — MEDIUM ALERT**
Ek thermostat **1200 ports × 250 IP addresses** scan kar raha tha — port entropy 9.5 — jo normal thermostat ke liye completely impossible hai. Model ne MEDIUM alert diya.

**Test 4 — /analyze Combined Call:**
Score: **0.8060 — HIGH**
Is endpoint mein fingerprinting aur anomaly detection **ek hi API call** mein hote hain. Automatically camera identify ki aur exfiltration detect ki.

**Result: Normal traffic pe zero false positives. Teeno attack types detect hue correct severity ke saath.**"

---

## SLIDE 12 — Conclusion & Contributions
*(Confidently — yeh aapki achievements hain)*

"In conclusion — is dissertation ne 8 konkrete contributions diye hain:

**1. Fingerprinting** — 100% accuracy, 8 IoT device types, sirf network traffic se — koi device access nahi.

**2. Anomaly Detection** — per-device unsupervised ensemble, Mirai/BASHLITE detection, AUC up to 0.877.

**3. Explainability** — SHAP TreeExplainer, real-time top-10 features, har prediction ke saath.

**4. Production Deployment** — HuggingFace Spaces pe live, publicly accessible, sub-40ms latency.

**5. REST API** — 8 FastAPI endpoints, fully documented Swagger UI.

**6. Dashboard** — Live HTML/Plotly.js monitoring dashboard — anomaly timeline, severity chart, real-time alert feed.

**7. Dataset** — Real N-BaIoT data, real Mirai aur BASHLITE attack traffic.

**8. Open Source** — GitHub pe available, MIT licensed, reproducible.

**Most importantly — yeh system right now live hai.** Yeh ek theoretical exercise nahi hai — yeh ek working production system hai."

---

## SLIDE 13 — Thank You
*(Calmly, confidently)*

"Thank you, respected panel members, for your time and attention.

I am happy to take your questions.

The live system is accessible at the URL shown on screen if you would like to test any endpoint directly."

---

## EXPECTED PANEL QUESTIONS — Prepared Answers

**Q1: F1 score low kyun hai anomaly detection mein?**
A: Mirai aur BASHLITE specifically IoT traffic mimic karne ke liye design hue hain. Model sirf normal traffic pe trained tha — phir bhi AUC 0.877 achieve hua. AUC threshold-independent metric hai — F1 deployment mein tune hota hai.

**Q2: 100% fingerprinting accuracy — overfitting toh nahi?**
A: Nahi. Dataset mein physically alag alag device types hain jinke protocol signatures genuinely different hain. Train-test split proper tha. AUC 1.0 is liye hai kyunki MQTT/CoAP/HTTPS signatures non-overlapping hain.

**Q3: Real network pe kaise deploy karenge?**
A: Network tap ya mirror port se traffic capture karein, 37 features extract karein, POST /fingerprint pe bhejein. Edge mein deploy ho sakta hai — Raspberry Pi pe bhi chalta hai.

**Q4: SHAP kyun use kiya, LIME kyun nahi?**
A: TreeExplainer Random Forest ke liye native support deta hai — LIME se 10x fast hai. LIME approximation-based hai, SHAP exact Shapley values compute karta hai — zyada accurate hai.

**Q5: Dataset aur real-world traffic mein gap hai?**
A: N-BaIoT real physical devices se capture hua hai — simulated nahi. Haan, new device types ke liye retraining zaroori hogi — yeh future work mein mention hai.

**Q6: HuggingFace free tier pe production-grade system kaise?**
A: HuggingFace Spaces Docker SDK free tier pe 16GB RAM aur 2 vCPU deta hai — chhote deployments ke liye sufficient hai. Models PKL files se load hote hain — cold start ~10 seconds.

---
*Script prepared for panel defense — NIELIT Srinagar, May 2026*
