"""Find DoS values that push above 0.75 threshold on smart_camera."""
import urllib.request, json

def post(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        "http://127.0.0.1:8000" + path, data=data,
        headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=5).read())

base = {
    "flow_duration": 90.0, "mean_iat": 0.003, "std_iat": 0.002,
    "min_iat": 0.001, "max_iat": 0.015, "byte_count": 42000000,
    "mean_pkt_size": 1400, "std_pkt_size": 180, "min_pkt_size": 64,
    "max_pkt_size": 1500, "tcp_ratio": 0.95, "udp_ratio": 0.05,
    "fin_ratio": 0.004, "rst_ratio": 0.001, "ack_ratio": 0.60,
    "is_https": 1.0, "is_mqtt": 0.0, "is_coap": 0.0,
    "is_mdns": 0.05, "is_ntp": 0.04, "dns_query_count": 4,
    "well_known_port_ratio": 0.90, "is_encrypted": 1.0,
    "upload_bytes": 28000000, "download_bytes": 14000000,
    "upload_download_ratio": 2.0, "unique_dest_ports": 4,
    "unique_dest_ips": 3, "port_entropy": 1.2, "ip_entropy": 1.0,
    "well_known_ports_count": 3, "mean_dest_port": 443, "std_dest_port": 30
}

# Test different DoS intensities
tests = [
    (50000, 3500000, 80000000, 0.85, "100x pkt_rate, syn=0.85"),
    (80000, 5600000, 120000000, 0.95, "200x pkt_rate, syn=0.95"),
    (120000, 8400000, 180000000, 0.99, "300x pkt_rate, syn=0.99"),
    (240000, 16800000, 360000000, 0.99, "600x pkt_rate, syn=0.99"),
]

print("DoS on smart_camera — finding threshold:")
for pkt_rate, pkt_count, byte_rate, syn, label in tests:
    feats = dict(base)
    feats.update({"packet_rate": pkt_rate, "packet_count": pkt_count,
                  "byte_rate": byte_rate, "syn_ratio": syn})
    r = post("/anomaly/score", {"features": feats, "device_type": "smart_camera",
                                "source_ip": "192.168.1.45"})
    alert = "ALERT" if r["is_anomalous"] else "no alert"
    print(f"  {label}: score={r['anomaly_score']:.4f}  [{alert}]  severity={r['severity']}")

print()
# Also test DoS on a sensor (easier to detect since sensor has minimal normal traffic)
sensor_base = dict(base)
sensor_base.update({
    "byte_count": 800, "packet_count": 5, "packet_rate": 10, "byte_rate": 270,
    "mean_pkt_size": 85, "tcp_ratio": 0.15, "udp_ratio": 0.85,
    "is_https": 0.0, "is_mqtt": 1.0, "is_coap": 1.0,
    "upload_bytes": 400, "download_bytes": 400, "upload_download_ratio": 1.0,
    "unique_dest_ports": 1, "unique_dest_ips": 1,
    "port_entropy": 0.2, "ip_entropy": 0.1, "mean_dest_port": 1883
})
dos_sensor = dict(sensor_base)
dos_sensor.update({
    "packet_rate": 50000, "packet_count": 4500000,
    "byte_rate": 2000000, "syn_ratio": 0.90
})
r2 = post("/analyze", {"features": dos_sensor, "source_ip": "192.168.1.99"})
fp = r2["fingerprint"]; an = r2["anomaly"]
print(f"DoS on motion_sensor: device={fp['device_type']} conf={fp['confidence']:.4f}  score={an['anomaly_score']:.4f}  anomalous={an['is_anomalous']}  severity={an['severity']}")
