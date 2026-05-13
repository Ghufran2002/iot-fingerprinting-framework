"""Find attack payload values that reliably trigger alerts above 0.75 threshold."""
import urllib.request, json

def post(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        "http://127.0.0.1:8000" + path, data=data,
        headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=5).read())

# ── Exfiltration: fix upload_download_ratio (was 4.0, corrected to 120) ──────
exfil_fixed = {
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
        "is_encrypted": 1.0,
        "upload_bytes": 1680000000,
        "download_bytes": 14000000,       # FIXED: keep at normal (was 420000000)
        "upload_download_ratio": 120.0,   # FIXED: 1680MB/14MB = 120 (was 4.0)
        "unique_dest_ports": 4, "unique_dest_ips": 3,
        "port_entropy": 1.2, "ip_entropy": 1.0,
        "well_known_ports_count": 3, "mean_dest_port": 443, "std_dest_port": 30
    },
    "device_type": "smart_camera", "source_ip": "192.168.1.45"
}
r = post("/anomaly/score", exfil_fixed)
print(f"Exfil fixed (ratio=120): score={r['anomaly_score']:.4f}  anomalous={r['is_anomalous']}  severity={r['severity']}")

# ── DoS: increase packet_rate to 120x, syn_ratio to 0.85 ─────────────────────
dos_fixed = {
    "features": {
        "flow_duration": 90.0, "mean_iat": 0.003, "std_iat": 0.002,
        "min_iat": 0.001, "max_iat": 0.015,
        "packet_count": 4200000,          # 150x of 28,000
        "byte_count": 42000000,
        "packet_rate": 48000,             # 120x of 400
        "byte_rate": 72000000,            # 120x of 600,000
        "mean_pkt_size": 1400, "std_pkt_size": 180, "min_pkt_size": 64,
        "max_pkt_size": 1500, "tcp_ratio": 0.95, "udp_ratio": 0.05,
        "syn_ratio": 0.85,                # very high (SYN flood indicator)
        "fin_ratio": 0.004, "rst_ratio": 0.001, "ack_ratio": 0.60,
        "is_https": 1.0, "is_mqtt": 0.0, "is_coap": 0.0,
        "is_mdns": 0.05, "is_ntp": 0.04, "dns_query_count": 4,
        "well_known_port_ratio": 0.90, "is_encrypted": 1.0,
        "upload_bytes": 28000000, "download_bytes": 14000000,
        "upload_download_ratio": 2.0,
        "unique_dest_ports": 4, "unique_dest_ips": 3,
        "port_entropy": 1.2, "ip_entropy": 1.0,
        "well_known_ports_count": 3, "mean_dest_port": 443, "std_dest_port": 30
    },
    "source_ip": "192.168.1.45"
}
r2 = post("/analyze", dos_fixed)
fp = r2["fingerprint"]
an = r2["anomaly"]
print(f"DoS fixed (120x, syn=0.85): device={fp['device_type']} conf={fp['confidence']:.4f}  score={an['anomaly_score']:.4f}  anomalous={an['is_anomalous']}  severity={an['severity']}")

print("\nDone.")
