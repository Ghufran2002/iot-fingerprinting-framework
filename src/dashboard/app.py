"""
Real-time Plotly Dash monitoring dashboard — Port 8050
Auto-refreshes every 5 seconds from the FastAPI backend (port 8000).
Includes SHAP Explainability panel showing live feature contributions.
"""
import time
import random
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output, callback

API_BASE            = "http://127.0.0.1:8000"
REFRESH_INTERVAL_MS = 5000

DEVICE_COLORS = {
    'smart_camera':     '#2196F3',
    'smart_thermostat': '#FF9800',
    'smart_tv':         '#9C27B0',
    'smart_bulb':       '#FFEB3B',
    'smart_plug':       '#4CAF50',
    'smart_speaker':    '#00BCD4',
    'smart_doorbell':   '#F44336',
    'motion_sensor':    '#795548',
    'unknown':          '#9E9E9E',
}
SEVERITY_COLORS = {
    'LOW': '#4CAF50', 'MEDIUM': '#FF9800',
    'HIGH': '#F44336', 'CRITICAL': '#9C27B0',
}

_score_history: list = []
_MAX_HISTORY = 60

# ---------------------------------------------------------------------------
# Device flow profiles for SHAP demo
# ---------------------------------------------------------------------------
_BASE_FLOW = {
    "flow_duration": 10.0, "mean_iat": 0.01, "std_iat": 0.005,
    "min_iat": 0.001, "max_iat": 0.05,
    "packet_count": 100.0, "byte_count": 50000.0,
    "packet_rate": 10.0, "byte_rate": 5000.0,
    "mean_pkt_size": 500.0, "std_pkt_size": 100.0,
    "min_pkt_size": 64.0, "max_pkt_size": 1500.0,
    "tcp_ratio": 0.5, "udp_ratio": 0.5,
    "syn_ratio": 0.01, "fin_ratio": 0.008, "rst_ratio": 0.002, "ack_ratio": 0.4,
    "is_https": 0.0, "is_mqtt": 0.0, "is_coap": 0.0, "is_mdns": 0.0, "is_ntp": 0.0,
    "dns_query_count": 2.0, "well_known_port_ratio": 0.5, "is_encrypted": 0.0,
    "upload_bytes": 25000.0, "download_bytes": 25000.0, "upload_download_ratio": 1.0,
    "unique_dest_ports": 2.0, "unique_dest_ips": 2.0,
    "port_entropy": 1.0, "ip_entropy": 0.8,
    "well_known_ports_count": 1.0, "mean_dest_port": 8080.0, "std_dest_port": 100.0,
}

_DEVICE_OVERRIDES = {
    'smart_camera': {
        "tcp_ratio": 0.92, "udp_ratio": 0.08, "is_https": 1.0, "is_encrypted": 1.0,
        "mean_dest_port": 443.0, "std_dest_port": 15.0,
        "byte_count": 180000.0, "packet_count": 2000.0, "byte_rate": 18000.0,
        "ack_ratio": 0.65, "well_known_port_ratio": 0.95,
        "upload_bytes": 130000.0, "download_bytes": 50000.0, "upload_download_ratio": 2.6,
        "unique_dest_ips": 2.0, "dns_query_count": 3.0,
    },
    'smart_thermostat': {
        "tcp_ratio": 0.55, "udp_ratio": 0.45, "is_mqtt": 1.0,
        "mean_dest_port": 1883.0, "std_dest_port": 5.0,
        "byte_count": 3000.0, "packet_count": 40.0, "byte_rate": 300.0,
        "ack_ratio": 0.35, "well_known_port_ratio": 0.3, "is_encrypted": 0.0,
        "upload_bytes": 2000.0, "download_bytes": 1000.0, "upload_download_ratio": 2.0,
        "unique_dest_ips": 1.0, "dns_query_count": 1.0,
    },
    'smart_tv': {
        "tcp_ratio": 0.85, "udp_ratio": 0.15, "is_https": 1.0, "is_encrypted": 1.0,
        "mean_dest_port": 443.0, "std_dest_port": 80.0,
        "byte_count": 500000.0, "packet_count": 5000.0, "byte_rate": 50000.0,
        "ack_ratio": 0.60, "well_known_port_ratio": 0.85,
        "upload_bytes": 50000.0, "download_bytes": 450000.0, "upload_download_ratio": 0.11,
        "unique_dest_ips": 8.0, "ip_entropy": 2.1, "dns_query_count": 10.0,
    },
    'smart_bulb': {
        "tcp_ratio": 0.10, "udp_ratio": 0.90, "is_coap": 1.0, "is_encrypted": 0.0,
        "mean_dest_port": 5683.0, "std_dest_port": 2.0,
        "byte_count": 500.0, "packet_count": 10.0, "byte_rate": 50.0,
        "ack_ratio": 0.05, "well_known_port_ratio": 0.1,
        "upload_bytes": 300.0, "download_bytes": 200.0, "upload_download_ratio": 1.5,
        "unique_dest_ips": 1.0, "dns_query_count": 0.0,
    },
    'smart_plug': {
        "tcp_ratio": 0.60, "udp_ratio": 0.40, "is_mqtt": 1.0, "is_encrypted": 0.0,
        "mean_dest_port": 1883.0, "std_dest_port": 5.0,
        "byte_count": 2000.0, "packet_count": 30.0, "byte_rate": 200.0,
        "ack_ratio": 0.40, "well_known_port_ratio": 0.3,
        "upload_bytes": 1200.0, "download_bytes": 800.0, "upload_download_ratio": 1.5,
        "unique_dest_ips": 1.0, "dns_query_count": 1.0,
    },
    'smart_speaker': {
        "tcp_ratio": 0.70, "udp_ratio": 0.30, "is_https": 1.0, "is_encrypted": 1.0,
        "mean_dest_port": 443.0, "std_dest_port": 30.0,
        "byte_count": 50000.0, "packet_count": 500.0, "byte_rate": 5000.0,
        "ack_ratio": 0.50, "well_known_port_ratio": 0.75,
        "upload_bytes": 30000.0, "download_bytes": 20000.0, "upload_download_ratio": 1.5,
        "unique_dest_ips": 4.0, "dns_query_count": 5.0,
    },
    'smart_doorbell': {
        "tcp_ratio": 0.80, "udp_ratio": 0.20, "is_https": 1.0, "is_encrypted": 1.0,
        "mean_dest_port": 443.0, "std_dest_port": 20.0,
        "byte_count": 90000.0, "packet_count": 900.0, "byte_rate": 9000.0,
        "ack_ratio": 0.55, "well_known_port_ratio": 0.90,
        "upload_bytes": 60000.0, "download_bytes": 30000.0, "upload_download_ratio": 2.0,
        "unique_dest_ips": 2.0, "dns_query_count": 3.0,
    },
    'motion_sensor': {
        "tcp_ratio": 0.20, "udp_ratio": 0.80, "is_mqtt": 1.0, "is_encrypted": 0.0,
        "mean_dest_port": 1883.0, "std_dest_port": 3.0,
        "byte_count": 1000.0, "packet_count": 15.0, "byte_rate": 100.0,
        "ack_ratio": 0.15, "well_known_port_ratio": 0.2,
        "upload_bytes": 700.0, "download_bytes": 300.0, "upload_download_ratio": 2.3,
        "unique_dest_ips": 1.0, "dns_query_count": 0.0,
    },
}


def _build_device_flow(device: str) -> dict:
    flow = dict(_BASE_FLOW)
    flow.update(_DEVICE_OVERRIDES.get(device, {}))
    return flow


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = Dash(__name__, title="IoT Security Monitor")

app.layout = html.Div(
    style={'backgroundColor': '#0F1117', 'minHeight': '100vh',
           'fontFamily': 'Segoe UI, sans-serif', 'color': '#E0E0E0'},
    children=[
        # Header
        html.Div(
            style={'background': 'linear-gradient(90deg, #1A237E 0%, #283593 100%)',
                   'padding': '18px 30px', 'display': 'flex',
                   'alignItems': 'center', 'justifyContent': 'space-between',
                   'borderBottom': '2px solid #3949AB'},
            children=[
                html.Div([
                    html.H1("IoT Device Fingerprinting & Anomaly Detection",
                            style={'margin': 0, 'fontSize': '22px', 'fontWeight': '700',
                                   'color': '#90CAF9'}),
                    html.P("M.Tech Cyber Forensics | NIELIT Srinagar | Md Ghufran Alam (NDU202400038)",
                           style={'margin': '4px 0 0', 'fontSize': '12px', 'color': '#B0BEC5'}),
                ]),
                html.Div(id='header-status',
                         style={'fontSize': '13px', 'color': '#A5D6A7', 'textAlign': 'right'}),
            ]
        ),

        dcc.Interval(id='interval', interval=REFRESH_INTERVAL_MS, n_intervals=0),

        # KPI Cards Row
        html.Div(id='kpi-row',
                 style={'display': 'flex', 'gap': '16px', 'padding': '20px 30px 10px'}),

        # Charts Row 1: timeline + pie
        html.Div(
            style={'display': 'flex', 'gap': '16px', 'padding': '0 30px 16px'},
            children=[
                html.Div(dcc.Graph(id='anomaly-timeline'), style={'flex': '2'}),
                html.Div(dcc.Graph(id='device-pie'),       style={'flex': '1'}),
            ]
        ),

        # Charts Row 2: severity bar + gauge
        html.Div(
            style={'display': 'flex', 'gap': '16px', 'padding': '0 30px 16px'},
            children=[
                html.Div(dcc.Graph(id='severity-bar'), style={'flex': '1'}),
                html.Div(dcc.Graph(id='score-gauge'),  style={'flex': '1'}),
            ]
        ),

        # Recent Alerts Table
        html.Div(
            style={'padding': '0 30px 24px'},
            children=[
                html.H3("Recent Anomaly Alerts",
                        style={'color': '#90CAF9', 'margin': '0 0 10px'}),
                html.Div(id='alerts-table'),
            ]
        ),

        # ── SHAP Explainability Panel ────────────────────────────────────────
        html.Div(
            style={
                'margin': '0 30px 30px',
                'backgroundColor': '#1A1F2E',
                'border': '1px solid #1f2535',
                'borderRadius': '10px',
                'padding': '20px 24px',
            },
            children=[
                html.Div(
                    style={'display': 'flex', 'alignItems': 'center',
                           'gap': '12px', 'marginBottom': '6px'},
                    children=[
                        html.Div(
                            style={
                                'background': 'linear-gradient(135deg, #00d4e8, #a05aff)',
                                'borderRadius': '6px', 'padding': '4px 10px',
                                'fontSize': '11px', 'fontWeight': '700',
                                'color': '#fff', 'letterSpacing': '1px',
                            },
                            children="SHAP XAI"
                        ),
                        html.H3(
                            "Live Explainability — Why the Model Made Its Last Prediction",
                            style={'color': '#00d4e8', 'margin': 0,
                                   'fontSize': '16px', 'fontWeight': '600'}
                        ),
                    ]
                ),
                html.P(
                    "Each bar shows a feature's SHAP contribution to the current device prediction. "
                    "Green = pushes model TOWARD that device type. Red = pushes AWAY.",
                    style={'color': '#6b7898', 'fontSize': '12px', 'marginBottom': '12px'}
                ),
                dcc.Graph(id='shap-bar'),
            ]
        ),
    ]
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _card(title, value, subtitle="", color="#2196F3"):
    return html.Div(
        style={'backgroundColor': '#1A1F2E', 'border': f'1px solid {color}',
               'borderRadius': '8px', 'padding': '16px 20px',
               'flex': '1', 'minWidth': '140px'},
        children=[
            html.P(title, style={'margin': '0 0 4px', 'fontSize': '12px',
                                 'color': '#90A4AE', 'textTransform': 'uppercase',
                                 'letterSpacing': '1px'}),
            html.H2(value, style={'margin': '0', 'fontSize': '28px',
                                  'fontWeight': '700', 'color': color}),
            html.P(subtitle, style={'margin': '4px 0 0', 'fontSize': '11px',
                                    'color': '#607D8B'}),
        ]
    )


def _api_get(endpoint, fallback=None):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", timeout=3)
        return r.json() if r.status_code == 200 else fallback
    except Exception:
        return fallback


def _api_post(endpoint, data=None):
    try:
        r = requests.post(f"{API_BASE}{endpoint}", json=data, timeout=4)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def _simulate_flow():
    devices = list(DEVICE_COLORS.keys())[:-1]
    device  = random.choice(devices)
    score   = random.gauss(0.3, 0.15)
    score   = max(0.0, min(1.0, score))
    if random.random() < 0.08:
        score = random.uniform(0.76, 0.98)
    return device, round(score, 4)


def _shap_placeholder(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message, x=0.5, y=0.5, xref='paper', yref='paper',
        showarrow=False, font=dict(color='#6b7898', size=13),
    )
    fig.update_layout(
        paper_bgcolor='#12161F', plot_bgcolor='#12161F',
        font_color='#c9d1e0', height=220,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig


# ---------------------------------------------------------------------------
# Main callback
# ---------------------------------------------------------------------------
@callback(
    Output('header-status',   'children'),
    Output('kpi-row',         'children'),
    Output('anomaly-timeline','figure'),
    Output('device-pie',      'figure'),
    Output('severity-bar',    'figure'),
    Output('score-gauge',     'figure'),
    Output('alerts-table',    'children'),
    Output('shap-bar',        'figure'),
    Input('interval',         'n_intervals'),
)
def refresh(n):
    metrics     = _api_get("/metrics", {
        "uptime_seconds": 0, "request_count": n * 3,
        "total_alerts": 0, "anomaly_rate": 0.0,
        "models_loaded": False, "shap_ready": False,
    })
    alerts_data = _api_get("/alerts/recent?n=20", {"alerts": [], "count": 0})

    # Simulate a live flow for demo
    device, score = _simulate_flow()
    is_alert = score >= 0.75
    _score_history.append({'time': time.time(), 'device': device, 'score': score, 'alert': is_alert})
    if len(_score_history) > _MAX_HISTORY:
        _score_history.pop(0)

    if is_alert:
        _api_post("/demo/inject", {"device_type": device, "anomaly_score": score})

    # ── Header status ─────────────────────────────────────────────────────
    model_status = "Models Loaded" if metrics.get('models_loaded') else "No Models — Run train.py"
    shap_status  = " | SHAP Ready" if metrics.get('shap_ready') else ""
    uptime_s = int(metrics.get('uptime_seconds', 0))
    h, m, s  = uptime_s // 3600, (uptime_s % 3600) // 60, uptime_s % 60
    status_el = html.Div([
        html.Div(f"Status: {model_status}{shap_status}",
                 style={'color': '#A5D6A7' if metrics.get('models_loaded') else '#EF9A9A'}),
        html.Div(f"Uptime: {h:02d}:{m:02d}:{s:02d}"),
        html.Div(f"Requests: {metrics.get('request_count', 0)}"),
    ])

    # ── KPI Cards ─────────────────────────────────────────────────────────
    kpis = [
        _card("Total Alerts",    str(metrics.get('total_alerts', 0)),        "anomaly events",      "#F44336"),
        _card("Anomaly Rate",    f"{metrics.get('anomaly_rate', 0)*100:.1f}%","of processed flows",  "#FF9800"),
        _card("Requests",        str(metrics.get('request_count', 0)),       "API calls served",    "#2196F3"),
        _card("Devices",         "8",                                         "supported IoT types", "#4CAF50"),
        _card("Features",        "37",                                        "per-flow features",   "#9C27B0"),
        _card("Alert Threshold", "0.75",                                      "ensemble score",      "#00BCD4"),
    ]

    # ── Anomaly Timeline ──────────────────────────────────────────────────
    hist_df = pd.DataFrame(_score_history) if _score_history else pd.DataFrame(
        columns=['time', 'device', 'score', 'alert'])

    fig_timeline = go.Figure()
    if not hist_df.empty:
        fig_timeline.add_trace(go.Scatter(
            x=list(range(len(hist_df))),
            y=hist_df['score'],
            mode='lines+markers',
            name='Anomaly Score',
            line=dict(color='#42A5F5', width=2),
            marker=dict(
                color=['#F44336' if a else '#42A5F5' for a in hist_df['alert']],
                size=[10 if a else 5 for a in hist_df['alert']],
                symbol=['x' if a else 'circle' for a in hist_df['alert']],
            ),
        ))
        fig_timeline.add_hline(y=0.75, line_dash='dash', line_color='red',
                               annotation_text='Alert Threshold (0.75)')
    fig_timeline.update_layout(
        title='Live Anomaly Score Timeline', paper_bgcolor='#1A1F2E',
        plot_bgcolor='#12161F', font_color='#E0E0E0',
        margin=dict(l=40, r=20, t=40, b=30), height=280,
        xaxis_title='Flow Index', yaxis_title='Anomaly Score',
        yaxis=dict(range=[0, 1.05]),
        legend=dict(bgcolor='rgba(0,0,0,0)'),
    )

    # ── Device Pie ────────────────────────────────────────────────────────
    dev_counts = hist_df['device'].value_counts() if not hist_df.empty else pd.Series()
    fig_pie = go.Figure(go.Pie(
        labels=dev_counts.index.tolist() if not dev_counts.empty else ['No data'],
        values=dev_counts.values.tolist() if not dev_counts.empty else [1],
        hole=0.45,
        marker=dict(colors=[DEVICE_COLORS.get(d, '#9E9E9E') for d in
                             (dev_counts.index if not dev_counts.empty else [])]),
        textinfo='label+percent', textfont_size=10,
    ))
    fig_pie.update_layout(
        title='Detected Device Types', paper_bgcolor='#1A1F2E',
        font_color='#E0E0E0', margin=dict(l=10, r=10, t=40, b=10), height=280,
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(size=9)),
        showlegend=False,
    )

    # ── Severity Bar ──────────────────────────────────────────────────────
    alert_list = alerts_data.get('alerts', [])
    sev_counts = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
    for a in alert_list:
        sev = a.get('severity', '')
        if sev in sev_counts:
            sev_counts[sev] += 1

    fig_sev = go.Figure(go.Bar(
        x=list(sev_counts.keys()),
        y=list(sev_counts.values()),
        marker_color=[SEVERITY_COLORS[k] for k in sev_counts],
        text=list(sev_counts.values()),
        textposition='outside',
    ))
    fig_sev.update_layout(
        title='Alerts by Severity', paper_bgcolor='#1A1F2E',
        plot_bgcolor='#12161F', font_color='#E0E0E0',
        margin=dict(l=30, r=20, t=40, b=30), height=250,
        yaxis_title='Count', showlegend=False,
    )

    # ── Score Gauge ───────────────────────────────────────────────────────
    latest_score = hist_df['score'].iloc[-1] if not hist_df.empty else 0.0
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(latest_score, 3),
        title={'text': "Latest Anomaly Score", 'font': {'color': '#E0E0E0'}},
        number={'font': {'color': '#E0E0E0', 'size': 36}},
        delta={'reference': 0.75,
               'increasing': {'color': '#F44336'},
               'decreasing': {'color': '#4CAF50'}},
        gauge={
            'axis': {'range': [0, 1], 'tickcolor': '#90A4AE', 'tickfont': {'color': '#90A4AE'}},
            'bar': {'color': '#F44336' if latest_score >= 0.75 else '#42A5F5'},
            'bgcolor': '#1A1F2E',
            'steps': [
                {'range': [0,    0.50], 'color': '#1B5E20'},
                {'range': [0.50, 0.65], 'color': '#E65100'},
                {'range': [0.65, 0.80], 'color': '#B71C1C'},
                {'range': [0.80, 1.00], 'color': '#4A0072'},
            ],
            'threshold': {'line': {'color': 'red', 'width': 3}, 'value': 0.75},
        },
    ))
    fig_gauge.update_layout(
        paper_bgcolor='#1A1F2E', font_color='#E0E0E0',
        margin=dict(l=20, r=20, t=40, b=20), height=250,
    )

    # ── Alerts Table ──────────────────────────────────────────────────────
    if not alert_list:
        table = html.P("No alerts recorded yet.",
                       style={'color': '#607D8B', 'fontStyle': 'italic'})
    else:
        header = html.Tr([
            html.Th(col, style={'padding': '8px 12px', 'borderBottom': '1px solid #37474F',
                                'color': '#90CAF9', 'textAlign': 'left'})
            for col in ['#', 'Time', 'Source IP', 'Device', 'Score', 'Severity', 'Message']
        ])
        rows = []
        for a in alert_list[:15]:
            sev   = a.get('severity', '')
            color = SEVERITY_COLORS.get(sev, '#9E9E9E')
            t     = time.strftime('%H:%M:%S', time.localtime(a.get('timestamp', 0)))
            rows.append(html.Tr([
                html.Td(str(a.get('alert_id', '')),
                        style={'padding': '6px 12px', 'color': '#90A4AE'}),
                html.Td(t, style={'padding': '6px 12px'}),
                html.Td(a.get('source_ip', ''),
                        style={'padding': '6px 12px', 'fontFamily': 'monospace'}),
                html.Td(a.get('device_type', '').replace('smart_', '').replace('_', ' ').title(),
                        style={'padding': '6px 12px',
                               'color': DEVICE_COLORS.get(a.get('device_type', ''), '#9E9E9E')}),
                html.Td(str(a.get('anomaly_score', '')), style={'padding': '6px 12px'}),
                html.Td(sev, style={'padding': '6px 12px', 'fontWeight': '700', 'color': color}),
                html.Td(a.get('message', ''),
                        style={'padding': '6px 12px', 'fontSize': '12px'}),
            ], style={'borderBottom': '1px solid #1E272E'}))

        table = html.Table(
            [html.Thead(header), html.Tbody(rows)],
            style={'width': '100%', 'borderCollapse': 'collapse',
                   'backgroundColor': '#1A1F2E', 'borderRadius': '8px', 'fontSize': '13px'},
        )

    # ── SHAP Explainability Bar ───────────────────────────────────────────
    device_flow  = _build_device_flow(device)
    explain_data = _api_post("/explain", device_flow)

    if explain_data and "explanation" in explain_data:
        predicted = explain_data.get("device_type", device)
        conf      = explain_data.get("confidence", 0.0)
        contribs  = explain_data["explanation"]

        feat_labels = [c["feature"].replace("_", " ") for c in contribs]
        shap_vals   = [c["shap_value"] for c in contribs]
        bar_colors  = ["#00e580" if v > 0 else "#ff4757" for v in shap_vals]

        device_label = predicted.replace("smart_", "").replace("_", " ").title()
        title_text   = (
            f"SHAP: Why the model says → <b>{device_label}</b> "
            f"({conf:.0%} confidence)"
        )

        fig_shap = go.Figure(go.Bar(
            y=feat_labels[::-1],
            x=shap_vals[::-1],
            orientation='h',
            marker_color=bar_colors[::-1],
            marker_line_color='#1f2535',
            marker_line_width=0.8,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "SHAP value: %{x:.5f}<br>"
                "<extra></extra>"
            ),
        ))
        fig_shap.add_vline(x=0, line_color='#6b7898', line_width=1.2)

        fig_shap.update_layout(
            title=dict(text=title_text, font=dict(color='#00d4e8', size=13)),
            paper_bgcolor='#12161F',
            plot_bgcolor='#12161F',
            font_color='#c9d1e0',
            margin=dict(l=160, r=80, t=50, b=40),
            height=360,
            xaxis=dict(
                title='SHAP Value  (feature contribution to model output)',
                title_font=dict(color='#6b7898', size=11),
                tickfont=dict(color='#c9d1e0', size=10),
                gridcolor='#1f2535', zeroline=False,
            ),
            yaxis=dict(
                tickfont=dict(color='#c9d1e0', size=11),
                gridcolor='#1f2535',
            ),
            showlegend=False,
            annotations=[
                dict(
                    x=0.01, y=1.06, xref='paper', yref='paper',
                    text="<span style='color:#00e580'>&#9646; toward device</span>"
                         "    "
                         "<span style='color:#ff4757'>&#9646; away from device</span>",
                    showarrow=False,
                    font=dict(size=11),
                    align='left',
                )
            ],
        )
    else:
        fig_shap = _shap_placeholder(
            "SHAP data unavailable — ensure API is running with models loaded (run train.py)"
        )

    return status_el, kpis, fig_timeline, fig_pie, fig_sev, fig_gauge, table, fig_shap


if __name__ == "__main__":
    app.run(debug=False, port=8050, host="0.0.0.0")
