"""Test exact demo payloads from PANEL_DEMO_GUIDE.md against the live API."""
import urllib.request, json

BASE = "http://127.0.0.1:8000"

def post(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=data, headers={"Content-Type": "application/json"})
    r = urllib.request.urlopen(req, timeout=5)
    return json.loads(r.read())

print("=" * 60)
print("Testing EXACT payloads from PANEL_DEMO_GUIDE.md")
print("=" * 60)

# ── Demo 5: Normal camera (POST /anomaly/score) ───────────────
normal_camera = {
    "features": {
        "flow_duration": 90.0, "mean_iat": 0.003, "std_iat": 0.002,
        "min_iat": 0.001, "max_iat": 0.015, "packet_count": 28000,
        "byte_count": 42000000, "packet_rate": 400, "byte_rate": 600000,
        "mean_pkt_size": 1400, "std_pkt_size": 180, "min_pkt_size": 64,
        "max_pkt_size": 1500, "tcp_ratio": 0.95, "udp_ratio": 0.05,
        "syn_ratio": 0.005, "fin_ratio": 0.004, "rst_ratio": 0.001,
        "ack_ratio": 0.60, "is_https": 1.0, "is_mqtt": 0.0,
        "is_coap": 0.0, "is_mdns": 0.05, "is_ntp": 0.04,
        "dns_query_count": 4, "well_known_port_ratio": 0.90,
        "is_encrypted": 1.0, "upload_bytes": 28000000,
        "download_bytes": 14000000, "upload_download_ratio": 2.0,
        "unique_dest_ports": 4, "unique_dest_ips": 3,
        "port_entropy": 1.2, "ip_entropy": 1.0,
        "well_known_ports_count": 3, "mean_dest_port": 443, "std_dest_port": 30
    },
    "device_type": "smart_camera", "source_ip": "192.168.1.45"
}
r = post("/anomaly/score", normal_camera)
ok = "OK" if not r["is_anomalous"] else "FAIL"
print(f"\nDemo 5 — Normal Camera:       [{ok}]  score={r['anomaly_score']:.4f}  anomalous={r['is_anomalous']}")

# ── Demo 6: Data exfiltration attack ─────────────────────────
exfil_camera = {
    "features": {
        "flow_duration": 90.0, "mean_iat": 0.003, "std_iat": 0.002,
        "min_iat": 0.001, "max_iat": 0.015, "packet_count": 28000,
        "byte_count": 2100000000, "packet_rate": 400, "byte_rate": 36000000,
        "mean_pkt_size": 1400, "std_pkt_size": 180, "min_pkt_size": 64,
        "max_pkt_size": 1500, "tcp_ratio": 0.95, "udp_ratio": 0.05,
        "syn_ratio": 0.005, "fin_ratio": 0.004, "rst_ratio": 0.001,
        "ack_ratio": 0.60, "is_https": 1.0, "is_mqtt": 0.0,
        "is_coap": 0.0, "is_mdns": 0.05, "is_ntp": 0.04,
        "dns_query_count": 4, "well_known_port_ratio": 0.90,
        "is_encrypted": 1.0, "upload_bytes": 1680000000,
        "download_bytes": 14000000, "upload_download_ratio": 120.0,
        "unique_dest_ports": 4, "unique_dest_ips": 3,
        "port_entropy": 1.2, "ip_entropy": 1.0,
        "well_known_ports_count": 3, "mean_dest_port": 443, "std_dest_port": 30
    },
    "device_type": "smart_camera", "source_ip": "192.168.1.45"
}
r = post("/anomaly/score", exfil_camera)
ok = "OK" if r["is_anomalous"] else "FAIL"
print(f"Demo 6 — Exfiltration Attack:  [{ok}]  score={r['anomaly_score']:.4f}  anomalous={r['is_anomalous']}  severity={r['severity']}")

# ── Demo 7: Port scan attack ──────────────────────────────────
port_scan = {
    "features": {
        "flow_duration": 4.0, "mean_iat": 0.8, "std_iat": 0.3,
        "min_iat": 0.05, "max_iat": 5.0, "packet_count": 400000,
        "byte_count": 800, "packet_rate": 2, "byte_rate": 200,
        "mean_pkt_size": 85, "std_pkt_size": 20, "min_pkt_size": 40,
        "max_pkt_size": 200, "tcp_ratio": 0.15, "udp_ratio": 0.85,
        "syn_ratio": 0.05, "fin_ratio": 0.04, "rst_ratio": 0.01,
        "ack_ratio": 0.10, "is_https": 0.0, "is_mqtt": 1.0,
        "is_coap": 0.0, "is_mdns": 0.02, "is_ntp": 0.05,
        "dns_query_count": 1, "well_known_port_ratio": 0.60,
        "is_encrypted": 0.0, "upload_bytes": 400, "download_bytes": 400,
        "upload_download_ratio": 1.0, "unique_dest_ports": 1200,
        "unique_dest_ips": 250, "port_entropy": 9.5, "ip_entropy": 8.2,
        "well_known_ports_count": 1, "mean_dest_port": 1883, "std_dest_port": 10
    },
    "device_type": "smart_thermostat", "source_ip": "192.168.1.22"
}
r = post("/anomaly/score", port_scan)
ok = "OK" if r["is_anomalous"] else "FAIL"
print(f"Demo 7 — Port Scan Attack:     [{ok}]  score={r['anomaly_score']:.4f}  anomalous={r['is_anomalous']}  severity={r['severity']}")

# ── Demo 8: Combined /analyze — Exfiltration attack ──────────
exfil_analyze = {
    "features": {
        "flow_duration": 90.0, "mean_iat": 0.003, "std_iat": 0.002,
        "min_iat": 0.001, "max_iat": 0.015, "packet_count": 28000,
        "byte_count": 2100000000, "packet_rate": 400, "byte_rate": 36000000,
        "mean_pkt_size": 1400, "std_pkt_size": 180, "min_pkt_size": 64,
        "max_pkt_size": 1500, "tcp_ratio": 0.95, "udp_ratio": 0.05,
        "syn_ratio": 0.005, "fin_ratio": 0.004, "rst_ratio": 0.001,
        "ack_ratio": 0.60, "is_https": 1.0, "is_mqtt": 0.0,
        "is_coap": 0.0, "is_mdns": 0.05, "is_ntp": 0.04,
        "dns_query_count": 4, "well_known_port_ratio": 0.90,
        "is_encrypted": 1.0, "upload_bytes": 1680000000,
        "download_bytes": 14000000, "upload_download_ratio": 120.0,
        "unique_dest_ports": 4, "unique_dest_ips": 3,
        "port_entropy": 1.2, "ip_entropy": 1.0,
        "well_known_ports_count": 3, "mean_dest_port": 443, "std_dest_port": 30
    },
    "source_ip": "192.168.1.45"
}
r = post("/analyze", exfil_analyze)
fp = r["fingerprint"]
an = r["anomaly"]
ok = "OK" if an["is_anomalous"] else "FAIL"
print(f"Demo 8 — Exfil /analyze:       [{ok}]  device={fp['device_type']}({fp['confidence']:.4f})  score={an['anomaly_score']:.4f}  severity={an['severity']}")

print("\n" + "=" * 60)
all_ok = True
