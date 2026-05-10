"""
Synthetic IoT network flow dataset generator.
Generates 1,600 labelled flows (200 per device) with 5% anomaly injection.
Each device profile is statistically distinct across all 37 features.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from src.features.extractor import FEATURE_NAMES, DEVICE_TYPES

np.random.seed(42)

FLOWS_PER_DEVICE = 200
ANOMALY_FRACTION = 0.05
DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def _clip_normal(mean, std, lo, hi, n):
    out = []
    while len(out) < n:
        v = np.random.normal(mean, std, n * 3)
        v = v[(v >= lo) & (v <= hi)]
        out.extend(v.tolist())
    return np.array(out[:n])


def _bern(p, n):
    return (np.random.rand(n) < p).astype(float)


# ---------------------------------------------------------------------------
# Per-device normal flow profiles
# ---------------------------------------------------------------------------
def _profile_smart_camera(n):
    d = {}
    d['flow_duration']         = _clip_normal(90, 30, 10, 300, n)
    d['mean_iat']              = _clip_normal(0.003, 0.001, 0.0005, 0.01, n)
    d['std_iat']               = _clip_normal(0.002, 0.0005, 0.0001, 0.008, n)
    d['min_iat']               = _clip_normal(0.001, 0.0003, 0.00005, 0.004, n)
    d['max_iat']               = _clip_normal(0.015, 0.003, 0.005, 0.05, n)
    d['packet_count']          = _clip_normal(28000, 4000, 10000, 60000, n)
    d['byte_count']            = _clip_normal(42_000_000, 8_000_000, 15_000_000, 80_000_000, n)
    d['packet_rate']           = _clip_normal(400, 60, 150, 700, n)
    d['byte_rate']             = _clip_normal(600_000, 90_000, 200_000, 1_200_000, n)
    d['mean_pkt_size']         = _clip_normal(1400, 80, 1000, 1500, n)
    d['std_pkt_size']          = _clip_normal(180, 30, 50, 400, n)
    d['min_pkt_size']          = _clip_normal(64, 10, 40, 128, n)
    d['max_pkt_size']          = _clip_normal(1500, 2, 1480, 1500, n)
    d['tcp_ratio']             = _clip_normal(0.95, 0.02, 0.85, 1.0, n)
    d['udp_ratio']             = 1 - d['tcp_ratio']
    d['syn_ratio']             = _clip_normal(0.005, 0.002, 0.0, 0.02, n)
    d['fin_ratio']             = _clip_normal(0.004, 0.001, 0.0, 0.015, n)
    d['rst_ratio']             = _clip_normal(0.001, 0.0005, 0.0, 0.005, n)
    d['ack_ratio']             = _clip_normal(0.60, 0.05, 0.4, 0.8, n)
    d['is_https']              = _bern(0.92, n)
    d['is_mqtt']               = _bern(0.01, n)
    d['is_coap']               = _bern(0.01, n)
    d['is_mdns']               = _bern(0.05, n)
    d['is_ntp']                = _bern(0.04, n)
    d['dns_query_count']       = _clip_normal(4, 1, 1, 10, n)
    d['well_known_port_ratio'] = _clip_normal(0.90, 0.03, 0.8, 1.0, n)
    d['is_encrypted']          = _bern(0.92, n)
    d['upload_bytes']          = _clip_normal(28_000_000, 5_000_000, 10_000_000, 60_000_000, n)
    d['download_bytes']        = d['byte_count'] - d['upload_bytes']
    d['upload_download_ratio'] = d['upload_bytes'] / (d['download_bytes'] + 1)
    d['unique_dest_ports']     = _clip_normal(4, 1, 2, 8, n).astype(int)
    d['unique_dest_ips']       = _clip_normal(3, 1, 1, 6, n).astype(int)
    d['port_entropy']          = _clip_normal(1.2, 0.3, 0.5, 3.0, n)
    d['ip_entropy']            = _clip_normal(1.0, 0.2, 0.3, 2.5, n)
    d['well_known_ports_count']= _clip_normal(3, 0.8, 1, 6, n).astype(int)
    d['mean_dest_port']        = _clip_normal(443, 10, 400, 500, n)
    d['std_dest_port']         = _clip_normal(30, 8, 5, 100, n)
    return d


def _profile_smart_thermostat(n):
    d = {}
    d['flow_duration']         = _clip_normal(4, 2, 0.5, 15, n)
    d['mean_iat']              = _clip_normal(0.8, 0.2, 0.1, 3.0, n)
    d['std_iat']               = _clip_normal(0.3, 0.1, 0.01, 1.0, n)
    d['min_iat']               = _clip_normal(0.05, 0.02, 0.005, 0.2, n)
    d['max_iat']               = _clip_normal(5.0, 1.0, 1.0, 15.0, n)
    d['packet_count']          = _clip_normal(8, 3, 2, 20, n).astype(int)
    d['byte_count']            = _clip_normal(800, 200, 100, 2000, n)
    d['packet_rate']           = _clip_normal(2, 1, 0.5, 6, n)
    d['byte_rate']             = _clip_normal(200, 80, 30, 600, n)
    d['mean_pkt_size']         = _clip_normal(85, 15, 40, 150, n)
    d['std_pkt_size']          = _clip_normal(20, 5, 5, 50, n)
    d['min_pkt_size']          = _clip_normal(40, 8, 20, 70, n)
    d['max_pkt_size']          = _clip_normal(200, 30, 100, 400, n)
    d['tcp_ratio']             = _clip_normal(0.15, 0.05, 0.0, 0.4, n)
    d['udp_ratio']             = 1 - d['tcp_ratio']
    d['syn_ratio']             = _clip_normal(0.05, 0.02, 0.0, 0.15, n)
    d['fin_ratio']             = _clip_normal(0.04, 0.01, 0.0, 0.12, n)
    d['rst_ratio']             = _clip_normal(0.01, 0.005, 0.0, 0.03, n)
    d['ack_ratio']             = _clip_normal(0.10, 0.03, 0.0, 0.25, n)
    d['is_https']              = _bern(0.08, n)
    d['is_mqtt']               = _bern(0.90, n)
    d['is_coap']               = _bern(0.05, n)
    d['is_mdns']               = _bern(0.02, n)
    d['is_ntp']                = _bern(0.05, n)
    d['dns_query_count']       = _clip_normal(1, 0.5, 0, 3, n)
    d['well_known_port_ratio'] = _clip_normal(0.60, 0.08, 0.4, 0.85, n)
    d['is_encrypted']          = _bern(0.05, n)
    d['upload_bytes']          = _clip_normal(400, 120, 50, 1000, n)
    d['download_bytes']        = d['byte_count'] - d['upload_bytes']
    d['upload_download_ratio'] = d['upload_bytes'] / (d['download_bytes'] + 1)
    d['unique_dest_ports']     = _clip_normal(1.5, 0.5, 1, 4, n).astype(int)
    d['unique_dest_ips']       = _clip_normal(1.2, 0.4, 1, 3, n).astype(int)
    d['port_entropy']          = _clip_normal(0.4, 0.15, 0.0, 1.2, n)
    d['ip_entropy']            = _clip_normal(0.2, 0.08, 0.0, 0.8, n)
    d['well_known_ports_count']= _clip_normal(1.5, 0.5, 1, 3, n).astype(int)
    d['mean_dest_port']        = _clip_normal(1883, 20, 1800, 1960, n)
    d['std_dest_port']         = _clip_normal(10, 3, 1, 30, n)
    return d


def _profile_smart_tv(n):
    d = {}
    d['flow_duration']         = _clip_normal(3600, 900, 300, 7200, n)
    d['mean_iat']              = _clip_normal(0.001, 0.0003, 0.0002, 0.005, n)
    d['std_iat']               = _clip_normal(0.0008, 0.0002, 0.0001, 0.003, n)
    d['min_iat']               = _clip_normal(0.0005, 0.0001, 0.00005, 0.002, n)
    d['max_iat']               = _clip_normal(0.05, 0.01, 0.01, 0.2, n)
    d['packet_count']          = _clip_normal(500_000, 80_000, 150_000, 1_000_000, n)
    d['byte_count']            = _clip_normal(700_000_000, 100_000_000, 200_000_000, 1_500_000_000, n)
    d['packet_rate']           = _clip_normal(140, 20, 60, 280, n)
    d['byte_rate']             = _clip_normal(200_000, 30_000, 80_000, 450_000, n)
    d['mean_pkt_size']         = _clip_normal(1400, 60, 1100, 1500, n)
    d['std_pkt_size']          = _clip_normal(200, 40, 80, 450, n)
    d['min_pkt_size']          = _clip_normal(64, 10, 40, 128, n)
    d['max_pkt_size']          = _clip_normal(1500, 2, 1480, 1500, n)
    d['tcp_ratio']             = _clip_normal(0.85, 0.05, 0.65, 0.98, n)
    d['udp_ratio']             = 1 - d['tcp_ratio']
    d['syn_ratio']             = _clip_normal(0.003, 0.001, 0.0, 0.01, n)
    d['fin_ratio']             = _clip_normal(0.002, 0.0008, 0.0, 0.008, n)
    d['rst_ratio']             = _clip_normal(0.001, 0.0003, 0.0, 0.004, n)
    d['ack_ratio']             = _clip_normal(0.55, 0.04, 0.4, 0.72, n)
    d['is_https']              = _bern(0.88, n)
    d['is_mqtt']               = _bern(0.01, n)
    d['is_coap']               = _bern(0.00, n)
    d['is_mdns']               = _bern(0.10, n)
    d['is_ntp']                = _bern(0.05, n)
    d['dns_query_count']       = _clip_normal(20, 5, 5, 50, n)
    d['well_known_port_ratio'] = _clip_normal(0.92, 0.03, 0.8, 1.0, n)
    d['is_encrypted']          = _bern(0.88, n)
    d['upload_bytes']          = _clip_normal(5_000_000, 1_000_000, 1_000_000, 15_000_000, n)
    d['download_bytes']        = d['byte_count'] - d['upload_bytes']
    d['upload_download_ratio'] = d['upload_bytes'] / (d['download_bytes'] + 1)
    d['unique_dest_ports']     = _clip_normal(12, 3, 5, 25, n).astype(int)
    d['unique_dest_ips']       = _clip_normal(18, 4, 8, 40, n).astype(int)
    d['port_entropy']          = _clip_normal(2.8, 0.3, 1.5, 4.0, n)
    d['ip_entropy']            = _clip_normal(3.0, 0.3, 1.8, 4.2, n)
    d['well_known_ports_count']= _clip_normal(10, 2, 5, 20, n).astype(int)
    d['mean_dest_port']        = _clip_normal(443, 5, 420, 470, n)
    d['std_dest_port']         = _clip_normal(150, 30, 50, 350, n)
    return d


def _profile_smart_bulb(n):
    d = {}
    d['flow_duration']         = _clip_normal(0.5, 0.2, 0.05, 2.0, n)
    d['mean_iat']              = _clip_normal(0.05, 0.02, 0.01, 0.2, n)
    d['std_iat']               = _clip_normal(0.02, 0.008, 0.001, 0.08, n)
    d['min_iat']               = _clip_normal(0.01, 0.004, 0.001, 0.04, n)
    d['max_iat']               = _clip_normal(0.3, 0.08, 0.05, 1.0, n)
    d['packet_count']          = _clip_normal(4, 1.5, 1, 10, n).astype(int)
    d['byte_count']            = _clip_normal(120, 40, 30, 350, n)
    d['packet_rate']           = _clip_normal(8, 3, 1, 20, n)
    d['byte_rate']             = _clip_normal(240, 90, 40, 600, n)
    d['mean_pkt_size']         = _clip_normal(30, 8, 15, 60, n)
    d['std_pkt_size']          = _clip_normal(8, 3, 1, 20, n)
    d['min_pkt_size']          = _clip_normal(18, 3, 10, 30, n)
    d['max_pkt_size']          = _clip_normal(60, 10, 30, 120, n)
    d['tcp_ratio']             = _clip_normal(0.05, 0.02, 0.0, 0.15, n)
    d['udp_ratio']             = 1 - d['tcp_ratio']
    d['syn_ratio']             = _clip_normal(0.02, 0.008, 0.0, 0.06, n)
    d['fin_ratio']             = _clip_normal(0.02, 0.008, 0.0, 0.06, n)
    d['rst_ratio']             = _clip_normal(0.005, 0.002, 0.0, 0.015, n)
    d['ack_ratio']             = _clip_normal(0.05, 0.02, 0.0, 0.15, n)
    d['is_https']              = _bern(0.02, n)
    d['is_mqtt']               = _bern(0.05, n)
    d['is_coap']               = _bern(0.92, n)
    d['is_mdns']               = _bern(0.03, n)
    d['is_ntp']                = _bern(0.02, n)
    d['dns_query_count']       = _clip_normal(0.3, 0.2, 0, 2, n)
    d['well_known_port_ratio'] = _clip_normal(0.40, 0.08, 0.2, 0.65, n)
    d['is_encrypted']          = _bern(0.02, n)
    d['upload_bytes']          = _clip_normal(60, 20, 10, 180, n)
    d['download_bytes']        = d['byte_count'] - d['upload_bytes']
    d['upload_download_ratio'] = d['upload_bytes'] / (d['download_bytes'] + 1)
    d['unique_dest_ports']     = _clip_normal(1.1, 0.3, 1, 3, n).astype(int)
    d['unique_dest_ips']       = _clip_normal(1.05, 0.2, 1, 2, n).astype(int)
    d['port_entropy']          = _clip_normal(0.05, 0.02, 0.0, 0.2, n)
    d['ip_entropy']            = _clip_normal(0.05, 0.02, 0.0, 0.2, n)
    d['well_known_ports_count']= _clip_normal(1, 0.2, 1, 2, n).astype(int)
    d['mean_dest_port']        = _clip_normal(5683, 10, 5650, 5720, n)
    d['std_dest_port']         = _clip_normal(3, 1, 0, 10, n)
    return d


def _profile_smart_plug(n):
    d = {}
    d['flow_duration']         = _clip_normal(1.5, 0.5, 0.2, 5.0, n)
    d['mean_iat']              = _clip_normal(0.2, 0.06, 0.03, 0.6, n)
    d['std_iat']               = _clip_normal(0.08, 0.03, 0.005, 0.25, n)
    d['min_iat']               = _clip_normal(0.03, 0.01, 0.005, 0.1, n)
    d['max_iat']               = _clip_normal(1.5, 0.4, 0.3, 4.0, n)
    d['packet_count']          = _clip_normal(6, 2, 2, 15, n).astype(int)
    d['byte_count']            = _clip_normal(300, 100, 60, 800, n)
    d['packet_rate']           = _clip_normal(4, 1.5, 1, 10, n)
    d['byte_rate']             = _clip_normal(200, 70, 40, 500, n)
    d['mean_pkt_size']         = _clip_normal(50, 12, 20, 100, n)
    d['std_pkt_size']          = _clip_normal(12, 4, 2, 30, n)
    d['min_pkt_size']          = _clip_normal(25, 6, 10, 45, n)
    d['max_pkt_size']          = _clip_normal(120, 20, 60, 250, n)
    d['tcp_ratio']             = _clip_normal(0.25, 0.08, 0.05, 0.5, n)
    d['udp_ratio']             = 1 - d['tcp_ratio']
    d['syn_ratio']             = _clip_normal(0.08, 0.03, 0.01, 0.2, n)
    d['fin_ratio']             = _clip_normal(0.07, 0.025, 0.01, 0.18, n)
    d['rst_ratio']             = _clip_normal(0.02, 0.008, 0.0, 0.06, n)
    d['ack_ratio']             = _clip_normal(0.12, 0.04, 0.03, 0.28, n)
    d['is_https']              = _bern(0.15, n)
    d['is_mqtt']               = _bern(0.30, n)
    d['is_coap']               = _bern(0.20, n)
    d['is_mdns']               = _bern(0.05, n)
    d['is_ntp']                = _bern(0.04, n)
    d['dns_query_count']       = _clip_normal(0.5, 0.3, 0, 2, n)
    d['well_known_port_ratio'] = _clip_normal(0.55, 0.08, 0.35, 0.75, n)
    d['is_encrypted']          = _bern(0.12, n)
    d['upload_bytes']          = _clip_normal(150, 50, 30, 400, n)
    d['download_bytes']        = d['byte_count'] - d['upload_bytes']
    d['upload_download_ratio'] = d['upload_bytes'] / (d['download_bytes'] + 1)
    d['unique_dest_ports']     = _clip_normal(1.5, 0.5, 1, 4, n).astype(int)
    d['unique_dest_ips']       = _clip_normal(1.3, 0.4, 1, 3, n).astype(int)
    d['port_entropy']          = _clip_normal(0.3, 0.1, 0.0, 0.9, n)
    d['ip_entropy']            = _clip_normal(0.2, 0.08, 0.0, 0.6, n)
    d['well_known_ports_count']= _clip_normal(1.5, 0.5, 1, 3, n).astype(int)
    d['mean_dest_port']        = _clip_normal(8883, 20, 8800, 8950, n)
    d['std_dest_port']         = _clip_normal(8, 3, 0, 25, n)
    return d


def _profile_smart_speaker(n):
    d = {}
    d['flow_duration']         = _clip_normal(15, 8, 1, 60, n)
    d['mean_iat']              = _clip_normal(0.02, 0.008, 0.003, 0.08, n)
    d['std_iat']               = _clip_normal(0.015, 0.005, 0.001, 0.06, n)
    d['min_iat']               = _clip_normal(0.005, 0.002, 0.0005, 0.02, n)
    d['max_iat']               = _clip_normal(0.8, 0.2, 0.1, 3.0, n)
    d['packet_count']          = _clip_normal(1500, 400, 200, 5000, n)
    d['byte_count']            = _clip_normal(800_000, 200_000, 100_000, 2_500_000, n)
    d['packet_rate']           = _clip_normal(100, 25, 20, 250, n)
    d['byte_rate']             = _clip_normal(55_000, 12_000, 8_000, 150_000, n)
    d['mean_pkt_size']         = _clip_normal(550, 80, 300, 900, n)
    d['std_pkt_size']          = _clip_normal(150, 30, 40, 350, n)
    d['min_pkt_size']          = _clip_normal(64, 10, 40, 128, n)
    d['max_pkt_size']          = _clip_normal(1460, 30, 1200, 1500, n)
    d['tcp_ratio']             = _clip_normal(0.55, 0.08, 0.3, 0.80, n)
    d['udp_ratio']             = 1 - d['tcp_ratio']
    d['syn_ratio']             = _clip_normal(0.012, 0.004, 0.002, 0.04, n)
    d['fin_ratio']             = _clip_normal(0.010, 0.003, 0.001, 0.03, n)
    d['rst_ratio']             = _clip_normal(0.003, 0.001, 0.0, 0.01, n)
    d['ack_ratio']             = _clip_normal(0.38, 0.05, 0.2, 0.55, n)
    d['is_https']              = _bern(0.82, n)
    d['is_mqtt']               = _bern(0.05, n)
    d['is_coap']               = _bern(0.01, n)
    d['is_mdns']               = _bern(0.12, n)
    d['is_ntp']                = _bern(0.05, n)
    d['dns_query_count']       = _clip_normal(8, 2, 2, 20, n)
    d['well_known_port_ratio'] = _clip_normal(0.88, 0.04, 0.75, 0.98, n)
    d['is_encrypted']          = _bern(0.82, n)
    d['upload_bytes']          = _clip_normal(120_000, 30_000, 20_000, 400_000, n)
    d['download_bytes']        = d['byte_count'] - d['upload_bytes']
    d['upload_download_ratio'] = d['upload_bytes'] / (d['download_bytes'] + 1)
    d['unique_dest_ports']     = _clip_normal(6, 2, 3, 12, n).astype(int)
    d['unique_dest_ips']       = _clip_normal(5, 2, 2, 12, n).astype(int)
    d['port_entropy']          = _clip_normal(1.8, 0.3, 0.8, 3.0, n)
    d['ip_entropy']            = _clip_normal(1.6, 0.3, 0.6, 2.8, n)
    d['well_known_ports_count']= _clip_normal(5, 1.5, 2, 10, n).astype(int)
    d['mean_dest_port']        = _clip_normal(443, 8, 420, 470, n)
    d['std_dest_port']         = _clip_normal(80, 20, 20, 200, n)
    return d


def _profile_smart_doorbell(n):
    d = {}
    d['flow_duration']         = _clip_normal(30, 15, 2, 120, n)
    d['mean_iat']              = _clip_normal(0.008, 0.003, 0.001, 0.03, n)
    d['std_iat']               = _clip_normal(0.02, 0.008, 0.002, 0.08, n)
    d['min_iat']               = _clip_normal(0.002, 0.0008, 0.0002, 0.01, n)
    d['max_iat']               = _clip_normal(0.5, 0.15, 0.05, 2.0, n)
    d['packet_count']          = _clip_normal(5000, 2000, 500, 20000, n)
    d['byte_count']            = _clip_normal(4_000_000, 1_500_000, 400_000, 15_000_000, n)
    d['packet_rate']           = _clip_normal(180, 60, 30, 500, n)
    d['byte_rate']             = _clip_normal(140_000, 50_000, 15_000, 500_000, n)
    d['mean_pkt_size']         = _clip_normal(850, 120, 400, 1400, n)
    d['std_pkt_size']          = _clip_normal(350, 70, 100, 700, n)
    d['min_pkt_size']          = _clip_normal(64, 10, 40, 128, n)
    d['max_pkt_size']          = _clip_normal(1500, 5, 1460, 1500, n)
    d['tcp_ratio']             = _clip_normal(0.75, 0.07, 0.5, 0.95, n)
    d['udp_ratio']             = 1 - d['tcp_ratio']
    d['syn_ratio']             = _clip_normal(0.008, 0.003, 0.001, 0.025, n)
    d['fin_ratio']             = _clip_normal(0.007, 0.002, 0.001, 0.02, n)
    d['rst_ratio']             = _clip_normal(0.003, 0.001, 0.0, 0.01, n)
    d['ack_ratio']             = _clip_normal(0.50, 0.06, 0.3, 0.68, n)
    d['is_https']              = _bern(0.78, n)
    d['is_mqtt']               = _bern(0.04, n)
    d['is_coap']               = _bern(0.02, n)
    d['is_mdns']               = _bern(0.08, n)
    d['is_ntp']                = _bern(0.04, n)
    d['dns_query_count']       = _clip_normal(5, 2, 1, 15, n)
    d['well_known_port_ratio'] = _clip_normal(0.85, 0.04, 0.72, 0.97, n)
    d['is_encrypted']          = _bern(0.78, n)
    d['upload_bytes']          = _clip_normal(2_500_000, 900_000, 200_000, 9_000_000, n)
    d['download_bytes']        = d['byte_count'] - d['upload_bytes']
    d['upload_download_ratio'] = d['upload_bytes'] / (d['download_bytes'] + 1)
    d['unique_dest_ports']     = _clip_normal(5, 2, 2, 10, n).astype(int)
    d['unique_dest_ips']       = _clip_normal(3, 1, 1, 8, n).astype(int)
    d['port_entropy']          = _clip_normal(1.5, 0.3, 0.5, 2.8, n)
    d['ip_entropy']            = _clip_normal(1.1, 0.25, 0.3, 2.2, n)
    d['well_known_ports_count']= _clip_normal(4, 1, 2, 8, n).astype(int)
    d['mean_dest_port']        = _clip_normal(443, 8, 420, 470, n)
    d['std_dest_port']         = _clip_normal(60, 15, 10, 150, n)
    return d


def _profile_motion_sensor(n):
    d = {}
    d['flow_duration']         = _clip_normal(0.3, 0.1, 0.05, 1.0, n)
    d['mean_iat']              = _clip_normal(0.08, 0.03, 0.01, 0.3, n)
    d['std_iat']               = _clip_normal(0.04, 0.015, 0.002, 0.15, n)
    d['min_iat']               = _clip_normal(0.01, 0.004, 0.001, 0.05, n)
    d['max_iat']               = _clip_normal(0.8, 0.25, 0.1, 2.5, n)
    d['packet_count']          = _clip_normal(3, 1, 1, 8, n).astype(int)
    d['byte_count']            = _clip_normal(80, 25, 20, 200, n)
    d['packet_rate']           = _clip_normal(10, 4, 2, 25, n)
    d['byte_rate']             = _clip_normal(270, 100, 50, 700, n)
    d['mean_pkt_size']         = _clip_normal(27, 7, 10, 50, n)
    d['std_pkt_size']          = _clip_normal(6, 2, 1, 15, n)
    d['min_pkt_size']          = _clip_normal(14, 3, 8, 25, n)
    d['max_pkt_size']          = _clip_normal(55, 10, 25, 100, n)
    d['tcp_ratio']             = _clip_normal(0.04, 0.015, 0.0, 0.12, n)
    d['udp_ratio']             = 1 - d['tcp_ratio']
    d['syn_ratio']             = _clip_normal(0.015, 0.005, 0.0, 0.05, n)
    d['fin_ratio']             = _clip_normal(0.012, 0.004, 0.0, 0.04, n)
    d['rst_ratio']             = _clip_normal(0.004, 0.001, 0.0, 0.012, n)
    d['ack_ratio']             = _clip_normal(0.04, 0.015, 0.0, 0.12, n)
    d['is_https']              = _bern(0.02, n)
    d['is_mqtt']               = _bern(0.40, n)
    d['is_coap']               = _bern(0.50, n)
    d['is_mdns']               = _bern(0.03, n)
    d['is_ntp']                = _bern(0.02, n)
    d['dns_query_count']       = _clip_normal(0.2, 0.15, 0, 1, n)
    d['well_known_port_ratio'] = _clip_normal(0.35, 0.08, 0.15, 0.60, n)
    d['is_encrypted']          = _bern(0.02, n)
    d['upload_bytes']          = _clip_normal(45, 15, 10, 120, n)
    d['download_bytes']        = d['byte_count'] - d['upload_bytes']
    d['upload_download_ratio'] = d['upload_bytes'] / (d['download_bytes'] + 1)
    d['unique_dest_ports']     = _clip_normal(1.05, 0.2, 1, 2, n).astype(int)
    d['unique_dest_ips']       = _clip_normal(1.02, 0.14, 1, 2, n).astype(int)
    d['port_entropy']          = _clip_normal(0.02, 0.01, 0.0, 0.08, n)
    d['ip_entropy']            = _clip_normal(0.02, 0.01, 0.0, 0.08, n)
    d['well_known_ports_count']= _clip_normal(1.0, 0.1, 1, 2, n).astype(int)
    d['mean_dest_port']        = _clip_normal(1884, 5, 1875, 1900, n)
    d['std_dest_port']         = _clip_normal(2, 0.8, 0, 8, n)
    return d


_PROFILE_FNS = {
    'smart_camera':     _profile_smart_camera,
    'smart_thermostat': _profile_smart_thermostat,
    'smart_tv':         _profile_smart_tv,
    'smart_bulb':       _profile_smart_bulb,
    'smart_plug':       _profile_smart_plug,
    'smart_speaker':    _profile_smart_speaker,
    'smart_doorbell':   _profile_smart_doorbell,
    'motion_sensor':    _profile_motion_sensor,
}


def _inject_anomaly(row: dict, anomaly_type: str) -> dict:
    r = dict(row)
    if anomaly_type == 'data_exfiltration':
        r['upload_bytes']          *= np.random.uniform(30, 80)
        r['byte_rate']             *= np.random.uniform(25, 60)
        r['byte_count']            *= np.random.uniform(20, 50)
        r['upload_download_ratio'] *= np.random.uniform(15, 40)
    elif anomaly_type == 'port_scan':
        r['unique_dest_ports'] = int(np.random.uniform(500, 1500))
        r['port_entropy']      = np.random.uniform(8.0, 10.0)
        r['ip_entropy']        = np.random.uniform(7.0, 9.0)
        r['packet_count']      *= np.random.uniform(20, 50)
        r['unique_dest_ips']   = int(np.random.uniform(100, 300))
    elif anomaly_type == 'dos_participation':
        r['packet_rate']    *= np.random.uniform(50, 120)
        r['packet_count']   *= np.random.uniform(40, 100)
        r['byte_rate']      *= np.random.uniform(40, 90)
        r['syn_ratio']      = min(1.0, r.get('syn_ratio', 0.01) * 30)
    return r


def generate_dataset(save: bool = True) -> pd.DataFrame:
    all_rows = []
    anomaly_types = ['data_exfiltration', 'port_scan', 'dos_participation']

    for device in DEVICE_TYPES:
        n_normal  = FLOWS_PER_DEVICE - int(FLOWS_PER_DEVICE * ANOMALY_FRACTION)
        n_anomaly = int(FLOWS_PER_DEVICE * ANOMALY_FRACTION)

        profile_data = _PROFILE_FNS[device](FLOWS_PER_DEVICE)
        records = []
        for i in range(FLOWS_PER_DEVICE):
            row = {feat: float(profile_data[feat][i]) for feat in FEATURE_NAMES}
            row['device_type'] = device
            if i >= n_normal:
                atype = anomaly_types[i % len(anomaly_types)]
                row = _inject_anomaly(row, atype)
                row['is_anomaly'] = 1
                row['anomaly_type'] = atype
            else:
                row['is_anomaly'] = 0
                row['anomaly_type'] = 'normal'
            records.append(row)
        all_rows.extend(records)

    df = pd.DataFrame(all_rows)
    df = df.reset_index(drop=True)

    if save:
        DATA_DIR.mkdir(exist_ok=True)
        df.to_csv(DATA_DIR / "iot_flows.csv", index=False)

    return df


if __name__ == "__main__":
    df = generate_dataset()
    print(f"Dataset shape: {df.shape}")
    print(df.groupby('device_type')['is_anomaly'].value_counts())
