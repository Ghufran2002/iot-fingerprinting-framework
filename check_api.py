"""Quick API health check for panel demo verification."""
import urllib.request, json, sys

results = []

def get(url):
    r = urllib.request.urlopen(url, timeout=5)
    return json.loads(r.read())

def post(url, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    r = urllib.request.urlopen(req, timeout=5)
    return json.loads(r.read())

# Camera features (normal traffic)
camera_feats = {
    "flow_duration": 90.0, "mean_iat": 0.003, "std_iat": 0.002,
    "min_iat": 0.001, "max_iat": 0.015, "packet_count": 28000,
    "byte_count": 42000000, "packet_rate": 400, "byte_rate": 600000,
    "mean_pkt_size": 1400, "std_pkt_size": 180, "min_pkt_size": 64,
    "max_pkt_size": 1500, "tcp_ratio": 0.95, "udp_ratio": 0.05,
    "syn_ratio": 0.005, "fin_ratio": 0.004, "rst_ratio": 0.001,
    "ack_ratio": 0.6, "is_https": 1.0, "is_mqtt": 0.0, "is_coap": 0.0,
    "is_mdns": 0.05, "is_ntp": 0.04, "dns_query_count": 4,
    "well_known_port_ratio": 0.9, "is_encrypted": 1.0,
    "upload_bytes": 28000000, "download_bytes": 14000000,
    "upload_download_ratio": 2.0, "unique_dest_ports": 4,
    "unique_dest_ips": 3, "port_entropy": 1.2, "ip_entropy": 1.0,
    "well_known_ports_count": 3, "mean_dest_port": 443, "std_dest_port": 30
}

# Attack features (data exfiltration — 50x upload)
attack_feats = dict(camera_feats)
attack_feats.update({"byte_count": 2100000000, "byte_rate": 36000000,
                     "upload_bytes": 1680000000, "download_bytes": 420000000,
                     "upload_download_ratio": 4.0})

try:
    h = get("http://127.0.0.1:8000/health")
    print(f"[OK] GET /health         status={h['status']}  models_loaded={h['models_loaded']}")
except Exception as e:
    print(f"[FAIL] GET /health: {e}"); sys.exit(1)

try:
    d = get("http://127.0.0.1:8000/devices")
    print(f"[OK] GET /devices        {len(d['supported_devices'])} device types listed")
except Exception as e:
    print(f"[FAIL] GET /devices: {e}")

try:
    f = post("http://127.0.0.1:8000/fingerprint", camera_feats)
    print(f"[OK] POST /fingerprint   device={f['device_type']}  confidence={f['confidence']:.4f}  known={f['is_known']}")
except Exception as e:
    print(f"[FAIL] POST /fingerprint: {e}")

try:
    n = post("http://127.0.0.1:8000/anomaly/score",
             {"features": camera_feats, "device_type": "smart_camera", "source_ip": "192.168.1.45"})
    print(f"[OK] POST /anomaly/score (normal)  score={n['anomaly_score']:.4f}  anomalous={n['is_anomalous']}")
except Exception as e:
    print(f"[FAIL] POST /anomaly/score (normal): {e}")

try:
    a = post("http://127.0.0.1:8000/anomaly/score",
             {"features": attack_feats, "device_type": "smart_camera", "source_ip": "192.168.1.45"})
    print(f"[OK] POST /anomaly/score (attack)  score={a['anomaly_score']:.4f}  anomalous={a['is_anomalous']}  severity={a['severity']}")
except Exception as e:
    print(f"[FAIL] POST /anomaly/score (attack): {e}")

try:
    m = get("http://127.0.0.1:8000/metrics")
    print(f"[OK] GET /metrics        requests={m['request_count']}  alerts={m['total_alerts']}")
except Exception as e:
    print(f"[FAIL] GET /metrics: {e}")

try:
    urllib.request.urlopen("http://127.0.0.1:8050", timeout=5)
    print("[OK] Dashboard (8050)    HTTP 200 OK — Plotly Dash live")
except Exception as e:
    print(f"[FAIL] Dashboard (8050): {e}")

print("\nAll checks complete.")
