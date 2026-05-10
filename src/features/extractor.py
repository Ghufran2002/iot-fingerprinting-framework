"""37 statistical and protocol-level features for IoT network flows."""

FEATURE_NAMES = [
    # Temporal (5)
    'flow_duration', 'mean_iat', 'std_iat', 'min_iat', 'max_iat',
    # Volume (4)
    'packet_count', 'byte_count', 'packet_rate', 'byte_rate',
    # Packet Size (4)
    'mean_pkt_size', 'std_pkt_size', 'min_pkt_size', 'max_pkt_size',
    # Protocol Flags (6)
    'tcp_ratio', 'udp_ratio', 'syn_ratio', 'fin_ratio', 'rst_ratio', 'ack_ratio',
    # Application Layer (8)
    'is_https', 'is_mqtt', 'is_coap', 'is_mdns', 'is_ntp',
    'dns_query_count', 'well_known_port_ratio', 'is_encrypted',
    # Traffic Direction (3)
    'upload_bytes', 'download_bytes', 'upload_download_ratio',
    # Destination (7)
    'unique_dest_ports', 'unique_dest_ips', 'port_entropy', 'ip_entropy',
    'well_known_ports_count', 'mean_dest_port', 'std_dest_port',
]

FEATURE_CATEGORIES = {
    'Temporal':          ['flow_duration', 'mean_iat', 'std_iat', 'min_iat', 'max_iat'],
    'Volume':            ['packet_count', 'byte_count', 'packet_rate', 'byte_rate'],
    'Packet Size':       ['mean_pkt_size', 'std_pkt_size', 'min_pkt_size', 'max_pkt_size'],
    'Protocol Flags':    ['tcp_ratio', 'udp_ratio', 'syn_ratio', 'fin_ratio', 'rst_ratio', 'ack_ratio'],
    'Application Layer': ['is_https', 'is_mqtt', 'is_coap', 'is_mdns', 'is_ntp',
                          'dns_query_count', 'well_known_port_ratio', 'is_encrypted'],
    'Traffic Direction': ['upload_bytes', 'download_bytes', 'upload_download_ratio'],
    'Destination':       ['unique_dest_ports', 'unique_dest_ips', 'port_entropy', 'ip_entropy',
                          'well_known_ports_count', 'mean_dest_port', 'std_dest_port'],
}

DEVICE_TYPES = [
    'smart_camera', 'smart_thermostat', 'smart_tv', 'smart_bulb',
    'smart_plug', 'smart_speaker', 'smart_doorbell', 'motion_sensor'
]

DEVICE_LABEL_MAP = {name: idx for idx, name in enumerate(DEVICE_TYPES)}
LABEL_DEVICE_MAP = {idx: name for name, idx in DEVICE_LABEL_MAP.items()}

assert len(FEATURE_NAMES) == 37, f"Expected 37 features, got {len(FEATURE_NAMES)}"
