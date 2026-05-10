"""
N-BaIoT real IoT dataset loader.

Dataset: "Detection of IoT Botnet Attacks N-BaIoT"
Source:  https://archive.ics.uci.edu/dataset/442
Format:  Pre-extracted 115 statistical features per flow (no raw PCAPs needed)
Size:    ~1.7 GB zipped (downloaded), benign CSVs + attack RARs extracted

9 real IoT devices → mapped to our 8 device types:
  Danmini_Doorbell              → smart_doorbell
  Ecobee_Thermostat             → smart_thermostat
  Provision_PT_737E_Security_Camera        → smart_camera
  Provision_PT_838_Security_Camera         → smart_speaker
  Samsung_SNH_1011_N_Webcam               → smart_tv
  Philips_B120N10_Baby_Monitor             → smart_bulb
  SimpleHome_XCS7_1002_WHT_Security_Camera → smart_plug
  SimpleHome_XCS7_1003_WHT_Security_Camera → smart_plug
  Ennio_Doorbell                → motion_sensor

Attack types (from RAR archives):
  mirai_attacks/  → ack, scan, syn, udp, udpplain
  gafgyt_attacks/ → combo, junk, scan, tcp, udp
"""
import io
import zipfile
import requests
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional, Tuple, Set

from src.features.extractor import FEATURE_NAMES, DEVICE_TYPES
from src.utils.logger import logger

DATA_DIR   = Path(__file__).resolve().parents[2] / "data"
NBAIOT_DIR = DATA_DIR / "nbaiot"

_UCI_ZIP_URL = (
    "https://archive.ics.uci.edu/static/public/442/"
    "detection+of+iot+botnet+attacks+n+baiot.zip"
)

_DEVICE_MAP = {
    "Danmini_Doorbell":                          "smart_doorbell",
    "Ecobee_Thermostat":                         "smart_thermostat",
    "Provision_PT_737E_Security_Camera":         "smart_camera",
    "Provision_PT_838_Security_Camera":          "smart_speaker",
    "Samsung_SNH_1011_N_Webcam":                 "smart_tv",
    "Philips_B120N10_Baby_Monitor":              "smart_bulb",
    "SimpleHome_XCS7_1002_WHT_Security_Camera":  "smart_plug",
    "SimpleHome_XCS7_1003_WHT_Security_Camera":  "smart_plug",
    "Ennio_Doorbell":                            "motion_sensor",
}

# Known protocol characteristics per device (not in N-BaIoT features)
_PROTO = {
    "smart_camera":     dict(tcp_ratio=0.95, is_https=1, is_mqtt=0, is_coap=0, is_encrypted=1, mean_dest_port=443),
    "smart_thermostat": dict(tcp_ratio=0.15, is_https=0, is_mqtt=1, is_coap=0, is_encrypted=0, mean_dest_port=1883),
    "smart_tv":         dict(tcp_ratio=0.87, is_https=1, is_mqtt=0, is_coap=0, is_encrypted=1, mean_dest_port=443),
    "smart_bulb":       dict(tcp_ratio=0.05, is_https=0, is_mqtt=0, is_coap=1, is_encrypted=0, mean_dest_port=5683),
    "smart_plug":       dict(tcp_ratio=0.25, is_https=0, is_mqtt=1, is_coap=0, is_encrypted=0, mean_dest_port=8883),
    "smart_speaker":    dict(tcp_ratio=0.55, is_https=1, is_mqtt=0, is_coap=0, is_encrypted=1, mean_dest_port=443),
    "smart_doorbell":   dict(tcp_ratio=0.75, is_https=1, is_mqtt=0, is_coap=0, is_encrypted=1, mean_dest_port=443),
    "motion_sensor":    dict(tcp_ratio=0.04, is_https=0, is_mqtt=1, is_coap=0, is_encrypted=0, mean_dest_port=1883),
}


# ---------------------------------------------------------------------------
# Downloader
# ---------------------------------------------------------------------------
def download_nbaiot(force: bool = False) -> bool:
    if NBAIOT_DIR.exists() and any(NBAIOT_DIR.rglob("benign_traffic.csv")) and not force:
        logger.info(f"N-BaIoT already at {NBAIOT_DIR}")
        return True

    NBAIOT_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Downloading N-BaIoT from UCI (~1.7 GB) — one-time download ...")

    try:
        resp = requests.get(_UCI_ZIP_URL, stream=True, timeout=120)
        resp.raise_for_status()
        zip_path = DATA_DIR / "nbaiot_raw.zip"
        downloaded = 0
        with open(zip_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
                downloaded += len(chunk)
                mb = downloaded // (1024 * 1024)
                if mb % 100 == 0 and mb > 0:
                    logger.info(f"  Downloaded {mb} MB ...")

        logger.info("Extracting ...")
        import zipfile as zf
        with zf.ZipFile(zip_path, "r") as z:
            z.extractall(NBAIOT_DIR)
        zip_path.unlink()
        logger.info(f"N-BaIoT ready at {NBAIOT_DIR}")
        return True

    except Exception as e:
        logger.error(f"Download failed: {e}")
        _print_manual_instructions()
        return False


def _print_manual_instructions():
    logger.warning("=" * 60)
    logger.warning("MANUAL DOWNLOAD:")
    logger.warning("  https://www.kaggle.com/datasets/mkashifn/nbaiot-dataset")
    logger.warning("  OR: https://archive.ics.uci.edu/dataset/442")
    logger.warning(f"  Extract to: {NBAIOT_DIR}")
    logger.warning("  Then run:   python train.py --hybrid")
    logger.warning("=" * 60)


# ---------------------------------------------------------------------------
# Feature mapper: N-BaIoT 115 features → our 37 features
# Columns confirmed: weight/mean/variance (for MI_, H_, HH_jit_)
#                    weight/mean/std/magnitude/radius/covariance/pcc (for HH_, HpHp_)
# ---------------------------------------------------------------------------
def _col(df: pd.DataFrame, name: str, default: float = 0.0) -> np.ndarray:
    if name in df.columns:
        return df[name].fillna(default).clip(lower=0).values
    return np.full(len(df), default)


def _map_to_37(raw: pd.DataFrame, device_type: str) -> pd.DataFrame:
    n    = len(raw)
    rng  = np.random.default_rng(42)
    p    = _PROTO.get(device_type, _PROTO["smart_camera"])

    # ---- N-BaIoT: weight = count of packets in time window (L5 = 5s) -------
    pkt_count_5s = _col(raw, "MI_dir_L5_weight", 1.0)          # packets in 5s
    pkt_size_mean = _col(raw, "MI_dir_L5_mean", 100.0)          # mean pkt size (bytes)
    pkt_size_var  = _col(raw, "MI_dir_L5_variance", 100.0)      # variance of pkt sizes
    pkt_size_std  = np.sqrt(np.maximum(pkt_size_var, 0))

    # ---- Temporal (5) -------------------------------------------------------
    flow_duration = np.full(n, 5.0)                              # L5 window = 5 seconds
    packet_rate   = pkt_count_5s / 5.0                          # pkt/sec
    mean_iat      = np.where(pkt_count_5s > 1,
                             5.0 / pkt_count_5s,
                             5.0)                                # avg seconds between pkts
    # jitter stats from HH (std of host-host IAT is a proxy)
    hh_std        = _col(raw, "HH_L5_std", 0.0)
    std_iat       = np.clip(hh_std * 0.001 + mean_iat * 0.15, 0.0001, mean_iat * 2)
    min_iat       = np.clip(mean_iat * 0.1, 0.00001, mean_iat)
    max_iat       = np.clip(mean_iat * 3.0, mean_iat, 60.0)

    # ---- Volume (4) ---------------------------------------------------------
    byte_count    = pkt_count_5s * pkt_size_mean
    byte_rate     = byte_count / 5.0

    # ---- Packet Size (4) ----------------------------------------------------
    min_pkt       = np.clip(pkt_size_mean - 2 * pkt_size_std, 14, 65535)
    max_pkt       = np.clip(pkt_size_mean + 2 * pkt_size_std, 14, 65535)

    # ---- Protocol Flags (6) -------------------------------------------------
    tcp  = np.full(n, p["tcp_ratio"])
    udp  = 1.0 - tcp
    syn  = rng.uniform(0.001, 0.02, n) * tcp
    fin  = rng.uniform(0.001, 0.015, n) * tcp
    rst  = rng.uniform(0.0005, 0.005, n) * tcp
    ack  = tcp * rng.uniform(0.4, 0.7, n)

    # ---- Application Layer (8) ----------------------------------------------
    is_https = np.full(n, float(p["is_https"]))
    is_mqtt  = np.full(n, float(p["is_mqtt"]))
    is_coap  = np.full(n, float(p["is_coap"]))
    is_mdns  = rng.binomial(1, 0.05, n).astype(float)
    is_ntp   = rng.binomial(1, 0.04, n).astype(float)
    # DNS queries inferred from HH_L5_weight (host connections in window)
    hh_w     = _col(raw, "HH_L5_weight", 1.0)
    dns_q    = np.clip(hh_w * 0.5, 0, 30)
    wkp_r    = np.full(n, 0.85 if p["is_https"] else 0.45)
    is_enc   = np.full(n, float(p["is_encrypted"]))

    # ---- Traffic Direction (3) ----------------------------------------------
    # Estimate upload vs download from HH magnitude vs MI magnitude
    hh_mag   = _col(raw, "HH_L5_magnitude", byte_count.mean())
    upload   = np.clip(hh_mag * 0.6, 0, byte_count * 0.95)
    download = np.clip(byte_count - upload, 0, byte_count)
    ul_dl    = np.where(download > 0, upload / (download + 1e-6), 1.0)

    # ---- Destination (7) ----------------------------------------------------
    hpHp_w   = _col(raw, "HpHp_L5_weight", 1.0)
    hpHp_pcc = _col(raw, "HpHp_L5_pcc", 0.0)
    hpHp_std = _col(raw, "HpHp_L5_std", 30.0)
    hh_pcc   = _col(raw, "HH_L5_pcc", 0.0)

    # unique dest ports ~ HpHp weight (each port pair = one "port slot")
    u_ports  = np.clip(hpHp_w * 1.5, 1, 500).astype(int)
    # unique dest IPs ~ HH weight
    u_ips    = np.clip(hh_w * 1.2, 1, 100).astype(int)
    port_ent = np.clip(np.abs(hpHp_pcc) * 2.0 + 0.3 * np.log1p(u_ports), 0, 10)
    ip_ent   = np.clip(np.abs(hh_pcc)   * 2.0 + 0.2 * np.log1p(u_ips),  0, 10)
    wkp_cnt  = np.clip(u_ports * wkp_r, 1, 50).astype(int)
    m_dp     = np.full(n, float(p["mean_dest_port"]))
    s_dp     = np.clip(hpHp_std, 0, 5000)

    result = pd.DataFrame({
        'flow_duration':          flow_duration,
        'mean_iat':               mean_iat,
        'std_iat':                std_iat,
        'min_iat':                min_iat,
        'max_iat':                max_iat,
        'packet_count':           pkt_count_5s,
        'byte_count':             byte_count,
        'packet_rate':            packet_rate,
        'byte_rate':              byte_rate,
        'mean_pkt_size':          pkt_size_mean,
        'std_pkt_size':           pkt_size_std,
        'min_pkt_size':           min_pkt,
        'max_pkt_size':           max_pkt,
        'tcp_ratio':              tcp,
        'udp_ratio':              udp,
        'syn_ratio':              syn,
        'fin_ratio':              fin,
        'rst_ratio':              rst,
        'ack_ratio':              ack,
        'is_https':               is_https,
        'is_mqtt':                is_mqtt,
        'is_coap':                is_coap,
        'is_mdns':                is_mdns,
        'is_ntp':                 is_ntp,
        'dns_query_count':        dns_q,
        'well_known_port_ratio':  wkp_r,
        'is_encrypted':           is_enc,
        'upload_bytes':           upload,
        'download_bytes':         download,
        'upload_download_ratio':  ul_dl,
        'unique_dest_ports':      u_ports.astype(float),
        'unique_dest_ips':        u_ips.astype(float),
        'port_entropy':           port_ent,
        'ip_entropy':             ip_ent,
        'well_known_ports_count': wkp_cnt.astype(float),
        'mean_dest_port':         m_dp,
        'std_dest_port':          s_dp,
    })

    assert list(result.columns) == FEATURE_NAMES
    return result


# ---------------------------------------------------------------------------
# Load benign CSV
# ---------------------------------------------------------------------------
def _load_benign(device_dir: Path, device_type: str,
                 max_rows: int = 2000) -> pd.DataFrame:
    benign = device_dir / "benign_traffic.csv"
    if not benign.exists():
        logger.warning(f"No benign_traffic.csv in {device_dir}")
        return pd.DataFrame()
    raw = pd.read_csv(benign, nrows=max_rows)
    raw.replace([np.inf, -np.inf], np.nan, inplace=True)
    raw.fillna(0, inplace=True)
    mapped = _map_to_37(raw, device_type)
    mapped['device_type']  = device_type
    mapped['is_anomaly']   = 0
    mapped['anomaly_type'] = 'normal'
    logger.info(f"  [{device_type}] {len(mapped):5d} normal flows from {device_dir.name}")
    return mapped


# ---------------------------------------------------------------------------
# Load attack CSVs from .rar archives  (uses 7-Zip, no unrar.exe needed)
# ---------------------------------------------------------------------------
_7ZIP = Path("C:/Program Files/7-Zip/7z.exe")


def _load_attacks(device_dir: Path, device_type: str,
                  max_per_rar: int = 50) -> pd.DataFrame:
    import subprocess, tempfile

    rar_files = list(device_dir.glob("*.rar"))
    if not rar_files:
        return pd.DataFrame()

    if not _7ZIP.exists():
        logger.warning("7-Zip not found at C:/Program Files/7-Zip/7z.exe — skipping attack data.")
        return pd.DataFrame()

    rows = []
    for rar_path in rar_files:
        attack_category = rar_path.stem
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [str(_7ZIP), "e", str(rar_path), f"-o{tmpdir}", "-y"],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.warning(f"  7z extraction failed for {rar_path.name}: {result.stderr[:200]}")
                continue

            csv_files = list(Path(tmpdir).glob("*.csv"))
            per_file  = max(5, max_per_rar // max(len(csv_files), 1))
            for csv_path in csv_files:
                try:
                    raw = pd.read_csv(csv_path, nrows=per_file)
                    raw.replace([np.inf, -np.inf], np.nan, inplace=True)
                    raw.fillna(0, inplace=True)
                    mapped = _map_to_37(raw, device_type)
                    mapped['device_type']  = device_type
                    mapped['is_anomaly']   = 1
                    mapped['anomaly_type'] = f"{attack_category}/{csv_path.stem}"
                    rows.append(mapped)
                except Exception as e:
                    logger.warning(f"  Skipping {csv_path.name}: {e}")

    if not rows:
        return pd.DataFrame()
    df = pd.concat(rows, ignore_index=True)
    logger.info(f"  [{device_type}] {len(df):5d} attack flows from {device_dir.name}")
    return df


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def load_real_dataset(
    nbaiot_root: Optional[Path] = None,
    n_normal: int = 2000,
    n_attack: int = 100,
) -> Tuple[pd.DataFrame, Set[str]]:
    """
    Load N-BaIoT real data. Returns (DataFrame, set_of_missing_device_types).
    """
    root = nbaiot_root or NBAIOT_DIR
    if not root.exists() or not any(root.rglob("benign_traffic.csv")):
        raise FileNotFoundError(
            f"N-BaIoT data not found at {root}.\n"
            "Run:  python train.py --download"
        )

    all_dfs     = []
    found_devs  = set()

    for folder_name, device_type in _DEVICE_MAP.items():
        dev_dir = root / folder_name
        if not dev_dir.exists():
            # case-insensitive search
            matches = [d for d in root.iterdir()
                       if d.is_dir() and d.name.lower() == folder_name.lower()]
            dev_dir = matches[0] if matches else None

        if dev_dir is None or not dev_dir.exists():
            logger.warning(f"Not found: {folder_name}")
            continue

        df_b = _load_benign(dev_dir, device_type, n_normal)
        df_a = _load_attacks(dev_dir, device_type, n_attack)

        for df_part in [df_b, df_a]:
            if len(df_part) > 0:
                all_dfs.append(df_part)
        if len(df_b) > 0:
            found_devs.add(device_type)

    if not all_dfs:
        raise RuntimeError("No N-BaIoT data loaded. Check folder structure.")

    df_real  = pd.concat(all_dfs, ignore_index=True)
    missing  = set(DEVICE_TYPES) - found_devs
    logger.info(f"Real data: {len(df_real)} total flows | {len(found_devs)} device types")
    if missing:
        logger.warning(f"Missing device types (synthetic fill-in): {missing}")
    return df_real, missing


def save_real_dataset(df: pd.DataFrame):
    DATA_DIR.mkdir(exist_ok=True)
    path = DATA_DIR / "iot_flows_real.csv"
    df.to_csv(path, index=False)
    logger.info(f"Saved: {path} ({len(df)} rows)")
