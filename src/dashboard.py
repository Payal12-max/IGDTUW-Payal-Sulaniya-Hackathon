import html
import math
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

CURRENT_DIR = Path(__file__).resolve().parent

if (CURRENT_DIR / "data").exists():
    PROJECT_ROOT = CURRENT_DIR
else:
    PROJECT_ROOT = CURRENT_DIR.parent

DATA_PATH = PROJECT_ROOT / "data" / "integrated_risk_results.csv"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STRESS_THRESHOLD = 7
PALETTE = ["#b8f53c", "#6fae1d", "#3f6b14", "#e4f5c8", "#8b9399", "#566127"]

st.set_page_config(
    page_title="RiskPulse | Event-Driven Stress Testing",
    page_icon="R",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

:root {
    --bg: #0b0d0e;
    --card: #14171a;
    --card2: #1a1e21;
    --line: #23282c;
    --ink: #f2f4f3;
    --muted: #8b9399;
    --lime: #b8f53c;
    --lime-d: #1d2a14;
    --good: #b8f53c;
    --bad: #ff6b5e;
    --warn: #e6b04a;
}

.stApp, .stMarkdown, .stSelectbox label {
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
}
.stApp { background: var(--bg); color: var(--ink); font-size: 16px; }
.block-container { max-width: 1400px; padding-top: 1.2rem; padding-bottom: 4rem; }
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
svg text { font-family: inherit; }

/* ---------- Streamlit widgets, dark ---------- */
.stSelectbox label p { font-size: 14px; color: var(--muted); }
[data-baseweb="select"] > div { background: var(--card) !important; border: 1px solid var(--line) !important;
    border-radius: 14px !important; color: var(--ink) !important; font-size: 15px; }
[data-baseweb="select"] * { color: var(--ink) !important; }
[data-baseweb="popover"] > div, [data-baseweb="popover"] ul { background: var(--card) !important; }
[data-baseweb="popover"] li { color: var(--ink) !important; }
[data-baseweb="popover"] li:hover { background: var(--card2) !important; }

/* ---------- Tabs as a pill navigation ---------- */
[data-baseweb="tab-list"] { background: var(--card); border: 1px solid var(--line); border-radius: 999px;
    padding: 6px; gap: 4px; width: fit-content; margin: 6px auto 10px auto; }
button[data-baseweb="tab"] { background: transparent; border-radius: 999px; padding: 10px 26px; height: auto; }
button[data-baseweb="tab"] p { font-size: 15px; font-weight: 500; color: var(--muted); }
button[data-baseweb="tab"][aria-selected="true"] { background: var(--lime); }
button[data-baseweb="tab"][aria-selected="true"] p { color: #0b0d0e !important; font-weight: 700; }
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none; }

/* ---------- Header ---------- */
.head { display: flex; justify-content: space-between; align-items: center; }
.logo, .head-meta { background: var(--card); border: 1px solid var(--line); border-radius: 999px;
    padding: 10px 22px 10px 12px; display: flex; align-items: center; gap: 12px; font-weight: 600; font-size: 17px; }
.head-meta { padding: 11px 22px; font-size: 14px; font-weight: 500; color: var(--muted); gap: 10px; }
.mark { width: 30px; height: 30px; border-radius: 9px; background: var(--lime); display: flex;
    flex-direction: column; justify-content: center; gap: 4px; padding: 0 7px; }
.mark i { display: block; height: 4px; background: #0b0d0e; border-radius: 2px; }
.mark i:nth-child(2) { width: 62%; }
.live { width: 8px; height: 8px; border-radius: 50%; background: var(--lime); }

/* ---------- Layout ---------- */
.title { font-size: 38px; font-weight: 600; letter-spacing: -0.5px; margin: 26px 0 4px 0; }
.subtitle { font-size: 17px; color: var(--muted); margin-bottom: 22px; }
.row { display: grid; gap: 16px; margin-top: 16px; }
.r4 { grid-template-columns: repeat(4, 1fr); }
.r-event { grid-template-columns: 1.5fr 1fr; }
.r-charts { grid-template-columns: 1.3fr 1fr; }
.r-bottom { grid-template-columns: 1fr 1.1fr 1.2fr; }
.r-two { grid-template-columns: 1fr 1fr; }
.r-three { grid-template-columns: repeat(3, 1fr); }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 22px; padding: 26px 28px; min-width: 0; }
.card-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; gap: 12px; }
.card-title { font-size: 22px; font-weight: 500; margin: 0; }
.chip { border: 1px solid var(--line); background: var(--card2); border-radius: 999px; padding: 8px 18px;
    font-size: 14px; color: var(--ink); white-space: nowrap; }
.chip.lime { background: var(--lime); color: #0b0d0e; border-color: var(--lime); font-weight: 600; }
.legend-row { display: flex; gap: 10px; margin: -4px 0 12px 0; align-items: center; font-size: 14px; color: var(--muted); }
.t-good { color: var(--good); } .t-bad { color: var(--bad); } .t-warn { color: var(--warn); } .t-mute { color: var(--muted); }

/* ---------- KPI ---------- */
.kpi { background: var(--card); border: 1px solid var(--line); border-radius: 22px; padding: 22px 26px 24px 26px; }
.kpi-top { display: flex; justify-content: space-between; align-items: center; font-size: 16px; color: var(--ink); }
.arrow { width: 40px; height: 40px; border-radius: 50%; background: var(--card2); border: 1px solid var(--line);
    display: grid; place-items: center; color: var(--ink); }
.kpi-val { font-size: 36px; font-weight: 600; letter-spacing: -0.8px; margin-top: 12px; font-variant-numeric: tabular-nums; }
.kpi-sub { font-size: 14.5px; margin-top: 8px; }

/* ---------- Event ---------- */
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 18px; }
.ev-head { font-size: 28px; line-height: 1.35; font-weight: 500; letter-spacing: -0.3px; margin: 0; }
.scale-head { font-size: 14.5px; color: var(--muted); margin-bottom: 46px; line-height: 1.5; }
.scale-body { position: relative; margin: 0 8px; }
.track { display: flex; height: 14px; border-radius: 999px; overflow: hidden; gap: 3px; }
.track div { height: 100%; }
.z1 { background: #2f4a1a; } .z2 { background: #6e9a1c; } .z3 { background: #d6a53a; } .z4 { background: #e0584a; }
.thresh { position: absolute; top: -8px; height: 30px; border-left: 2px dashed #e9eee9; }
.marker { position: absolute; top: -8px; height: 30px; width: 4px; background: #fff; border-radius: 2px; transform: translateX(-50%); }
.marker span { position: absolute; bottom: 38px; left: 50%; transform: translateX(-50%); background: var(--lime);
    color: #0b0d0e; font-size: 15px; font-weight: 700; padding: 3px 12px; border-radius: 999px; white-space: nowrap; }
.zones { display: flex; margin-top: 14px; font-size: 13.5px; color: var(--muted); }

/* ---------- Lists, goals ---------- */
.ico { width: 46px; height: 46px; border-radius: 50%; background: var(--lime-d); color: var(--lime);
    display: grid; place-items: center; flex: none; }
.ico.sm { width: 40px; height: 40px; }
.goal + .goal { margin-top: 30px; }
.goal-top { display: flex; align-items: center; gap: 14px; }
.goal-title { font-size: 16px; }
.goal-val { font-size: 25px; font-weight: 600; font-variant-numeric: tabular-nums; }
.goal-val small { font-size: 16px; color: var(--muted); font-weight: 400; }
.goal-pct { margin-left: auto; font-size: 16px; color: var(--muted); }
.pbar { height: 12px; background: var(--card2); border-radius: 999px; margin: 14px 0 10px 0; overflow: hidden; }
.pbar div { height: 100%; background: var(--lime); border-radius: 999px; }
.pbar.red div { background: var(--bad); }
.goal-foot { display: flex; justify-content: space-between; font-size: 14.5px; color: var(--muted); }

.li { display: grid; grid-template-columns: 46px 1fr auto auto; align-items: center; gap: 16px; padding: 12px 0; }
.li + .li { border-top: 1px solid var(--line); }
.li .ini { width: 46px; height: 46px; border-radius: 50%; background: var(--card2); border: 1px solid var(--line);
    display: grid; place-items: center; font-weight: 600; color: var(--lime); }
.li .nm { font-size: 16px; font-weight: 500; }
.li .sb { font-size: 13.5px; color: var(--muted); margin-top: 2px; }
.li .pc { font-size: 14.5px; color: var(--muted); text-align: right; min-width: 56px; }
.li .am { font-size: 16px; font-weight: 600; text-align: right; min-width: 96px; font-variant-numeric: tabular-nums; }

.minis { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.mini { background: var(--card); border: 1px solid var(--line); border-radius: 22px; padding: 20px 22px; }
.mini-top { display: flex; align-items: center; gap: 12px; font-size: 15px; color: var(--muted); }
.mini-val { font-size: 28px; font-weight: 600; margin: 18px 0 14px 0; font-variant-numeric: tabular-nums; letter-spacing: -0.5px; }
.pill { display: inline-block; background: var(--card2); border: 1px solid var(--line); border-radius: 999px; padding: 6px 16px; font-size: 14px; }

/* ---------- Donut legend ---------- */
.donut-wrap { display: grid; grid-template-columns: 230px 1fr; gap: 22px; align-items: center; }
.leg { display: flex; align-items: center; gap: 12px; padding: 9px 0; font-size: 15.5px; }
.leg .dot { width: 10px; height: 10px; border-radius: 50%; flex: none; }
.leg .v { margin-left: auto; font-weight: 600; font-variant-numeric: tabular-nums; }
.leg .s { color: var(--muted); min-width: 62px; text-align: right; font-variant-numeric: tabular-nums; }

/* ---------- Table ---------- */
.tbl-wrap { overflow-x: auto; }
.tbl { width: 100%; border-collapse: collapse; font-size: 15.5px; font-variant-numeric: tabular-nums; }
.tbl th { text-align: right; font-weight: 500; color: var(--muted); padding: 12px 14px; border-bottom: 1px solid var(--line); font-size: 14px; }
.tbl td { text-align: right; padding: 15px 14px; border-bottom: 1px solid var(--line); }
.tbl th:nth-child(-n+3), .tbl td:nth-child(-n+3) { text-align: left; }
.tbl tr:last-child td { border-bottom: 0; }
.lbar { display: flex; align-items: center; justify-content: flex-end; gap: 12px; }
.lbar i { display: block; height: 8px; border-radius: 999px; background: var(--bad); min-width: 3px; }

/* ---------- Misc ---------- */
.note { background: var(--card); border: 1px solid var(--line); border-radius: 22px; padding: 26px 28px;
    font-size: 17px; line-height: 1.6; }
.note b { color: var(--lime); font-weight: 600; }
.plain-list { margin: 6px 0 0 0; padding-left: 20px; color: var(--muted); font-size: 16px; line-height: 1.9; }
.kv { display: flex; justify-content: space-between; padding: 11px 0; font-size: 15.5px; border-top: 1px solid var(--line); }
.kv span:first-child { color: var(--muted); }
.footer { margin-top: 40px; color: var(--muted); font-size: 13.5px; line-height: 1.65; max-width: 900px; }

@media (max-width: 1000px) {
    .r4 { grid-template-columns: repeat(2, 1fr); }
    .r-event, .r-charts, .r-bottom, .r-two, .r-three { grid-template-columns: 1fr; }
    .donut-wrap { grid-template-columns: 1fr; }
    .head { flex-direction: column; gap: 10px; align-items: flex-start; }
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

def esc(value):
    return html.escape(str(value))

def block(markup):
    """Render HTML. Lines are stripped so Markdown never treats them as code."""
    cleaned = " ".join(line.strip() for line in markup.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)

def to_bool(value):
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes")
    return bool(value)

def compact(v):
    a = abs(v)
    if a >= 1e9:
        s = f"{v / 1e9:.1f}B"
    elif a >= 1e6:
        s = f"{v / 1e6:.1f}M"
    elif a >= 1e3:
        s = f"{v / 1e3:.0f}K"
    else:
        s = f"{v:.0f}"
    return s.replace(".0B", "B").replace(".0M", "M")

ICONS = {
    "bolt": "M13 2 4 14h7l-1 8 9-12h-7z",
    "shield": "M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z",
    "trend": "M3 17l6-6 4 4 8-8M15 7h6v6",
    "layers": "M12 3l9 5-9 5-9-5zM3 13l9 5 9-5",
    "wallet": "M3 7h15a3 3 0 0 1 3 3v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2zM3 7l12-3v3M17 14h2",
    "pulse": "M3 12h4l3-8 4 16 3-8h4",
    "down": "M3 7l6 6 4-4 8 8M15 17h6v-6",
}


def icon(name, size=20):
    return (
        f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" '
        f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="{ICONS[name]}"/></svg>'
    )

ARROW = (
    '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round"><path d="M7 17 17 7M8 7h9v9"/></svg>'
)

def nice_scale(peak, divisions=4):
    if peak <= 0:
        return 1.0, float(divisions)
    raw = peak / divisions
    mag = 10 ** math.floor(math.log10(raw))
    step = 10 * mag
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            step = m * mag
            break
    ymax = step * math.ceil(peak / step - 1e-9)
    return step, ymax


def bars_svg(uid, labels, series, colors=None, avg=None, W=760, H=310):
    """Vertical bar chart. One series gets the gradient look, several get grouped bars."""
    left, right, top, bottom = 58, 8, 30, 46
    pw, ph = W - left - right, H - top - bottom
    peak = max([max(s) for s in series] + [0])
    step, ymax = nice_scale(peak)
    n = len(series)

    o = [
        f'<svg viewBox="0 0 {W} {H}" width="100%" role="img">',
        f'<defs><linearGradient id="hi{uid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#b8f53c" stop-opacity="0.95"/>'
        f'<stop offset="1" stop-color="#4c7d18" stop-opacity="0.25"/></linearGradient>'
        f'<linearGradient id="lo{uid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#6fae1d" stop-opacity="0.8"/>'
        f'<stop offset="1" stop-color="#2f4a12" stop-opacity="0.15"/></linearGradient></defs>',
    ]

    for k in range(int(round(ymax / step)) + 1):
        val = k * step
        y = top + ph - ph * val / ymax
        o.append(f'<line x1="{left}" x2="{W - right}" y1="{y:.1f}" y2="{y:.1f}" stroke="#23282c" stroke-width="1"/>')
        o.append(f'<text x="{left - 12}" y="{y + 4.5:.1f}" text-anchor="end" font-size="13" fill="#8b9399">{compact(val)}</text>')

    slot = pw / max(len(labels), 1)
    group_w = slot * 0.64
    gap = 5 if n > 1 else 0
    bw = (group_w - gap * (n - 1)) / n
    best = series[0].index(max(series[0])) if n == 1 and series[0] else -1

    for i, lab in enumerate(labels):
        x0 = left + i * slot + (slot - group_w) / 2
        for j, s in enumerate(series):
            h = max(ph * s[i] / ymax, 1)
            x = x0 + j * (bw + gap)
            y = top + ph - h
            if n == 1:
                fill = f"url(#hi{uid})" if i == best else f"url(#lo{uid})"
            else:
                fill = colors[j]
            o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="6" fill="{fill}"/>')
        short = lab if len(lab) <= 10 else lab[:9] + "..."
        o.append(
            f'<text x="{left + i * slot + slot / 2:.1f}" y="{H - 16}" text-anchor="middle" '
            f'font-size="13" fill="#8b9399">{esc(short)}</text>'
        )

    if avg is not None and ymax > 0:
        y = top + ph - ph * avg / ymax
        o.append(f'<line x1="{left}" x2="{W - right}" y1="{y:.1f}" y2="{y:.1f}" stroke="#b8f53c" stroke-width="1.6" stroke-dasharray="6 6"/>')
        tag = f"Avg {compact(avg)}"
        tw = 12 + 8.2 * len(tag)
        o.append(f'<rect x="{left + 6}" y="{y - 26:.1f}" width="{tw:.0f}" height="22" rx="6" fill="#2a3a18"/>')
        o.append(f'<text x="{left + 6 + tw / 2:.0f}" y="{y - 10.5:.1f}" text-anchor="middle" font-size="13" fill="#b8f53c" font-weight="600">{tag}</text>')

    o.append("</svg>")
    return "".join(o)


def donut_svg(values, top_label, main_label):
    total = sum(values)
    r, cx = 78, 110
    circ = 2 * math.pi * r
    o = ['<svg viewBox="0 0 220 220" width="100%" role="img">']
    offset = 0.0
    for i, v in enumerate(values):
        frac = v / total if total > 0 else 0
        seg = max(frac * circ - 4, 0)
        o.append(
            f'<circle cx="{cx}" cy="{cx}" r="{r}" fill="none" stroke="{PALETTE[i % len(PALETTE)]}" '
            f'stroke-width="34" stroke-dasharray="{seg:.2f} {circ - seg:.2f}" '
            f'stroke-dashoffset="{-(offset + 2):.2f}" transform="rotate(-90 {cx} {cx})"/>'
        )
        offset += frac * circ
    main = main_label if len(main_label) <= 13 else main_label[:12] + "..."
    o.append(f'<text x="{cx}" y="{cx - 8}" text-anchor="middle" font-size="12.5" fill="#8b9399">{esc(top_label)}</text>')
    o.append(f'<text x="{cx}" y="{cx + 17}" text-anchor="middle" font-size="19" font-weight="600" fill="#f2f4f3">{esc(main)}</text>')
    o.append("</svg>")
    return "".join(o)


def donut_card(title, chip, frame, label_col, value_col, top_label):
    values = [float(v) for v in frame[value_col]]
    names = [str(n) for n in frame[label_col]]
    total = sum(values)
    legend = ""
    for i, (nm, v) in enumerate(zip(names, values)):
        share = v / total * 100 if total > 0 else 0
        legend += (
            f'<div class="leg"><span class="dot" style="background:{PALETTE[i % len(PALETTE)]}"></span>'
            f'<span>{esc(nm)}</span><span class="v">{v:,.0f}</span><span class="s">({share:.1f}%)</span></div>'
        )
    svg = donut_svg(values, top_label, names[0] if names else "n/a")
    return (
        f'<div class="card"><div class="card-head"><h3 class="card-title">{esc(title)}</h3>'
        f'<span class="chip">{esc(chip)}</span></div>'
        f'<div class="donut-wrap"><div>{svg}</div><div>{legend}</div></div></div>'
    )


def kpi(label, value, sub, tone):
    return (
        f'<div class="kpi"><div class="kpi-top"><span>{esc(label)}</span><span class="arrow">{ARROW}</span></div>'
        f'<div class="kpi-val">{value}</div><div class="kpi-sub t-{tone}">{sub}</div></div>'
    )


def goal(icon_name, title, value_txt, unit, pct, foot_left, status, tone, bar_class=""):
    return (
        f'<div class="goal"><div class="goal-top"><span class="ico">{icon(icon_name)}</span>'
        f'<div><div class="goal-title">{esc(title)}</div><div class="goal-val">{value_txt} <small>{unit}</small></div></div>'
        f'<span class="goal-pct">{pct:.0f}%</span></div>'
        f'<div class="pbar {bar_class}"><div style="width:{max(0, min(pct, 100)):.1f}%"></div></div>'
        f'<div class="goal-foot"><span>{foot_left}</span><span class="t-{tone}">{status}</span></div></div>'
    )


def mini(icon_name, label, value, pill):
    return (
        f'<div class="mini"><div class="mini-top"><span class="ico sm">{icon(icon_name, 18)}</span>{esc(label)}</div>'
        f'<div class="mini-val">{value}</div><span class="pill">{pill}</span></div>'
    )

@st.cache_data
def load_results():
    if not DATA_PATH.exists():
        return None
    return pd.read_csv(DATA_PATH)

df = load_results()

if df is None:
    st.error(
        f"Risk results file was not found at:\n\n"
        f"`{DATA_PATH}`\n\n"
        f"Run:\n\n"
        f"`python src/integrated_risk_pipeline.py`"
    )
    st.stop()

if df.empty:
    st.error("The integrated risk results file is empty.")
    st.stop()

block(
    f"""
    <div class="head">
        <div class="logo"><span class="mark"><i></i><i></i></span>RiskPulse</div>
        <div class="head-meta"><span class="live"></span>Results loaded<span>{len(df)} event(s)</span></div>
    </div>
    """
)

event_index = 0
if len(df) > 1:
    sel, _ = st.columns([2, 3])
    with sel:
        event_index = st.selectbox(
            "Event under review",
            options=list(range(len(df))),
            format_func=lambda i: (
                f"{str(df.iloc[i].get('date', ''))[:10]}   "
                f"{str(df.iloc[i].get('text', ''))[:80]}"
            ),
        )

row = df.iloc[event_index]

headline = str(row.get("text", "N/A"))
entity = str(row.get("entity", "N/A"))
source = str(row.get("source", "N/A"))
date = str(row.get("date", "N/A"))

sentiment_score = float(row.get("sentiment_score", 0))
sentiment_label = str(row.get("sentiment_label", "N/A"))

event_class = str(row.get("event_class", "Unclassified"))
confidence = float(row.get("event_confidence", 0))
method = str(row.get("classification_method", "N/A"))

impact_score = float(row.get("impact_score", 0))
stress_trigger = to_bool(row.get("stress_trigger", False))

if impact_score >= 9:
    risk_level, level_tone = "Critical", "bad"
elif impact_score >= 7:
    risk_level, level_tone = "High", "bad"
elif impact_score >= 4:
    risk_level, level_tone = "Moderate", "warn"
else:
    risk_level, level_tone = "Low", "good"

sent_tone = "bad" if sentiment_score <= -0.05 else ("good" if sentiment_score >= 0.05 else "mute")

positions = summary = scenario = None

if stress_trigger:
    try:
        from src.portfolio_stress import (
            load_portfolio,
            stress_test_portfolio,
            get_stress_scenario,
        )

        portfolio = load_portfolio()
        positions, summary = stress_test_portfolio(portfolio, event_class)
        scenario = get_stress_scenario(event_class)

        portfolio_before = summary["portfolio_value_before"]
        portfolio_after = summary["portfolio_value_after"]
        portfolio_loss = summary["portfolio_loss"]
        loss_percent = summary["portfolio_loss_percent"]

        positions = positions.copy()
        if "sector" in positions.columns:
            positions["sector"] = positions["sector"].fillna("Unassigned")

    except Exception as e:
        st.error(f"Portfolio stress calculation failed: {e}")
        st.stop()

tab_overview, tab_stress, tab_positions, tab_method = st.tabs(
    ["Overview", "Stress Test", "Positions", "Methodology"]
)

with tab_overview:

    block(
        f"""
        <div class="title">Risk Overview</div>
        <div class="subtitle">Event-driven portfolio stress test for {esc(entity)}</div>
        """
    )

    if stress_trigger:
        k3 = kpi("Stress Loss", f"-{portfolio_loss:,.0f}", f"-{loss_percent:.2f}% of portfolio value", "bad")
    else:
        k3 = kpi("Stress Loss", "None", "Scenario not triggered", "good")

    block(
        '<div class="row r4">'
        + kpi("Impact Score", f"{impact_score:.1f} / 10", f"{risk_level} severity", level_tone)
        + kpi("Sentiment Score", f"{sentiment_score:+.3f}", esc(sentiment_label.title()), sent_tone)
        + k3
        + kpi("Event Class", esc(event_class), f"Confidence {confidence:.2f}", "good")
        + "</div>"
    )

    marker_pct = max(0.0, min(impact_score / 10 * 100, 100.0))
    thresh_pct = STRESS_THRESHOLD / 10 * 100

    block(
        f"""
        <div class="row r-event">
            <div class="card">
                <div class="card-head"><h3 class="card-title">Detected Event</h3><span class="chip lime">{esc(entity)}</span></div>
                <div class="chips">
                    <span class="chip">{esc(event_class)}</span>
                    <span class="chip">{esc(date[:10])}</span>
                    <span class="chip">{esc(source[:40])}</span>
                </div>
                <p class="ev-head">{esc(headline)}</p>
            </div>
            <div class="card">
                <div class="card-head"><h3 class="card-title">Impact Scale</h3><span class="chip">Stress trigger &gt; {STRESS_THRESHOLD}</span></div>
                <div class="scale-head">1–10 severity scale for classified events; 0 for unclassified. Impact &gt; 7 triggers the stress scenario.</div>
                <div class="scale-body">
                    <div class="track">
                        <div class="z1" style="width:40%"></div><div class="z2" style="width:30%"></div>
                        <div class="z3" style="width:20%"></div><div class="z4" style="width:10%"></div>
                    </div>
                    <div class="thresh" style="left:{thresh_pct}%"></div>
                    <div class="marker" style="left:{marker_pct:.1f}%"><span>{impact_score:.1f}</span></div>
                    <div class="zones">
                        <div style="width:40%">Low</div><div style="width:30%">Moderate</div>
                        <div style="width:20%">High</div><div style="width:10%">Critical</div>
                    </div>
                </div>
            </div>
        </div>
        """
    )

    if stress_trigger:
        by_pos = positions.sort_values("loss", ascending=False)
        pos_labels = [str(a) for a in by_pos["asset_id"]]
        pos_loss = [float(v) for v in by_pos["loss"]]
        avg_loss = sum(pos_loss) / len(pos_loss) if pos_loss else 0

        bar_card = (
            '<div class="card"><div class="card-head"><h3 class="card-title">Stress Loss by Position</h3>'
            '<span class="chip">Synthetic units</span></div>'
            '<div class="legend-row"><span class="chip lime">Loss</span><span>Dashed line shows the average loss per position</span></div>'
            + bars_svg("pos", pos_labels, [pos_loss], avg=avg_loss)
            + "</div>"
        )
        by_asset = (
            positions.groupby("asset_type")["loss"].sum().sort_values(ascending=False).reset_index()
        )
        donut = donut_card("Loss by Asset Class", "All positions", by_asset, "asset_type", "loss", "Largest loss")

        block(f'<div class="row r-charts">{bar_card}{donut}</div>')

    goals = goal(
        "bolt",
        "Impact score",
        f"{impact_score:.1f}",
        "/ 10",
        impact_score / 10 * 100,
        f"Stress trigger: Impact > {STRESS_THRESHOLD}",
        "Above threshold" if stress_trigger else "Below threshold",
        "bad" if stress_trigger else "good",
        "red" if stress_trigger else "",
    ) + goal(
        "shield",
        "Classifier confidence",
        f"{confidence:.2f}",
        "/ 1.00",
        confidence * 100,
        f"Method: {esc(method)}",
        "High confidence" if confidence >= 0.8 else ("Moderate" if confidence >= 0.5 else "Low confidence"),
        "good" if confidence >= 0.8 else "warn",
    )
    if stress_trigger:
        goals += goal(
            "down",
            "Portfolio loss",
            f"{loss_percent:.2f}%",
            "of value",
            min(loss_percent, 100),
            f"{portfolio_loss:,.0f} units",
            "Stress applied",
            "bad",
            "red",
        )
    goals_card = f'<div class="card">{goals}</div>'

    if stress_trigger:
        top5 = positions.sort_values("loss", ascending=False).head(5)
        items = ""
        for _, p in top5.iterrows():
            items += (
                f'<div class="li"><div class="ini">{esc(str(p["asset_type"])[:1].upper())}</div>'
                f'<div><div class="nm">{esc(p["asset_id"])}</div>'
                f'<div class="sb">{esc(p["asset_type"])}, {esc(p.get("sector", ""))}</div></div>'
                f'<div class="pc">{p["loss_percent"]:.2f}%</div>'
                f'<div class="am t-bad">-{p["loss"]:,.0f}</div></div>'
            )
        list_card = (
            '<div class="card"><div class="card-head"><h3 class="card-title">Largest Position Losses</h3>'
            '<span class="chip">Top 5</span></div>' + items + "</div>"
        )

        minis = (
            '<div class="minis">'
            + mini("wallet", "Value before", f"{portfolio_before:,.0f}", "Synthetic units")
            + mini("down", "Value after", f"{portfolio_after:,.0f}", f"-{loss_percent:.2f}%")
            + mini("trend", "Equity shock", f"{scenario['equity_shock']:+.0%}", esc(event_class))
            + mini("pulse", "Rate shock", f"{scenario['rate_shock']:+.0%}", f"Credit {scenario['credit_shock']:+.0%}")
            + "</div>"
        )
        block(f'<div class="row r-bottom">{goals_card}{list_card}{minis}</div>')
    else:
        no_stress = (
            '<div class="note"><b>No stress scenario triggered.</b><br>'
            f"Impact score {impact_score:.1f} does not exceed the threshold of {STRESS_THRESHOLD}, "
            "so the portfolio was not re-valued for this event.</div>"
        )
        block(f'<div class="row r-two">{goals_card}{no_stress}</div>')

with tab_stress:

    block(
        """
        <div class="title">Stress Test</div>
        <div class="subtitle">Scenario shocks mapped from the event class and applied to every position</div>
        """
    )

    if stress_trigger:
        block(
            '<div class="row r4">'
            + kpi("Scenario", esc(event_class), f"Impact {impact_score:.1f}, stress trigger > {STRESS_THRESHOLD}", "bad")
            + kpi("Equity Shock", f"{scenario['equity_shock']:+.0%}", "Applied to equity sensitivity", "mute")
            + kpi("Rate Shock", f"{scenario['rate_shock']:+.0%}", "Applied to rate sensitivity", "mute")
            + kpi("Credit Shock", f"{scenario['credit_shock']:+.0%}", "Applied to credit sensitivity", "mute")
            + "</div>"
        )

        grouped = (
            positions.groupby("asset_type")[["market_value", "stressed_value"]].sum().reset_index()
        )
        grouped_card = (
            '<div class="card"><div class="card-head"><h3 class="card-title">Value Before and After</h3>'
            '<span class="chip">By asset class</span></div>'
            '<div class="legend-row"><span class="chip" style="background:#4d6b2a;border-color:#4d6b2a">Before</span>'
            '<span class="chip lime">After</span></div>'
            + bars_svg(
                "grp",
                [str(a) for a in grouped["asset_type"]],
                [
                    [float(v) for v in grouped["market_value"]],
                    [float(v) for v in grouped["stressed_value"]],
                ],
                colors=["#4d6b2a", "#b8f53c"],
            )
            + "</div>"
        )

        if "sector" in positions.columns:
            by_sector = (
                positions.groupby("sector")["loss"].sum().sort_values(ascending=False).reset_index()
            )
            sector_card = donut_card("Loss by Sector", "All positions", by_sector, "sector", "loss", "Largest loss")
        else:
            sector_card = ""

        block(f'<div class="row r-charts">{grouped_card}{sector_card}</div>')

        block(
            '<div class="row r-three">'
            f'<div class="card"><div class="card-title" style="margin-bottom:10px">Portfolio before</div>'
            f'<div class="kpi-val">{portfolio_before:,.0f}</div><div class="kpi-sub t-mute">Synthetic portfolio units</div></div>'
            f'<div class="card"><div class="card-title" style="margin-bottom:10px">Portfolio after</div>'
            f'<div class="kpi-val">{portfolio_after:,.0f}</div><div class="kpi-sub t-mute">After scenario shocks</div></div>'
            f'<div class="card"><div class="card-title" style="margin-bottom:10px">Stress loss</div>'
            f'<div class="kpi-val t-bad">-{portfolio_loss:,.0f}</div><div class="kpi-sub t-bad">-{loss_percent:.2f}% of portfolio</div></div>'
            "</div>"
        )
    else:
        block(
            f'<div class="note"><b>No stress scenario triggered.</b><br>'
            f"Impact score {impact_score:.1f} does not exceed the threshold of {STRESS_THRESHOLD}. "
            "Select an event with a higher impact score to see portfolio stress results.</div>"
        )

with tab_positions:
    block(
        """
        <div class="title">Positions</div>
        <div class="subtitle">Every position before and after the scenario</div>
        """
    )

    if stress_trigger:
        max_pct = max(float(positions["loss_percent"].max()), 0.01)
        body = ""
        for _, p in positions.iterrows():
            w = max(p["loss_percent"] / max_pct * 70, 0)
            change = p["value_change"]
            body += (
                f'<tr><td>{esc(p["asset_id"])}</td><td>{esc(p["asset_type"])}</td><td>{esc(p.get("sector", ""))}</td>'
                f'<td>{p["market_value"]:,.0f}</td><td>{p["stressed_value"]:,.0f}</td>'
                f'<td class="t-bad">{change:,.0f}</td><td>{p["loss"]:,.0f}</td>'
                f'<td><div class="lbar"><i style="width:{w:.0f}px"></i>{p["loss_percent"]:.2f}%</div></td></tr>'
            )
        block(
            '<div class="card"><div class="card-head"><h3 class="card-title">Position-Level Stress Impact</h3>'
            f'<span class="chip">{len(positions)} positions</span></div>'
            '<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Asset</th><th>Type</th><th>Sector</th>'
            "<th>Before</th><th>After</th><th>Change</th><th>Loss</th><th>Loss %</th></tr></thead>"
            f"<tbody>{body}</tbody></table></div></div>"
        )
    else:
        block(
            '<div class="note"><b>No position data to show.</b><br>'
            "Positions appear once an event crosses the stress threshold.</div>"
        )

with tab_method:

    block(
        """
        <div class="title">Methodology and Scope</div>
        <div class="subtitle">How a news item becomes a portfolio stress result</div>
        <div class="row r-three">
            <div class="card">
                <h3 class="card-title" style="margin-bottom:8px">Risk engine</h3>
                <ul class="plain-list">
                    <li>FinBERT financial sentiment analysis</li>
                    <li>Hybrid rule-based and zero-shot event classification</li>
                    <li>Transparent 1 to 10 impact scoring</li>
                    <li>Configurable stress trigger</li>
                </ul>
            </div>
            <div class="card">
                <h3 class="card-title" style="margin-bottom:8px">Stress testing</h3>
                <ul class="plain-list">
                    <li>Synthetic wholesale banking portfolio</li>
                    <li>Loans, bonds, equities and derivatives</li>
                    <li>Scenario-based sensitivity shocks</li>
                    <li>Strategic event-driven stress analysis</li>
                </ul>
            </div>
            <div class="card">
                <h3 class="card-title" style="margin-bottom:12px">Base impact by event class</h3>
                <div class="kv"><span>Credit Event</span><span>8.0</span></div>
                <div class="kv"><span>Geopolitical</span><span>7.0</span></div>
                <div class="kv"><span>Macroeconomic, Regulatory</span><span>6.0</span></div>
                <div class="kv"><span>Merger and Acquisition, Earnings</span><span>5.0</span></div>
                <div class="kv"><span>Product Launch</span><span>3.0</span></div>
            </div>
        </div>
        """
    )

block(
    """
    <div class="footer">
        RiskPulse is a reproducible prototype using public historical data
        and a synthetic portfolio. Stress results are scenario-based
        estimates and are not regulatory capital or bank-grade valuation
        outputs.
    </div>
    """
)