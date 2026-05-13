"""
Generates final presentation PPT for IoT Device Fingerprinting & Anomaly Detection Framework.
Output: IoT_Fingerprinting_Presentation.pptx
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt
import copy
from lxml import etree

# ── Palette ────────────────────────────────────────────────────────────────
C_BG      = RGBColor(0x0D, 0x0F, 0x14)
C_SURFACE = RGBColor(0x13, 0x16, 0x1E)
C_SURF2   = RGBColor(0x1A, 0x1E, 0x28)
C_BORDER  = RGBColor(0x1F, 0x25, 0x35)
C_CYAN    = RGBColor(0x00, 0xD4, 0xE8)
C_PURPLE  = RGBColor(0xA0, 0x5A, 0xFF)
C_GREEN   = RGBColor(0x00, 0xE5, 0x80)
C_YELLOW  = RGBColor(0xFF, 0xCD, 0x43)
C_RED     = RGBColor(0xFF, 0x47, 0x57)
C_WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
C_TEXT    = RGBColor(0xC9, 0xD1, 0xE0)
C_DIM     = RGBColor(0x6B, 0x78, 0x98)

W  = Inches(13.33)   # widescreen 16:9
H  = Inches(7.5)

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H

BLANK = prs.slide_layouts[6]   # completely blank


# ── Helpers ─────────────────────────────────────────────────────────────────

def new_slide():
    return prs.slides.add_slide(BLANK)


def bg(slide, color=C_BG):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def rect(slide, x, y, w, h, fill_color=None, line_color=None, line_width=Pt(0)):
    shape = slide.shapes.add_shape(1, x, y, w, h)   # MSO_SHAPE_TYPE.RECTANGLE = 1
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = line_width
    else:
        shape.line.fill.background()
    return shape


def txbox(slide, text, x, y, w, h,
          font_size=Pt(14), bold=False, color=C_TEXT,
          align=PP_ALIGN.LEFT, font_name="Calibri",
          italic=False, wrap=True):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = wrap
    p  = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size      = font_size
    run.font.bold      = bold
    run.font.italic    = italic
    run.font.color.rgb = color
    run.font.name      = font_name
    return tb


def heading(slide, text, y=Inches(0.25), size=Pt(28), color=C_CYAN):
    txbox(slide, text, Inches(0.5), y, Inches(12.33), Inches(0.6),
          font_size=size, bold=True, color=color, align=PP_ALIGN.LEFT)


def sub_heading(slide, text, y, size=Pt(16), color=C_PURPLE):
    txbox(slide, text, Inches(0.5), y, Inches(12.33), Inches(0.4),
          font_size=size, bold=True, color=color)


def divider(slide, y):
    r = rect(slide, Inches(0.5), y, Inches(12.33), Pt(1.5), fill_color=C_BORDER)
    return r


def footer(slide, roll="NDU202400038", name="Md Ghufran Alam", inst="NIELIT Srinagar"):
    rect(slide, 0, H - Inches(0.35), W, Inches(0.35), fill_color=C_SURFACE)
    txbox(slide, f"{name}  |  {roll}  |  {inst}  |  M.Tech Cyber Forensics",
          Inches(0.3), H - Inches(0.33), Inches(10), Inches(0.32),
          font_size=Pt(9), color=C_DIM)
    txbox(slide, "IoT Device Fingerprinting Framework",
          Inches(10.3), H - Inches(0.33), Inches(2.7), Inches(0.32),
          font_size=Pt(9), color=C_DIM, align=PP_ALIGN.RIGHT)


def bullet_box(slide, items, x, y, w, h,
               size=Pt(13), color=C_TEXT, bullet="▸", spacing=Inches(0.03)):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    first = True
    for item in items:
        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()
        p.space_before = Pt(4)
        run = p.add_run()
        run.text = f"{bullet}  {item}"
        run.font.size      = size
        run.font.color.rgb = color
        run.font.name      = "Calibri"
    return tb


def add_table(slide, headers, rows, x, y, w, h,
              hdr_bg=C_SURF2, hdr_fg=C_CYAN,
              row_bg=C_SURFACE, row_bg_alt=C_SURF2, row_fg=C_TEXT,
              font_size=Pt(11)):
    cols = len(headers)
    nrows = len(rows) + 1
    table = slide.shapes.add_table(nrows, cols, x, y, w, h).table

    col_w = int(w / cols)
    for i in range(cols):
        table.columns[i].width = col_w

    def set_cell(cell, text, bg, fg, bold=False, align=PP_ALIGN.CENTER):
        cell.fill.solid()
        cell.fill.fore_color.rgb = bg
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = align
        run = p.add_run()
        run.text = text
        run.font.size      = font_size
        run.font.bold      = bold
        run.font.color.rgb = fg
        run.font.name      = "Calibri"
        # thin border
        for side in ('top', 'bottom', 'left', 'right'):
            tc = cell._tc
            tcPr = tc.get_or_add_tcPr()

    # Header
    for c, hdr in enumerate(headers):
        set_cell(table.cell(0, c), hdr, hdr_bg, hdr_fg, bold=True)

    # Data rows
    for r, row in enumerate(rows):
        bg_c = row_bg if r % 2 == 0 else row_bg_alt
        for c, val in enumerate(row):
            align = PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER
            set_cell(table.cell(r + 1, c), str(val), bg_c, row_fg, align=align)

    return table


def stat_card(slide, value, label, x, y, w=Inches(2.4), h=Inches(1.1),
              val_color=C_CYAN):
    rect(slide, x, y, w, h, fill_color=C_SURF2, line_color=C_BORDER, line_width=Pt(1))
    txbox(slide, value,
          x, y + Inches(0.08), w, Inches(0.58),
          font_size=Pt(28), bold=True, color=val_color, align=PP_ALIGN.CENTER)
    txbox(slide, label,
          x, y + Inches(0.65), w, Inches(0.38),
          font_size=Pt(10), color=C_DIM, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════
#  SLIDE 1 — TITLE
# ═══════════════════════════════════════════════════════════════════════════
sl = new_slide(); bg(sl)

# Top accent bar
rect(sl, 0, 0, W, Inches(0.08), fill_color=C_CYAN)

# Large background logo-like rectangle (decorative)
rect(sl, Inches(9.5), Inches(1.2), Inches(3.5), Inches(4.5),
     fill_color=RGBColor(0x10, 0x14, 0x20), line_color=C_BORDER, line_width=Pt(1))
txbox(sl, "📡", Inches(9.5), Inches(1.8), Inches(3.5), Inches(2),
      font_size=Pt(90), align=PP_ALIGN.CENTER)
txbox(sl, "IoT Security", Inches(9.5), Inches(3.8), Inches(3.5), Inches(0.5),
      font_size=Pt(13), color=C_DIM, align=PP_ALIGN.CENTER)

# Title
txbox(sl,
      "Design of Framework for IoT Device\nFingerprinting and Anomaly Detection\nfor Smart Home Using Machine Learning",
      Inches(0.5), Inches(1.0), Inches(8.7), Inches(2.6),
      font_size=Pt(30), bold=True, color=C_WHITE, align=PP_ALIGN.LEFT)

# Subtitle line
rect(sl, Inches(0.5), Inches(3.65), Inches(4.0), Pt(2.5), fill_color=C_CYAN)

txbox(sl, "M.Tech Thesis — Final Presentation",
      Inches(0.5), Inches(3.75), Inches(8.0), Inches(0.4),
      font_size=Pt(14), color=C_CYAN, italic=True)

# Student block
rect(sl, Inches(0.5), Inches(4.35), Inches(5.5), Inches(1.85),
     fill_color=C_SURFACE, line_color=C_BORDER, line_width=Pt(1))

txbox(sl, "Student",
      Inches(0.65), Inches(4.45), Inches(2), Inches(0.3),
      font_size=Pt(10), color=C_DIM)
txbox(sl, "Md Ghufran Alam",
      Inches(0.65), Inches(4.72), Inches(5.2), Inches(0.38),
      font_size=Pt(18), bold=True, color=C_WHITE)
txbox(sl, "Roll No: NDU202400038",
      Inches(0.65), Inches(5.08), Inches(5.2), Inches(0.3),
      font_size=Pt(12), color=C_CYAN)
txbox(sl, "NIELIT Srinagar  |  M.Tech Cyber Forensics  |  Batch 2024–2026",
      Inches(0.65), Inches(5.38), Inches(5.2), Inches(0.3),
      font_size=Pt(11), color=C_DIM)

# Date
txbox(sl, "May 2026",
      Inches(0.5), Inches(6.8), Inches(4), Inches(0.35),
      font_size=Pt(11), color=C_DIM)

# Bottom accent bar
rect(sl, 0, H - Inches(0.08), W, Inches(0.08), fill_color=C_PURPLE)


# ═══════════════════════════════════════════════════════════════════════════
#  SLIDE 2 — PROBLEM STATEMENT
# ═══════════════════════════════════════════════════════════════════════════
sl = new_slide(); bg(sl)
footer(sl)
heading(sl, "Problem Statement")
divider(sl, Inches(0.95))

# Stats row
stat_card(sl, "30B+",  "IoT Devices by 2030", Inches(0.5),  Inches(1.1), val_color=C_CYAN)
stat_card(sl, "70%",   "Lack Basic Security",  Inches(3.1),  Inches(1.1), val_color=C_RED)
stat_card(sl, "10×",   "Attack Surface Growth",Inches(5.7),  Inches(1.1), val_color=C_YELLOW)
stat_card(sl, "₹1.5T", "Global IoT Loss/yr",   Inches(8.3),  Inches(1.1), val_color=C_PURPLE)
stat_card(sl, "0",     "Built-in Identity",    Inches(10.9), Inches(1.1), val_color=C_RED)

sub_heading(sl, "Core Challenges in Smart Home IoT Security", Inches(2.35))

problems = [
    "IoT devices lack unique identifiers — rogue or spoofed devices go undetected",
    "Heterogeneous protocols (MQTT, CoAP, HTTPS) make unified monitoring difficult",
    "Traditional intrusion detection systems are not designed for constrained IoT devices",
    "Anomalous behaviour (data exfiltration, port scans, DoS) is hard to distinguish from normal bursts",
    "No per-device baseline makes global anomaly thresholds unreliable",
    "Smart home gateways have no visibility into individual device traffic behaviour",
]
bullet_box(sl, problems, Inches(0.5), Inches(2.75), Inches(12.33), Inches(3.5), size=Pt(13))


# ═══════════════════════════════════════════════════════════════════════════
#  SLIDE 3 — OBJECTIVES
# ═══════════════════════════════════════════════════════════════════════════
sl = new_slide(); bg(sl)
footer(sl)
heading(sl, "Objectives")
divider(sl, Inches(0.95))

objectives = [
    ("01", "Design a passive, non-intrusive ML-based framework for IoT device fingerprinting",        C_CYAN),
    ("02", "Extract 37 statistical and protocol-level features from raw network flows without DPI",   C_PURPLE),
    ("03", "Classify 8 distinct smart home IoT device types with >95% accuracy",                     C_GREEN),
    ("04", "Detect three classes of anomalies using per-device ensemble (IF + OC-SVM)",              C_YELLOW),
    ("05", "Provide a production-ready REST API (FastAPI) and real-time monitoring dashboard",        C_CYAN),
    ("06", "Establish per-device behavioural baselines to eliminate false positives",                 C_PURPLE),
]

for i, (num, text, color) in enumerate(objectives):
    y = Inches(1.1) + i * Inches(0.92)
    rect(sl, Inches(0.5), y, Inches(0.7), Inches(0.75),
         fill_color=color if False else C_SURF2, line_color=color, line_width=Pt(2))
    txbox(sl, num, Inches(0.5), y, Inches(0.7), Inches(0.75),
          font_size=Pt(16), bold=True, color=color, align=PP_ALIGN.CENTER)
    rect(sl, Inches(1.3), y, Inches(11.5), Inches(0.75),
         fill_color=C_SURFACE, line_color=C_BORDER, line_width=Pt(1))
    txbox(sl, text, Inches(1.45), y + Inches(0.15), Inches(11.2), Inches(0.55),
          font_size=Pt(13), color=C_TEXT)


# ═══════════════════════════════════════════════════════════════════════════
#  SLIDE 4 — SYSTEM ARCHITECTURE
# ═══════════════════════════════════════════════════════════════════════════
sl = new_slide(); bg(sl)
footer(sl)
heading(sl, "System Architecture")
divider(sl, Inches(0.95))

# Architecture pipeline — boxes with arrows
components = [
    ("Data Generation\n& Synthetic\nFlows (1600)", C_CYAN,   Inches(0.3)),
    ("Feature\nExtraction\n(37 Features)",          C_PURPLE, Inches(2.55)),
    ("Preprocessing\nRobustScaler\n+ SMOTE",         C_GREEN,  Inches(4.8)),
    ("Fingerprinting\nRandom Forest\n+ Ensemble",   C_YELLOW, Inches(7.05)),
    ("Anomaly\nDetection\nIF + OC-SVM",             C_RED,    Inches(9.3)),
    ("Alert\nManager &\nAPI / Dashboard",           C_CYAN,   Inches(11.55)),
]

box_w = Inches(2.1)
box_h = Inches(1.6)
box_y = Inches(1.5)

for label, color, x in components:
    rect(sl, x, box_y, box_w, box_h,
         fill_color=C_SURF2, line_color=color, line_width=Pt(2))
    txbox(sl, label, x, box_y, box_w, box_h,
          font_size=Pt(11), bold=True, color=color, align=PP_ALIGN.CENTER)
    # Arrow (except last)
    if x != Inches(11.55):
        txbox(sl, "▶", x + box_w, box_y + Inches(0.55), Inches(0.45), Inches(0.5),
              font_size=Pt(18), color=C_DIM, align=PP_ALIGN.CENTER)

# Two bottom boxes
rect(sl, Inches(0.5),  Inches(3.5), Inches(5.9), Inches(2.6),
     fill_color=C_SURFACE, line_color=C_CYAN, line_width=Pt(1.5))
txbox(sl, "REST API  (FastAPI — Port 8000)",
      Inches(0.5), Inches(3.55), Inches(5.9), Inches(0.45),
      font_size=Pt(13), bold=True, color=C_CYAN, align=PP_ALIGN.CENTER)
api_items = [
    "POST /fingerprint  →  Device Identification",
    "POST /anomaly/score  →  Anomaly Scoring",
    "POST /analyze  →  Combined Analysis",
    "GET  /alerts/recent  →  Alert History",
    "GET  /metrics  →  System Statistics",
]
bullet_box(sl, api_items, Inches(0.6), Inches(4.05), Inches(5.7), Inches(2.0),
           size=Pt(11), bullet="•")

rect(sl, Inches(6.93), Inches(3.5), Inches(5.9), Inches(2.6),
     fill_color=C_SURFACE, line_color=C_PURPLE, line_width=Pt(1.5))
txbox(sl, "Live Dashboard  (Plotly Dash — Port 8050)",
      Inches(6.93), Inches(3.55), Inches(5.9), Inches(0.45),
      font_size=Pt(13), bold=True, color=C_PURPLE, align=PP_ALIGN.CENTER)
dash_items = [
    "Real-time anomaly score timeline",
    "Device traffic breakdown by type",
    "Alert severity distribution chart",
    "Top suspicious IPs & device health",
    "Interactive demo injection panel",
]
bullet_box(sl, dash_items, Inches(7.03), Inches(4.05), Inches(5.7), Inches(2.0),
           size=Pt(11), bullet="•")

# arrow downward from pipeline to API/Dash
txbox(sl, "▼", Inches(1.9),  Inches(3.1), Inches(1.0), Inches(0.4),
      font_size=Pt(16), color=C_DIM, align=PP_ALIGN.CENTER)
txbox(sl, "▼", Inches(8.4),  Inches(3.1), Inches(1.0), Inches(0.4),
      font_size=Pt(16), color=C_DIM, align=PP_ALIGN.CENTER)
txbox(sl, "◀──────────────────────────────────────────────────▶",
      Inches(2.4), Inches(3.7), Inches(6.4), Inches(0.4),
      font_size=Pt(10), color=C_BORDER, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════
#  SLIDE 5 — DATASET
# ═══════════════════════════════════════════════════════════════════════════
sl = new_slide(); bg(sl)
footer(sl)
heading(sl, "Dataset Description")
divider(sl, Inches(0.95))

# Stats row
stat_card(sl, "1,600",  "Total Flows",         Inches(0.5),  Inches(1.1), val_color=C_CYAN)
stat_card(sl, "8",      "Device Types",         Inches(3.1),  Inches(1.1), val_color=C_PURPLE)
stat_card(sl, "200",    "Flows / Device",       Inches(5.7),  Inches(1.1), val_color=C_GREEN)
stat_card(sl, "5%",     "Anomaly Fraction",     Inches(8.3),  Inches(1.1), val_color=C_YELLOW)
stat_card(sl, "3",      "Anomaly Types",        Inches(10.9), Inches(1.1), val_color=C_RED)

# Left: devices table
sub_heading(sl, "8 Smart Home Device Types", Inches(2.35), color=C_CYAN)
devices_data = [
    ("Smart Camera",     "High-BW HTTPS/RTSP streaming",       "~40MB/flow"),
    ("Smart Thermostat", "Low-BW MQTT periodic updates",        "~800B/flow"),
    ("Smart TV",         "Very high-BW streaming, many IPs",    "~700MB/flow"),
    ("Smart Bulb",       "Ultra-low CoAP on/off commands",      "~120B/flow"),
    ("Smart Plug",       "Minimal, power reporting bursts",     "~300B/flow"),
    ("Smart Speaker",    "Medium BW, voice + cloud API",        "~800KB/flow"),
    ("Smart Doorbell",   "Medium-high, camera + motion",        "~4MB/flow"),
    ("Motion Sensor",    "Ultra-low event-driven MQTT/CoAP",    "~80B/flow"),
]
add_table(sl,
          ["Device Type", "Traffic Profile", "Typical Byte Count"],
          devices_data,
          Inches(0.5), Inches(2.7), Inches(8.5), Inches(3.85),
          font_size=Pt(11))

# Right: split info
rect(sl, Inches(9.2), Inches(2.7), Inches(3.63), Inches(3.85),
     fill_color=C_SURFACE, line_color=C_BORDER, line_width=Pt(1))
txbox(sl, "Train / Val / Test Split",
      Inches(9.2), Inches(2.75), Inches(3.63), Inches(0.38),
      font_size=Pt(12), bold=True, color=C_PURPLE, align=PP_ALIGN.CENTER)
splits = [("Training",   "70%", "1,120 flows", C_GREEN),
          ("Validation", "15%", "240 flows",   C_YELLOW),
          ("Test",       "15%", "240 flows",   C_CYAN)]
for i, (name, pct, cnt, color) in enumerate(splits):
    y = Inches(3.3) + i * Inches(0.72)
    txbox(sl, name, Inches(9.35), y, Inches(1.5), Inches(0.4),
          font_size=Pt(12), color=C_TEXT)
    txbox(sl, pct, Inches(10.85), y, Inches(0.7), Inches(0.4),
          font_size=Pt(14), bold=True, color=color, align=PP_ALIGN.CENTER)
    txbox(sl, cnt, Inches(11.55), y, Inches(1.2), Inches(0.4),
          font_size=Pt(11), color=C_DIM, align=PP_ALIGN.RIGHT)
txbox(sl, "SMOTE applied on training set\nto balance class distribution",
      Inches(9.35), Inches(5.55), Inches(3.4), Inches(0.7),
      font_size=Pt(10), color=C_DIM, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════
#  SLIDE 6 — FEATURE ENGINEERING
# ═══════════════════════════════════════════════════════════════════════════
sl = new_slide(); bg(sl)
footer(sl)
heading(sl, "Feature Engineering — 37 Features across 7 Categories")
divider(sl, Inches(0.95))

categories = [
    ("Temporal (5)",          C_CYAN,   "flow_duration, mean_iat, std_iat, min_iat, max_iat"),
    ("Volume (4)",            C_PURPLE, "packet_count, byte_count, packet_rate, byte_rate"),
    ("Packet Size (4)",       C_GREEN,  "mean_pkt_size, std_pkt_size, min_pkt_size, max_pkt_size"),
    ("Protocol Flags (6)",    C_YELLOW, "tcp_ratio, udp_ratio, syn_ratio, fin_ratio, rst_ratio, ack_ratio"),
    ("Application Layer (8)", C_CYAN,   "is_https, is_mqtt, is_coap, is_mdns, is_ntp, dns_query_count,\nwell_known_port_ratio, is_encrypted"),
    ("Traffic Direction (3)", C_PURPLE, "upload_bytes, download_bytes, upload_download_ratio"),
    ("Destination (7)",       C_GREEN,  "unique_dest_ports, unique_dest_ips, port_entropy, ip_entropy,\nwell_known_ports_count, mean_dest_port, std_dest_port"),
]

col_w = Inches(6.0)
col_h = Inches(0.88)
gap   = Inches(0.12)
start_y = Inches(1.1)

for i, (cat, color, features) in enumerate(categories):
    col = i % 2
    row = i // 2
    if i == 6:   # last item: full width
        x = Inches(0.5)
        w = Inches(12.33)
    else:
        x = Inches(0.5) + col * (col_w + Inches(0.33))
        w = col_w

    y = start_y + row * (col_h + gap)

    rect(sl, x, y, w, col_h,
         fill_color=C_SURFACE, line_color=color, line_width=Pt(2))
    txbox(sl, cat,
          x + Inches(0.1), y + Inches(0.04), w - Inches(0.2), Inches(0.3),
          font_size=Pt(12), bold=True, color=color)
    txbox(sl, features,
          x + Inches(0.1), y + Inches(0.34), w - Inches(0.2), Inches(0.52),
          font_size=Pt(10), color=C_DIM)

txbox(sl, "All features are computed from passive traffic observation — no DPI, no payload inspection",
      Inches(0.5), Inches(6.85), Inches(12.33), Inches(0.3),
      font_size=Pt(11), italic=True, color=C_DIM, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════
#  SLIDE 7 — DEVICE FINGERPRINTING MODULE
# ═══════════════════════════════════════════════════════════════════════════
sl = new_slide(); bg(sl)
footer(sl)
heading(sl, "Device Fingerprinting Module")
divider(sl, Inches(0.95))

# Left: description
rect(sl, Inches(0.5), Inches(1.1), Inches(5.5), Inches(5.55),
     fill_color=C_SURFACE, line_color=C_CYAN, line_width=Pt(1.5))
txbox(sl, "Primary Model — Random Forest",
      Inches(0.6), Inches(1.15), Inches(5.3), Inches(0.4),
      font_size=Pt(14), bold=True, color=C_CYAN)

rf_details = [
    "n_estimators = 100 trees",
    "max_depth = 15",
    "class_weight = 'balanced'",
    "n_jobs = -1  (all CPU cores)",
    "random_state = 42",
    "Confidence threshold = 0.75",
    "Below threshold → 'unknown' class",
]
bullet_box(sl, rf_details, Inches(0.6), Inches(1.6), Inches(5.2), Inches(2.5),
           size=Pt(12), color=C_TEXT)

txbox(sl, "Comparison Models",
      Inches(0.6), Inches(4.2), Inches(5.3), Inches(0.38),
      font_size=Pt(13), bold=True, color=C_PURPLE)
comp_models = [
    "Gradient Boosting — 100 trees, lr=0.1",
    "SVM (RBF) — C=10, gamma='scale'",
    "Voting Ensemble — soft voting (RF+GB+SVM)",
]
bullet_box(sl, comp_models, Inches(0.6), Inches(4.6), Inches(5.2), Inches(1.5),
           size=Pt(12), color=C_TEXT)

txbox(sl, "Best model auto-selected by validation accuracy",
      Inches(0.6), Inches(6.1), Inches(5.3), Inches(0.4),
      font_size=Pt(10), italic=True, color=C_DIM)

# Right: results table
txbox(sl, "Model Comparison Results",
      Inches(6.3), Inches(1.1), Inches(6.5), Inches(0.45),
      font_size=Pt(14), bold=True, color=C_YELLOW)

model_rows = [
    ("Random Forest ★",     "100.00%", "1.0000", "Primary"),
    ("Gradient Boosting",   "100.00%", "1.0000", "Comparison"),
    ("Voting Ensemble",     "100.00%", "1.0000", "Combined"),
    ("SVM (RBF)",           "87.50%",  "0.9900", "Comparison"),
]
add_table(sl,
          ["Model", "Accuracy", "ROC-AUC", "Role"],
          model_rows,
          Inches(6.3), Inches(1.65), Inches(6.5), Inches(2.0),
          font_size=Pt(11))

# Training pipeline
txbox(sl, "Training Pipeline",
      Inches(6.3), Inches(3.85), Inches(6.5), Inches(0.38),
      font_size=Pt(13), bold=True, color=C_GREEN)

steps = [
    "1. Generate 1,600 synthetic flows",
    "2. Stratified 70 / 15 / 15 split",
    "3. RobustScaler (fit on full data, outlier-resistant)",
    "4. SMOTE oversampling on full scaled data",
    "5. Train all 4 models in parallel",
    "6. Select best by validation accuracy",
    "7. Evaluate on held-out test set",
]
bullet_box(sl, steps, Inches(6.3), Inches(4.3), Inches(6.5), Inches(2.5),
           size=Pt(11), bullet="→")


# ═══════════════════════════════════════════════════════════════════════════
#  SLIDE 8 — ANOMALY DETECTION MODULE
# ═══════════════════════════════════════════════════════════════════════════
sl = new_slide(); bg(sl)
footer(sl)
heading(sl, "Anomaly Detection Module")
divider(sl, Inches(0.95))

# Architecture diagram
rect(sl, Inches(0.5), Inches(1.1), Inches(12.33), Inches(1.35),
     fill_color=C_SURFACE, line_color=C_BORDER, line_width=Pt(1))
txbox(sl, "Per-Device Ensemble Architecture  (8 independent models + 1 global fallback)",
      Inches(0.6), Inches(1.15), Inches(12.0), Inches(0.4),
      font_size=Pt(13), bold=True, color=C_CYAN)
txbox(sl, "Ensemble Score  =  0.60 × IsolationForest_score  +  0.40 × OneClassSVM_score",
      Inches(0.6), Inches(1.6), Inches(12.0), Inches(0.7),
      font_size=Pt(15), bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)

# Three columns
cols = [
    ("Isolation Forest",
     C_CYAN, [
         "n_estimators = 50 trees",
         "contamination = 0.05  (5%)",
         "max_samples = 128",
         "Trained on NORMAL flows only",
         "Score normalized to [0, 1]",
         "P5–P95 bounds + power calibration",
     ]),
    ("One-Class SVM",
     C_PURPLE, [
         "kernel = 'rbf'",
         "nu = 0.05  (5% anomaly bound)",
         "gamma = 'auto'",
         "Trained on NORMAL flows only",
         "Score normalized to [0, 1]",
         "P5–P95 bounds + power calibration",
     ]),
    ("Alert Severity",
     C_YELLOW, [
         "score ≥ 0.75       →  Anomalous",
         "0.50 – 0.65     →  Low",
         "0.65 – 0.80     →  Medium",
         "0.80 – 0.90     →  High",
         "0.90 – 1.00     →  Critical",
         "Global fallback for unknown devices",
     ]),
]

col_w2 = Inches(3.9)
col_h2 = Inches(3.7)
for i, (title, color, items) in enumerate(cols):
    x = Inches(0.5) + i * (col_w2 + Inches(0.27))
    rect(sl, x, Inches(2.6), col_w2, col_h2,
         fill_color=C_SURFACE, line_color=color, line_width=Pt(2))
    txbox(sl, title, x + Inches(0.1), Inches(2.65), col_w2 - Inches(0.2), Inches(0.4),
          font_size=Pt(13), bold=True, color=color)
    bullet_box(sl, items, x + Inches(0.1), Inches(3.1), col_w2 - Inches(0.2), Inches(3.0),
               size=Pt(11), bullet="▸")

txbox(sl, "Score calibration: power transform (p=0.6) pushes normal scores near 0, anomalies above 0.75",
      Inches(0.5), Inches(6.5), Inches(12.33), Inches(0.3),
      font_size=Pt(10), italic=True, color=C_DIM, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════
#  SLIDE 9 — ANOMALY TYPES DETECTED
# ═══════════════════════════════════════════════════════════════════════════
sl = new_slide(); bg(sl)
footer(sl)
heading(sl, "Anomaly Types Detected")
divider(sl, Inches(0.95))

anomalies = [
    ("Data Exfiltration", C_RED,
     "Unauthorized mass upload of device data to external servers",
     [
         "upload_bytes  →  30–80× normal spike",
         "byte_rate     →  25–60× normal rate",
         "byte_count    →  20–50× normal total",
         "upload_download_ratio  →  15–40×",
     ],
     "Smart Camera exfiltrating 1.5GB instead of normal 28MB"),
    ("Port Scan", C_YELLOW,
     "Device probing internal network for open services",
     [
         "unique_dest_ports  →  500–1,500 ports",
         "port_entropy       →  8.0–10.0 (near max)",
         "ip_entropy         →  7.0–9.0 (many hosts)",
         "packet_count       →  20–50× normal",
     ],
     "Smart Bulb scanning 800 ports instead of normal 1–3"),
    ("DoS Participation", C_PURPLE,
     "Compromised device flooding a target (botnet member)",
     [
         "packet_rate   →  50–120× normal",
         "packet_count  →  40–100× normal",
         "byte_rate     →  40–90× normal",
         "syn_ratio     →  30× normal (SYN flood)",
     ],
     "Motion Sensor sending 150k pkt/s instead of normal 10"),
]

aw = Inches(3.8)
ah = Inches(5.2)
for i, (title, color, desc, sigs, example) in enumerate(anomalies):
    x = Inches(0.5) + i * (aw + Inches(0.27))
    rect(sl, x, Inches(1.1), aw, ah,
         fill_color=C_SURFACE, line_color=color, line_width=Pt(2))
    # Title badge
    rect(sl, x, Inches(1.1), aw, Inches(0.45), fill_color=color)
    txbox(sl, title, x, Inches(1.1), aw, Inches(0.45),
          font_size=Pt(13), bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    txbox(sl, desc, x + Inches(0.1), Inches(1.63), aw - Inches(0.2), Inches(0.55),
          font_size=Pt(10), color=C_TEXT, italic=True)
    txbox(sl, "Anomaly Signature:", x + Inches(0.1), Inches(2.25), aw - Inches(0.2), Inches(0.3),
          font_size=Pt(11), bold=True, color=color)
    bullet_box(sl, sigs, x + Inches(0.1), Inches(2.6), aw - Inches(0.2), Inches(2.0),
               size=Pt(11), bullet="▸", color=C_TEXT)
    txbox(sl, "Example:", x + Inches(0.1), Inches(4.7), aw - Inches(0.2), Inches(0.28),
          font_size=Pt(10), bold=True, color=C_DIM)
    txbox(sl, example, x + Inches(0.1), Inches(5.0), aw - Inches(0.2), Inches(0.7),
          font_size=Pt(10), italic=True, color=C_DIM)


# ═══════════════════════════════════════════════════════════════════════════
#  SLIDE 10 — REST API & DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
sl = new_slide(); bg(sl)
footer(sl)
heading(sl, "REST API & Live Dashboard")
divider(sl, Inches(0.95))

# API section
rect(sl, Inches(0.5), Inches(1.1), Inches(6.0), Inches(5.55),
     fill_color=C_SURFACE, line_color=C_CYAN, line_width=Pt(1.5))
txbox(sl, "FastAPI — Port 8000",
      Inches(0.6), Inches(1.15), Inches(5.8), Inches(0.4),
      font_size=Pt(14), bold=True, color=C_CYAN)

endpoints = [
    ("GET",  "/health",        "System health, uptime & SHAP status"),
    ("GET",  "/devices",       "List of 8 supported device types"),
    ("POST", "/fingerprint",   "Identify device from 37 features"),
    ("POST", "/anomaly/score", "Per-device anomaly scoring"),
    ("POST", "/analyze",       "Combined fingerprint + anomaly"),
    ("POST", "/explain",       "Live SHAP — top 10 feature contributions"),
    ("GET",  "/alerts/recent", "Last N alert records (default 50)"),
    ("GET",  "/metrics",       "Uptime, request count, anomaly rate"),
    ("POST", "/demo/inject",   "Inject simulated anomaly event"),
]

for i, (method, path, desc) in enumerate(endpoints):
    y = Inches(1.65) + i * Inches(0.495)
    color = C_CYAN if method == "GET" else (C_GREEN if path == "/explain" else C_PURPLE)
    rect(sl, Inches(0.6), y, Inches(0.72), Inches(0.36), fill_color=color)
    txbox(sl, method, Inches(0.6), y, Inches(0.72), Inches(0.36),
          font_size=Pt(9), bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    txbox(sl, path, Inches(1.38), y, Inches(2.3), Inches(0.36),
          font_size=Pt(10), color=C_WHITE, bold=True)
    txbox(sl, desc, Inches(3.72), y, Inches(2.7), Inches(0.36),
          font_size=Pt(9), color=C_DIM)

txbox(sl, "Custom dark Swagger UI at /docs  |  SHAP Explainability via /explain endpoint",
      Inches(0.6), Inches(6.15), Inches(5.8), Inches(0.38),
      font_size=Pt(10), italic=True, color=C_DIM)

# Dashboard section
rect(sl, Inches(6.83), Inches(1.1), Inches(6.0), Inches(5.55),
     fill_color=C_SURFACE, line_color=C_PURPLE, line_width=Pt(1.5))
txbox(sl, "Plotly Dash — Port 8050",
      Inches(6.93), Inches(1.15), Inches(5.8), Inches(0.4),
      font_size=Pt(14), bold=True, color=C_PURPLE)

dash_panels = [
    ("Live Anomaly Timeline",    "Real-time score chart, auto-refreshes every 5s"),
    ("Device Breakdown",         "Pie chart of traffic by device type"),
    ("Alert Severity Histogram", "LOW / MEDIUM / HIGH / CRITICAL distribution"),
    ("Score Gauge",              "Latest anomaly score with coloured severity zones"),
    ("Recent Alerts Table",      "Alert log with IP, device, score, severity"),
    ("SHAP Explainability Panel","Live green/red bar chart — why model made prediction"),
]
for i, (panel, desc) in enumerate(dash_panels):
    y = Inches(1.65) + i * Inches(0.58)
    txbox(sl, f"▸  {panel}", Inches(6.93), y, Inches(3.0), Inches(0.4),
          font_size=Pt(11), bold=True, color=C_WHITE)
    txbox(sl, desc, Inches(9.98), y, Inches(2.7), Inches(0.4),
          font_size=Pt(10), color=C_DIM)


# ═══════════════════════════════════════════════════════════════════════════
#  SLIDE 11 — RESULTS & PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════
sl = new_slide(); bg(sl)
footer(sl)
heading(sl, "Results & Performance Metrics")
divider(sl, Inches(0.95))

# Top KPIs
stat_card(sl, "100%",   "RF/GB/Ensemble\nAccuracy",  Inches(0.5),  Inches(1.1), val_color=C_GREEN)
stat_card(sl, "1.0000", "RF ROC-AUC\nScore",          Inches(3.1),  Inches(1.1), val_color=C_CYAN)
stat_card(sl, "0.9741", "Mean Anomaly\nAUC-ROC",      Inches(5.7),  Inches(1.1), val_color=C_YELLOW)
stat_card(sl, "<50ms",  "API Response\nTime",         Inches(8.3),  Inches(1.1), val_color=C_PURPLE)
stat_card(sl, "8/8",    "Devices\nIdentified",        Inches(10.9), Inches(1.1), val_color=C_GREEN)

# Fingerprinting results table
txbox(sl, "Per-Device Fingerprinting Results (Test Set)",
      Inches(0.5), Inches(2.4), Inches(6.2), Inches(0.4),
      font_size=Pt(13), bold=True, color=C_CYAN)

fp_rows = [
    ("Smart Camera",     "100%", "1.000", "100%"),
    ("Smart Thermostat", "100%", "1.000", "100%"),
    ("Smart TV",         "100%", "1.000", "100%"),
    ("Smart Bulb",       "100%", "1.000", "100%"),
    ("Smart Plug",       "100%", "1.000", "100%"),
    ("Smart Speaker",    "100%", "1.000", "100%"),
    ("Smart Doorbell",   "100%", "1.000", "100%"),
    ("Motion Sensor",    "100%", "1.000", "100%"),
]
add_table(sl,
          ["Device", "Precision", "Recall", "F1-Score"],
          fp_rows,
          Inches(0.5), Inches(2.85), Inches(6.2), Inches(3.6),
          font_size=Pt(10))

# Anomaly detection results
txbox(sl, "Anomaly Detection Results (Ensemble)",
      Inches(7.0), Inches(2.4), Inches(5.83), Inches(0.4),
      font_size=Pt(13), bold=True, color=C_PURPLE)

ad_rows = [
    ("Smart Camera",     "0.9966",  "0.999"),
    ("Smart Thermostat", "0.9445",  "0.934"),
    ("Smart TV",         "0.9942",  "0.969"),
    ("Smart Bulb",       "0.9189",  "0.905"),
    ("Smart Plug",       "0.9358",  "0.921"),
    ("Smart Speaker",    "0.9674",  "0.969"),
    ("Smart Doorbell",   "0.9576",  "0.966"),
    ("Motion Sensor",    "0.9779",  "0.972"),
]
add_table(sl,
          ["Device", "AUC-ROC", "Avg Attack Score"],
          ad_rows,
          Inches(7.0), Inches(2.85), Inches(5.83), Inches(3.6),
          font_size=Pt(10))


# ═══════════════════════════════════════════════════════════════════════════
#  SLIDE 12 — TECH STACK
# ═══════════════════════════════════════════════════════════════════════════
sl = new_slide(); bg(sl)
footer(sl)
heading(sl, "Technology Stack")
divider(sl, Inches(0.95))

tech = [
    ("Core Language",       "Python 3.9+",                                             C_CYAN),
    ("ML / Modelling",      "scikit-learn — RF, GB, SVM, IsolationForest, OC-SVM",    C_PURPLE),
    ("Explainability",      "shap — SHAP TreeExplainer, live POST /explain endpoint",  C_GREEN),
    ("Class Balancing",     "imbalanced-learn — SMOTE oversampling",                   C_YELLOW),
    ("REST API",            "FastAPI + Uvicorn — async, OpenAPI, Swagger UI",          C_CYAN),
    ("Dashboard / Charts",  "Plotly Dash — live SHAP panel + anomaly monitoring",      C_PURPLE),
    ("Data Processing",     "NumPy + Pandas — feature engineering & manipulation",     C_GREEN),
    ("Model Persistence",   "joblib — serialization of all trained models",            C_YELLOW),
    ("Visualisation",       "Matplotlib + Seaborn — confusion matrix, heatmaps",       C_CYAN),
    ("Testing",             "pytest — unit & integration test suite",                  C_PURPLE),
    ("Frontend",            "JetBrains Mono + Swagger UI v5 (CDN) — custom docs",     C_GREEN),
    ("Environment",         "Windows 11, 8GB RAM, Python venv",                       C_DIM),
]

col_w3 = Inches(5.9)
for i, (cat, detail, color) in enumerate(tech):
    col = i % 2
    row = i // 2
    x = Inches(0.5) + col * (col_w3 + Inches(0.43))
    y = Inches(1.1) + row * Inches(0.73)
    rect(sl, x, y, col_w3, Inches(0.62),
         fill_color=C_SURFACE, line_color=color, line_width=Pt(1.5))
    txbox(sl, cat, x + Inches(0.1), y + Inches(0.04), Inches(1.7), Inches(0.32),
          font_size=Pt(10), bold=True, color=color)
    txbox(sl, detail, x + Inches(1.85), y + Inches(0.04), col_w3 - Inches(2.0), Inches(0.55),
          font_size=Pt(10), color=C_TEXT)


# ═══════════════════════════════════════════════════════════════════════════
#  SLIDE 13 — CONCLUSION & FUTURE WORK
# ═══════════════════════════════════════════════════════════════════════════
sl = new_slide(); bg(sl)
footer(sl)
heading(sl, "Conclusion & Future Work")
divider(sl, Inches(0.95))

# Left: Conclusion
rect(sl, Inches(0.5), Inches(1.1), Inches(5.9), Inches(5.55),
     fill_color=C_SURFACE, line_color=C_GREEN, line_width=Pt(1.5))
txbox(sl, "✔  What Was Achieved",
      Inches(0.6), Inches(1.15), Inches(5.7), Inches(0.4),
      font_size=Pt(14), bold=True, color=C_GREEN)

conclusions = [
    "Passive ML-based framework for smart home IoT fingerprinting designed and implemented",
    "37 carefully crafted features capture distinct device behavioural signatures",
    "Random Forest achieves 100% classification accuracy across all 8 device types",
    "Per-device IF + OC-SVM ensemble outperforms single global anomaly detector",
    "Three real-world attack patterns (exfiltration, scan, DoS) successfully detected",
    "SHAP explainability integrated — every prediction auditable via live POST /explain",
    "Production-ready REST API (9 endpoints) with FastAPI enables real-time deployment",
    "Live Plotly Dash dashboard with SHAP panel provides full security transparency",
]
bullet_box(sl, conclusions, Inches(0.6), Inches(1.65), Inches(5.7), Inches(4.7),
           size=Pt(11), bullet="✔", color=C_TEXT)

# Right: Future Work
rect(sl, Inches(6.93), Inches(1.1), Inches(5.9), Inches(5.55),
     fill_color=C_SURFACE, line_color=C_YELLOW, line_width=Pt(1.5))
txbox(sl, "→  Future Scope",
      Inches(7.03), Inches(1.15), Inches(5.7), Inches(0.4),
      font_size=Pt(14), bold=True, color=C_YELLOW)

future = [
    "Real traffic capture via Wireshark / tcpdump on live smart home network",
    "Deep Learning models (LSTM, Autoencoder) for temporal anomaly detection",
    "Federated Learning across multiple homes preserving user privacy",
    "Online / incremental learning to adapt to new device firmware updates",
    "Edge deployment on Raspberry Pi gateway for on-premise inference",
    "Graph Neural Network for device relationship and lateral movement detection",
    "CVE database integration for vulnerability-aware alert enrichment",
    "Mobile app for real-time alert notification to home owners",
]
bullet_box(sl, future, Inches(7.03), Inches(1.65), Inches(5.7), Inches(4.7),
           size=Pt(11), bullet="→", color=C_TEXT)


# ═══════════════════════════════════════════════════════════════════════════
#  SLIDE 14 — THANK YOU
# ═══════════════════════════════════════════════════════════════════════════
sl = new_slide(); bg(sl)

# Top + Bottom accent bars
rect(sl, 0, 0, W, Inches(0.08), fill_color=C_CYAN)
rect(sl, 0, H - Inches(0.08), W, Inches(0.08), fill_color=C_PURPLE)

# Central card
rect(sl, Inches(2.0), Inches(1.2), Inches(9.33), Inches(5.1),
     fill_color=C_SURFACE, line_color=C_CYAN, line_width=Pt(2))

txbox(sl, "Thank You",
      Inches(2.0), Inches(1.5), Inches(9.33), Inches(1.4),
      font_size=Pt(54), bold=True, color=C_CYAN, align=PP_ALIGN.CENTER)

txbox(sl, "for your attention",
      Inches(2.0), Inches(2.8), Inches(9.33), Inches(0.5),
      font_size=Pt(20), italic=True, color=C_DIM, align=PP_ALIGN.CENTER)

rect(sl, Inches(4.5), Inches(3.45), Inches(4.33), Pt(1.5), fill_color=C_PURPLE)

txbox(sl, "Open for Questions & Discussion",
      Inches(2.0), Inches(3.6), Inches(9.33), Inches(0.5),
      font_size=Pt(16), color=C_WHITE, align=PP_ALIGN.CENTER)

# Student info box
rect(sl, Inches(2.5), Inches(4.35), Inches(8.33), Inches(1.6),
     fill_color=C_SURF2, line_color=C_BORDER, line_width=Pt(1))

info_lines = [
    ("Name",       "Md Ghufran Alam"),
    ("Roll No",    "NDU202400038"),
    ("Programme",  "M.Tech Cyber Forensics  |  4th Semester"),
    ("Institute",  "NIELIT Srinagar  |  Batch 2024–2026"),
]
for i, (label, value) in enumerate(info_lines):
    y = Inches(4.42) + i * Inches(0.35)
    txbox(sl, f"{label}:", Inches(2.65), y, Inches(1.5), Inches(0.33),
          font_size=Pt(11), color=C_DIM, bold=True)
    txbox(sl, value, Inches(4.15), y, Inches(6.5), Inches(0.33),
          font_size=Pt(11), color=C_TEXT)

txbox(sl, "mdghufranalam377@gmail.com",
      Inches(2.0), Inches(6.1), Inches(9.33), Inches(0.32),
      font_size=Pt(11), color=C_CYAN, align=PP_ALIGN.CENTER)


# ── Save ────────────────────────────────────────────────────────────────────
out = r"D:\IoT_Device_Fingerprinting_Framework\IoT_Fingerprinting_Presentation.pptx"
prs.save(out)
print(f"Saved: {out}")
print(f"Slides: {len(prs.slides)}")
