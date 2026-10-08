import html
import math
import sys
import base64
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PATHS / CONFIG
# ============================================================

CURRENT_DIR = Path(__file__).resolve().parent

if (CURRENT_DIR / "data").exists():
    PROJECT_ROOT = CURRENT_DIR
else:
    PROJECT_ROOT = CURRENT_DIR.parent

DATA_PATH = PROJECT_ROOT / "data" / "integrated_risk_results.csv"
PORTFOLIO_PATH = PROJECT_ROOT / "data" / "portfolio.csv"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STRESS_THRESHOLD = 7

PALETTE = [
    "#b8f53c",
    "#6fae1d",
    "#3f6b14",
    "#e4f5c8",
    "#8b9399",
    "#566127",
]


# ============================================================
# STREAMLIT CONFIG
# ============================================================

LOGO_PATH = PROJECT_ROOT / "src" / "logo.png"

st.set_page_config(
    page_title="RiskPulse | Event-Driven Stress Testing",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM CSS
# ============================================================

CSS = """
<style>

@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

:root {
    --bg: #0b0d0e;
    --card: #14171a;
    --card2: #1a1e21;
    --card3: #101315;

    --line: #2a3035;
    --line-soft: #202529;

    --ink: #f2f4f3;
    --muted: #8b9399;
    --muted2: #667078;

    --lime: #b8f53c;
    --lime-d: #1d2a14;
    --lime-dark: #3f6b14;

    --good: #b8f53c;
    --bad: #ff6b5e;
    --warn: #e6b04a;
}

/* ==========================================================
   GLOBAL
   ========================================================== */

html,
body,
.stApp {
    background: var(--bg) !important;
    color: var(--ink) !important;
}

.stApp,
.stMarkdown,
.stSelectbox,
.stTextInput,
button,
input,
textarea {
    font-family:
        'Plus Jakarta Sans',
        system-ui,
        -apple-system,
        'Segoe UI',
        sans-serif !important;
}

.block-container {
    max-width: 1400px;
    padding-top: 1.2rem;
    padding-bottom: 4rem;
}

#MainMenu,
footer,
[data-testid="stToolbar"] {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

svg text {
    font-family: inherit;
}

/* ==========================================================
   STREAMLIT SELECTBOX
   ========================================================== */

.stSelectbox label p {
    color: var(--muted) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}

[data-baseweb="select"] > div {
    background: var(--card) !important;
    border: 1px solid var(--line) !important;
    border-radius: 14px !important;
    color: var(--ink) !important;
    font-size: 14px !important;
}

[data-baseweb="select"] * {
    color: var(--ink) !important;
}

[data-baseweb="popover"] > div,
[data-baseweb="popover"] ul {
    background: var(--card) !important;
}

[data-baseweb="popover"] li {
    color: var(--ink) !important;
}

[data-baseweb="popover"] li:hover {
    background: var(--card2) !important;
}

/* ==========================================================
   TABS
   ========================================================== */

[data-baseweb="tab-list"] {
    background: #101315 !important;
    border: 1px solid var(--line) !important;
    border-radius: 999px !important;
    padding: 6px !important;
    gap: 5px !important;
    width: fit-content !important;
    margin: 8px auto 18px auto !important;
}

button[data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-radius: 999px !important;
    padding: 10px 26px !important;
    height: auto !important;
    transition: all 0.18s ease !important;
}

button[data-baseweb="tab"] p {
    color: #9aa3a9 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}

button[data-baseweb="tab"]:hover {
    background: #1d2a14 !important;
}

button[data-baseweb="tab"]:hover p {
    color: #d9f7a4 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: var(--lime) !important;
    box-shadow:
        0 0 0 1px rgba(184, 245, 60, 0.22),
        0 5px 18px rgba(184, 245, 60, 0.12) !important;
}

button[data-baseweb="tab"][aria-selected="true"] p {
    color: #0b0d0e !important;
    font-weight: 800 !important;
}

[data-baseweb="tab-highlight"],
[data-baseweb="tab-border"] {
    display: none !important;
}

/* ==========================================================
   HEADER
   ========================================================== */

.head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    padding: 4px 0 10px 0;
}

.brand {
    display: flex;
    align-items: center;
    gap: 14px;
}

.logo {
    width: 56px;
    height: 56px;
    border-radius: 16px;
    background: #121619;
    border: 1px solid var(--line);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

.logo-img {
    width: 48px;
    height: 48px;
    object-fit: contain;
    display: block;
}

.brand-name {
    color: var(--ink);
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -0.8px;
}

.brand-name span {
    color: var(--lime);
}

.brand-tagline {
    color: var(--muted);
    font-size: 12px;
    margin-top: 2px;
    letter-spacing: 0.2px;
}

.head-meta {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 10px 18px;
    font-size: 13px;
    font-weight: 500;
    color: #d8dddf;
    display: flex;
    align-items: center;
    gap: 9px;
}

.live {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--lime);
    box-shadow: 0 0 10px rgba(184, 245, 60, 0.55);
}

/* ==========================================================
   TITLES
   ========================================================== */

.title {
    color: var(--ink);
    font-size: 38px;
    font-weight: 600;
    letter-spacing: -0.8px;
    margin: 26px 0 4px 0;
}

.subtitle {
    color: var(--muted);
    font-size: 16px;
    margin-bottom: 22px;
}

/* ==========================================================
   LAYOUT
   ========================================================== */

.row {
    display: grid;
    gap: 16px;
    margin-top: 16px;
}

.r4 {
    grid-template-columns: repeat(4, 1fr);
}

.r-event {
    grid-template-columns: 1.5fr 1fr;
}

.r-charts {
    grid-template-columns: 1.3fr 1fr;
}

.r-bottom {
    grid-template-columns: 1fr 1.1fr 1.2fr;
}

.r-two {
    grid-template-columns: 1fr 1fr;
}

.r-three {
    grid-template-columns: repeat(3, 1fr);
}

/* ==========================================================
   CARDS
   ========================================================== */

.card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 22px;
    padding: 26px 28px;
    min-width: 0;
}

.card:hover {
    border-color: #353d42;
}

.card-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 18px;
}

.card-title {
    color: var(--ink);
    font-size: 21px;
    font-weight: 500;
    margin: 0;
}

.card-title-small {
    color: var(--ink);
    font-size: 17px;
    font-weight: 600;
}

/* ==========================================================
   CHIPS
   ========================================================== */

.chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 18px;
}

.chip {
    display: inline-flex;
    align-items: center;
    border: 1px solid var(--line);
    background: var(--card2);
    border-radius: 999px;
    padding: 7px 14px;
    font-size: 13px;
    color: #dfe3e4;
    white-space: nowrap;
}

.chip.lime {
    background: var(--lime);
    color: #0b0d0e;
    border-color: var(--lime);
    font-weight: 700;
}

/* ==========================================================
   KPI
   ========================================================== */

.kpi {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 22px;
    padding: 21px 24px 23px 24px;
}

.kpi-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #dce1e2;
    font-size: 14px;
    font-weight: 500;
}

.arrow {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: var(--card2);
    border: 1px solid var(--line);
    display: grid;
    place-items: center;
    color: #cfd5d7;
}

.kpi-val {
    color: var(--ink);
    font-size: 32px;
    font-weight: 600;
    letter-spacing: -0.8px;
    margin-top: 12px;
    font-variant-numeric: tabular-nums;
}

.kpi-sub {
    font-size: 13px;
    margin-top: 7px;
}

/* ==========================================================
   TEXT COLORS
   ========================================================== */

.t-good {
    color: var(--good) !important;
}

.t-bad {
    color: var(--bad) !important;
}

.t-warn {
    color: var(--warn) !important;
}

.t-mute {
    color: var(--muted) !important;
}

/* ==========================================================
   EVENT
   ========================================================== */

.ev-head {
    color: #f1f3f2;
    font-size: 25px;
    line-height: 1.4;
    font-weight: 500;
    letter-spacing: -0.3px;
    margin: 0;
}

.scale-head {
    color: var(--muted);
    font-size: 13.5px;
    line-height: 1.55;
    margin-bottom: 44px;
}

.scale-body {
    position: relative;
    margin: 0 8px;
}

.track {
    display: flex;
    height: 14px;
    border-radius: 999px;
    overflow: hidden;
    gap: 3px;
}

.track div {
    height: 100%;
}

.z1 {
    background: #2f4a1a;
}

.z2 {
    background: #6e9a1c;
}

.z3 {
    background: #d6a53a;
}

.z4 {
    background: #e0584a;
}

.thresh {
    position: absolute;
    top: -8px;
    height: 30px;
    border-left: 2px dashed #e9eee9;
}

.marker {
    position: absolute;
    top: -8px;
    height: 30px;
    width: 4px;
    background: #ffffff;
    border-radius: 2px;
    transform: translateX(-50%);
}

.marker span {
    position: absolute;
    bottom: 38px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--lime);
    color: #0b0d0e;
    font-size: 14px;
    font-weight: 800;
    padding: 3px 11px;
    border-radius: 999px;
    white-space: nowrap;
}

.zones {
    display: flex;
    margin-top: 14px;
    font-size: 12.5px;
    color: var(--muted);
}

/* ==========================================================
   GOALS
   ========================================================== */

.goal {
    padding: 8px 0 18px 0;
}

.goal + .goal {
    border-top: 1px solid var(--line-soft);
    padding-top: 18px;
}

.goal-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
}

.goal-top > div {
    flex: 1;
}

.goal-title {
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 4px;
}

.goal-val {
    color: var(--ink);
    font-size: 25px;
    font-weight: 600;
}

.goal-val small {
    color: var(--muted);
    font-size: 12px;
    font-weight: 500;
}

.goal-pct {
    color: var(--muted);
    font-size: 13px;
}

.ico {
    width: 38px;
    height: 38px;
    display: grid;
    place-items: center;
    color: var(--lime);
    background: var(--lime-d);
    border: 1px solid #2c421a;
    border-radius: 11px;
}

.ico.sm {
    width: 30px;
    height: 30px;
    border-radius: 9px;
}

.pbar {
    width: 100%;
    height: 7px;
    margin: 12px 0 8px 0;
    background: #252a2e;
    border-radius: 999px;
    overflow: hidden;
}

.pbar > div {
    height: 100%;
    background: var(--lime);
    border-radius: inherit;
}

.pbar.red > div {
    background: var(--bad);
}

.goal-foot {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    color: var(--muted);
    font-size: 12px;
}

/* ==========================================================
   LISTS
   ========================================================== */

.li {
    display: grid;
    grid-template-columns: 36px 1fr auto auto;
    align-items: center;
    gap: 12px;
    padding: 13px 0;
    border-top: 1px solid var(--line-soft);
}

.li:first-child {
    border-top: none;
}

.ini {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    display: grid;
    place-items: center;
    background: var(--lime-d);
    color: var(--lime);
    font-size: 13px;
    font-weight: 700;
}

.nm {
    color: var(--ink);
    font-size: 14px;
    font-weight: 600;
}

.sb {
    color: var(--muted);
    font-size: 11.5px;
    margin-top: 3px;
}

.pc {
    color: var(--muted);
    font-size: 13px;
}

.am {
    font-size: 13px;
    font-weight: 600;
}

/* ==========================================================
   MINI CARDS
   ========================================================== */

.minis {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}

.mini {
    background: var(--card2);
    border: 1px solid var(--line);
    border-radius: 17px;
    padding: 17px;
}

.mini-top {
    display: flex;
    align-items: center;
    gap: 9px;
    color: var(--muted);
    font-size: 12px;
}

.mini-val {
    color: var(--ink);
    font-size: 22px;
    font-weight: 600;
    margin: 12px 0 7px 0;
}

.pill {
    display: inline-block;
    color: #cdd4d7;
    background: #252b2f;
    border-radius: 999px;
    padding: 4px 9px;
    font-size: 10.5px;
}

/* ==========================================================
   CHARTS
   ========================================================== */

.legend-row {
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--muted);
    font-size: 12px;
    margin-bottom: 10px;
}

.donut-wrap {
    display: grid;
    grid-template-columns: 0.9fr 1.1fr;
    align-items: center;
    gap: 14px;
}

.leg {
    display: grid;
    grid-template-columns: 10px 1fr auto auto;
    align-items: center;
    gap: 7px;
    padding: 7px 0;
    color: #d9dddf;
    font-size: 12px;
}

.dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

.leg .v {
    color: var(--ink);
    font-weight: 600;
}

.leg .s {
    color: var(--muted);
}

/* ==========================================================
   TABLE
   ========================================================== */

.tbl-wrap {
    overflow-x: auto;
}

.tbl {
    width: 100%;
    border-collapse: collapse;
    font-size: 12.5px;
}

.tbl th {
    color: var(--muted);
    text-align: left;
    font-size: 11px;
    font-weight: 600;
    padding: 12px 10px;
    border-bottom: 1px solid var(--line);
    white-space: nowrap;
}

.tbl td {
    color: #dce1e2;
    padding: 13px 10px;
    border-bottom: 1px solid var(--line-soft);
    white-space: nowrap;
}

.tbl tr:last-child td {
    border-bottom: none;
}

.lbar {
    display: flex;
    align-items: center;
    gap: 7px;
    color: var(--muted);
}

.lbar i {
    display: inline-block;
    height: 6px;
    background: var(--bad);
    border-radius: 999px;
    min-width: 3px;
}

/* ==========================================================
   METHODOLOGY
   ========================================================== */

.plain-list {
    padding-left: 19px;
    margin: 12px 0 0 0;
}

.plain-list li {
    color: #cbd1d3;
    font-size: 13px;
    line-height: 1.7;
    margin-bottom: 5px;
}

.kv {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid var(--line-soft);
    padding: 10px 0;
    color: var(--muted);
    font-size: 12.5px;
}

.kv:last-child {
    border-bottom: none;
}

.kv span:last-child {
    color: var(--ink);
    font-weight: 600;
}

/* ==========================================================
   NOTE / EMPTY STATE
   ========================================================== */

.note {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 25px 28px;
    color: var(--muted);
    font-size: 14px;
    line-height: 1.7;
}

.note b {
    color: var(--ink);
}

/* ==========================================================
   FOOTER
   ========================================================== */

.footer {
    margin-top: 42px;
    padding-top: 20px;
    border-top: 1px solid var(--line-soft);
    color: var(--muted);
    font-size: 12px;
    line-height: 1.7;
    max-width: 950px;
}

/* ==========================================================
   RESPONSIVE
   ========================================================== */

@media (max-width: 1100px) {

    .r4 {
        grid-template-columns: repeat(2, 1fr);
    }

    .r-event,
    .r-charts,
    .r-bottom,
    .r-two,
    .r-three {
        grid-template-columns: 1fr;
    }

    .minis {
        grid-template-columns: 1fr 1fr;
    }
}

@media (max-width: 700px) {

    .head {
        align-items: flex-start;
        flex-direction: column;
    }

    .head-meta {
        width: fit-content;
    }

    .title {
        font-size: 30px;
    }

    .r4 {
        grid-template-columns: 1fr;
    }

    .minis {
        grid-template-columns: 1fr;
    }

    [data-baseweb="tab-list"] {
        width: 100% !important;
        overflow-x: auto !important;
        justify-content: flex-start !important;
    }

    button[data-baseweb="tab"] {
        padding: 9px 15px !important;
    }
}

</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ============================================================
# LOGO
# ============================================================

if LOGO_PATH.exists():
    LOGO_DATA = base64.b64encode(LOGO_PATH.read_bytes()).decode("utf-8")
    LOGO_SRC = f"data:image/png;base64,{LOGO_DATA}"
else:
    LOGO_SRC = ""


# ============================================================
# HELPERS
# ============================================================

def esc(value):
    return html.escape(str(value))


def block(markup):
    """
    Render HTML safely.
    Joining lines prevents Streamlit Markdown from interpreting
    indentation as a code block.
    """
    cleaned = " ".join(
        line.strip()
        for line in markup.splitlines()
        if line.strip()
    )
    st.markdown(cleaned, unsafe_allow_html=True)


def to_bool(value):
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes")
    return bool(value)


def compact(v):
    a = abs(float(v))

    if a >= 1e9:
        s = f"{v / 1e9:.1f}B"
    elif a >= 1e6:
        s = f"{v / 1e6:.1f}M"
    elif a >= 1e3:
        s = f"{v / 1e3:.0f}K"
    else:
        s = f"{v:.0f}"

    return (
        s.replace(".0B", "B")
        .replace(".0M", "M")
    )


# ============================================================
# ICONS
# ============================================================

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
    path = ICONS[name]

    return (
        f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" '
        f'fill="none" stroke="currentColor" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="{path}"/>'
        f'</svg>'
    )


ARROW = (
    '<svg viewBox="0 0 24 24" width="18" height="18" '
    'fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M7 17 17 7M8 7h9v9"/>'
    '</svg>'
)


# ============================================================
# CHART HELPERS
# ============================================================

def nice_scale(peak, divisions=4):

    peak = float(peak)

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


def bars_svg(
    uid,
    labels,
    series,
    colors=None,
    avg=None,
    W=760,
    H=310,
):
    """
    Custom SVG bar chart.
    One series = gradient bars.
    Multiple series = grouped bars.
    """

    left, right, top, bottom = 58, 8, 30, 46

    pw = W - left - right
    ph = H - top - bottom

    peak = max(
        [max(s) for s in series if s] + [0]
    )

    step, ymax = nice_scale(peak)

    n = len(series)

    output = [
        f'<svg viewBox="0 0 {W} {H}" width="100%" role="img">',
        (
            f'<defs>'
            f'<linearGradient id="hi{uid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="#b8f53c" stop-opacity="0.95"/>'
            f'<stop offset="1" stop-color="#4c7d18" stop-opacity="0.25"/>'
            f'</linearGradient>'
        ),
        (
            f'<linearGradient id="lo{uid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="#6fae1d" stop-opacity="0.8"/>'
            f'<stop offset="1" stop-color="#2f4a12" stop-opacity="0.15"/>'
            f'</linearGradient>'
            f'</defs>'
        ),
    ]

    grid_count = int(round(ymax / step))

    for k in range(grid_count + 1):

        val = k * step

        y = top + ph - ph * val / ymax

        output.append(
            f'<line x1="{left}" x2="{W - right}" '
            f'y1="{y:.1f}" y2="{y:.1f}" '
            f'stroke="#23282c" stroke-width="1"/>'
        )

        output.append(
            f'<text x="{left - 12}" y="{y + 4.5:.1f}" '
            f'text-anchor="end" font-size="13" fill="#8b9399">'
            f'{compact(val)}</text>'
        )

    slot = pw / max(len(labels), 1)

    group_w = slot * 0.64

    gap = 5 if n > 1 else 0

    bw = (group_w - gap * (n - 1)) / n

    best = (
        series[0].index(max(series[0]))
        if n == 1 and series[0]
        else -1
    )

    for i, lab in enumerate(labels):

        x0 = (
            left
            + i * slot
            + (slot - group_w) / 2
        )

        for j, values in enumerate(series):

            h = max(
                ph * values[i] / ymax,
                1
            )

            x = x0 + j * (bw + gap)

            y = top + ph - h

            if n == 1:

                fill = (
                    f"url(#hi{uid})"
                    if i == best
                    else f"url(#lo{uid})"
                )

            else:

                fill = (
                    colors[j]
                    if colors and j < len(colors)
                    else "#b8f53c"
                )

            output.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" '
                f'width="{bw:.1f}" height="{h:.1f}" '
                f'rx="6" fill="{fill}"/>'
            )

        short = (
            lab
            if len(lab) <= 10
            else lab[:9] + "..."
        )

        output.append(
            f'<text x="{left + i * slot + slot / 2:.1f}" '
            f'y="{H - 16}" text-anchor="middle" '
            f'font-size="13" fill="#8b9399">'
            f'{esc(short)}</text>'
        )

    if avg is not None and ymax > 0:

        y = (
            top
            + ph
            - ph * avg / ymax
        )

        output.append(
            f'<line x1="{left}" x2="{W - right}" '
            f'y1="{y:.1f}" y2="{y:.1f}" '
            f'stroke="#b8f53c" stroke-width="1.6" '
            f'stroke-dasharray="6 6"/>'
        )

        tag = f"Avg {compact(avg)}"

        tw = 12 + 8.2 * len(tag)

        output.append(
            f'<rect x="{left + 6}" y="{y - 26:.1f}" '
            f'width="{tw:.0f}" height="22" rx="6" '
            f'fill="#2a3a18"/>'
        )

        output.append(
            f'<text x="{left + 6 + tw / 2:.0f}" '
            f'y="{y - 10.5:.1f}" '
            f'text-anchor="middle" font-size="13" '
            f'fill="#b8f53c" font-weight="600">'
            f'{tag}</text>'
        )

    output.append("</svg>")

    return "".join(output)


def donut_svg(values, top_label, main_label):

    total = sum(values)

    r = 78
    cx = 110

    circumference = 2 * math.pi * r

    output = [
        '<svg viewBox="0 0 220 220" width="100%" role="img">'
    ]

    offset = 0.0

    for i, value in enumerate(values):

        frac = (
            value / total
            if total > 0
            else 0
        )

        segment = max(
            frac * circumference - 4,
            0
        )

        output.append(
            f'<circle cx="{cx}" cy="{cx}" r="{r}" '
            f'fill="none" '
            f'stroke="{PALETTE[i % len(PALETTE)]}" '
            f'stroke-width="34" '
            f'stroke-dasharray="{segment:.2f} '
            f'{circumference - segment:.2f}" '
            f'stroke-dashoffset="{-(offset + 2):.2f}" '
            f'transform="rotate(-90 {cx} {cx})"/>'
        )

        offset += frac * circumference

    main = (
        main_label
        if len(main_label) <= 13
        else main_label[:12] + "..."
    )

    output.append(
        f'<text x="{cx}" y="{cx - 8}" '
        f'text-anchor="middle" font-size="12.5" '
        f'fill="#8b9399">{esc(top_label)}</text>'
    )

    output.append(
        f'<text x="{cx}" y="{cx + 17}" '
        f'text-anchor="middle" font-size="19" '
        f'font-weight="600" fill="#f2f4f3">'
        f'{esc(main)}</text>'
    )

    output.append("</svg>")

    return "".join(output)


def donut_card(
    title,
    chip,
    frame,
    label_col,
    value_col,
    top_label,
):

    values = [
        float(v)
        for v in frame[value_col]
    ]

    names = [
        str(n)
        for n in frame[label_col]
    ]

    total = sum(values)

    legend = ""

    for i, (name, value) in enumerate(
        zip(names, values)
    ):

        share = (
            value / total * 100
            if total > 0
            else 0
        )

        legend += (
            f'<div class="leg">'
            f'<span class="dot" '
            f'style="background:{PALETTE[i % len(PALETTE)]}"></span>'
            f'<span>{esc(name)}</span>'
            f'<span class="v">{value:,.0f}</span>'
            f'<span class="s">({share:.1f}%)</span>'
            f'</div>'
        )

    svg = donut_svg(
        values,
        top_label,
        names[0] if names else "n/a"
    )

    return (
        f'<div class="card">'
        f'<div class="card-head">'
        f'<h3 class="card-title">{esc(title)}</h3>'
        f'<span class="chip">{esc(chip)}</span>'
        f'</div>'
        f'<div class="donut-wrap">'
        f'<div>{svg}</div>'
        f'<div>{legend}</div>'
        f'</div>'
        f'</div>'
    )


# ============================================================
# COMPONENT HELPERS
# ============================================================

def kpi(label, value, sub, tone):

    return (
        f'<div class="kpi">'
        f'<div class="kpi-top">'
        f'<span>{esc(label)}</span>'
        f'<span class="arrow">{ARROW}</span>'
        f'</div>'
        f'<div class="kpi-val">{value}</div>'
        f'<div class="kpi-sub t-{tone}">{sub}</div>'
        f'</div>'
    )


def goal(
    icon_name,
    title,
    value_txt,
    unit,
    pct,
    foot_left,
    status,
    tone,
    bar_class="",
):

    pct = max(
        0,
        min(float(pct), 100)
    )

    return (
        f'<div class="goal">'
        f'<div class="goal-top">'
        f'<span class="ico">{icon(icon_name)}</span>'
        f'<div>'
        f'<div class="goal-title">{esc(title)}</div>'
        f'<div class="goal-val">{value_txt} '
        f'<small>{esc(unit)}</small></div>'
        f'</div>'
        f'<span class="goal-pct">{pct:.0f}%</span>'
        f'</div>'
        f'<div class="pbar {bar_class}">'
        f'<div style="width:{pct:.1f}%"></div>'
        f'</div>'
        f'<div class="goal-foot">'
        f'<span>{foot_left}</span>'
        f'<span class="t-{tone}">{status}</span>'
        f'</div>'
        f'</div>'
    )


def mini(icon_name, label, value, pill):

    return (
        f'<div class="mini">'
        f'<div class="mini-top">'
        f'<span class="ico sm">{icon(icon_name, 18)}</span>'
        f'{esc(label)}'
        f'</div>'
        f'<div class="mini-val">{value}</div>'
        f'<span class="pill">{pill}</span>'
        f'</div>'
    )


# ============================================================
# LOAD RESULTS
# ============================================================

@st.cache_data
def load_results():

    if not DATA_PATH.exists():
        return None

    return pd.read_csv(DATA_PATH)


df = load_results()


if df is None:

    st.error(
        "Risk results file was not found at:\n\n"
        f"{DATA_PATH}\n\n"
        "Run:\n\n"
        "python src/integrated_risk_pipeline.py"
    )

    st.stop()


if df.empty:

    st.error(
        "The integrated risk results file is empty."
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

block(
    f"""
    <div class="head">

        <div class="brand">

            <div class="logo">
                <img
                    class="logo-img"
                    src="{LOGO_SRC}"
                    alt=""
                >
            </div>

            <div>
                <div class="brand-name">
                    Risk<span>Pulse</span>
                </div>

                <div class="brand-tagline">
                    AI/NLP Financial Risk Intelligence
                </div>
            </div>

        </div>

        <div class="head-meta">
            <span class="live"></span>
            <span>Results loaded</span>
            <span>{len(df)} event(s)</span>
        </div>

    </div>
    """
)


# ============================================================
# EVENT SELECTOR
# ============================================================

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


# ============================================================
# RISK SIGNAL
# ============================================================

headline = str(
    row.get("text", "N/A")
)

entity = str(
    row.get("entity", "N/A")
)

source = str(
    row.get("source", "N/A")
)

date = str(
    row.get("date", "N/A")
)

sentiment_score = float(
    row.get("sentiment_score", 0)
)

sentiment_label = str(
    row.get("sentiment_label", "N/A")
)

event_class = str(
    row.get("event_class", "Unclassified")
)

confidence = float(
    row.get("event_confidence", 0)
)

method = str(
    row.get("classification_method", "N/A")
)

impact_score = float(
    row.get("impact_score", 0)
)

stress_trigger = to_bool(
    row.get("stress_trigger", False)
)


# ============================================================
# RISK LEVEL
# ============================================================

if impact_score >= 9:

    risk_level = "Critical"
    level_tone = "bad"

elif impact_score >= 7:

    risk_level = "High"
    level_tone = "bad"

elif impact_score >= 4:

    risk_level = "Moderate"
    level_tone = "warn"

else:

    risk_level = "Low"
    level_tone = "good"


sent_tone = (
    "bad"
    if sentiment_score <= -0.05
    else (
        "good"
        if sentiment_score >= 0.05
        else "mute"
    )
)


# ============================================================
# PORTFOLIO STRESS
# ============================================================

positions = None
summary = None
scenario = None

if stress_trigger:

    try:

        from src.portfolio_stress import (
            load_portfolio,
            stress_test_portfolio,
            get_stress_scenario,
        )

        portfolio = load_portfolio()

        positions, summary = stress_test_portfolio(
            portfolio,
            event_class
        )

        scenario = get_stress_scenario(
            event_class
        )

        portfolio_before = summary[
            "portfolio_value_before"
        ]

        portfolio_after = summary[
            "portfolio_value_after"
        ]

        portfolio_loss = summary[
            "portfolio_loss"
        ]

        loss_percent = summary[
            "portfolio_loss_percent"
        ]

        positions = positions.copy()

        if "sector" in positions.columns:

            positions["sector"] = (
                positions["sector"]
                .fillna("Unassigned")
            )

    except Exception as e:

        st.error(
            f"Portfolio stress calculation failed: {e}"
        )

        st.stop()


# ============================================================
# TABS
# ============================================================

(
    tab_overview,
    tab_stress,
    tab_positions,
    tab_method,
) = st.tabs(
    [
        "Overview",
        "Stress Test",
        "Positions",
        "Methodology",
    ]
)


# ============================================================
# OVERVIEW
# ============================================================

with tab_overview:

    block(
        f"""
        <div class="title">
            Risk Overview
        </div>

        <div class="subtitle">
            Event-driven portfolio stress test for {esc(entity)}
        </div>
        """
    )


    if stress_trigger:

        k3 = kpi(
            "Stress Loss",
            f"-{portfolio_loss:,.0f}",
            f"-{loss_percent:.2f}% of portfolio value",
            "bad",
        )

    else:

        k3 = kpi(
            "Stress Loss",
            "None",
            "Scenario not triggered",
            "good",
        )


    block(
        '<div class="row r4">'
        + kpi(
            "Impact Score",
            f"{impact_score:.1f} / 10",
            f"{risk_level} severity",
            level_tone,
        )
        + kpi(
            "Sentiment Score",
            f"{sentiment_score:+.3f}",
            esc(sentiment_label.title()),
            sent_tone,
        )
        + k3
        + kpi(
            "Event Class",
            esc(event_class),
            f"Confidence {confidence:.2f}",
            "good",
        )
        + "</div>"
    )


    # --------------------------------------------------------
    # EVENT + IMPACT SCALE
    # --------------------------------------------------------

    marker_pct = max(
        0.0,
        min(
            impact_score / 10 * 100,
            100.0
        ),
    )

    thresh_pct = (
        STRESS_THRESHOLD / 10 * 100
    )


    block(
        f"""
        <div class="row r-event">

            <div class="card">

                <div class="card-head">
                    <h3 class="card-title">
                        Detected Event
                    </h3>

                    <span class="chip lime">
                        {esc(entity)}
                    </span>
                </div>

                <div class="chips">

                    <span class="chip">
                        {esc(event_class)}
                    </span>

                    <span class="chip">
                        {esc(date[:10])}
                    </span>

                    <span class="chip">
                        {esc(source[:40])}
                    </span>

                </div>

                <p class="ev-head">
                    {esc(headline)}
                </p>

            </div>


            <div class="card">

                <div class="card-head">

                    <h3 class="card-title">
                        Impact Scale
                    </h3>

                    <span class="chip">
                        Stress trigger &gt; {STRESS_THRESHOLD}
                    </span>

                </div>

                <div class="scale-head">
                    1–10 severity scale for classified events;
                    0 for unclassified.
                    Impact &gt; 7 triggers the stress scenario.
                </div>

                <div class="scale-body">

                    <div class="track">

                        <div
                            class="z1"
                            style="width:40%"
                        ></div>

                        <div
                            class="z2"
                            style="width:30%"
                        ></div>

                        <div
                            class="z3"
                            style="width:20%"
                        ></div>

                        <div
                            class="z4"
                            style="width:10%"
                        ></div>

                    </div>

                    <div
                        class="thresh"
                        style="left:{thresh_pct}%"
                    ></div>

                    <div
                        class="marker"
                        style="left:{marker_pct:.1f}%"
                    >
                        <span>
                            {impact_score:.1f}
                        </span>
                    </div>

                    <div class="zones">

                        <div style="width:40%">
                            Low
                        </div>

                        <div style="width:30%">
                            Moderate
                        </div>

                        <div style="width:20%">
                            High
                        </div>

                        <div style="width:10%">
                            Critical
                        </div>

                    </div>

                </div>

            </div>

        </div>
        """
    )


    # --------------------------------------------------------
    # STRESS CHARTS
    # --------------------------------------------------------

    if stress_trigger:

        by_pos = positions.sort_values(
            "loss",
            ascending=False
        )

        pos_labels = [
            str(a)
            for a in by_pos["asset_id"]
        ]

        pos_loss = [
            float(v)
            for v in by_pos["loss"]
        ]

        avg_loss = (
            sum(pos_loss) / len(pos_loss)
            if pos_loss
            else 0
        )


        bar_card = (
            '<div class="card">'
            '<div class="card-head">'
            '<h3 class="card-title">'
            'Stress Loss by Position'
            '</h3>'
            '<span class="chip">'
            'Synthetic units'
            '</span>'
            '</div>'

            '<div class="legend-row">'
            '<span class="chip lime">'
            'Loss'
            '</span>'
            '<span>'
            'Dashed line shows the average loss per position'
            '</span>'
            '</div>'

            + bars_svg(
                "pos",
                pos_labels,
                [pos_loss],
                avg=avg_loss,
            )

            + '</div>'
        )


        by_asset = (
            positions
            .groupby("asset_type")["loss"]
            .sum()
            .sort_values(
                ascending=False
            )
            .reset_index()
        )


        donut = donut_card(
            "Loss by Asset Class",
            "All positions",
            by_asset,
            "asset_type",
            "loss",
            "Largest loss",
        )


        block(
            f'<div class="row r-charts">'
            f'{bar_card}'
            f'{donut}'
            f'</div>'
        )


    # --------------------------------------------------------
    # GOALS
    # --------------------------------------------------------

    goals = (

        goal(
            "bolt",
            "Impact score",
            f"{impact_score:.1f}",
            "/ 10",
            impact_score / 10 * 100,
            f"Stress trigger: Impact > {STRESS_THRESHOLD}",
            (
                "Above threshold"
                if stress_trigger
                else "Below threshold"
            ),
            (
                "bad"
                if stress_trigger
                else "good"
            ),
            (
                "red"
                if stress_trigger
                else ""
            ),
        )

        +

        goal(
            "shield",
            "Classifier confidence",
            f"{confidence:.2f}",
            "/ 1.00",
            confidence * 100,
            f"Method: {esc(method)}",
            (
                "High confidence"
                if confidence >= 0.8
                else (
                    "Moderate"
                    if confidence >= 0.5
                    else "Low confidence"
                )
            ),
            (
                "good"
                if confidence >= 0.8
                else "warn"
            ),
        )
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


    goals_card = (
        f'<div class="card">'
        f'{goals}'
        f'</div>'
    )


    # --------------------------------------------------------
    # LARGEST LOSSES
    # --------------------------------------------------------

    if stress_trigger:

        top5 = (
            positions
            .sort_values(
                "loss",
                ascending=False
            )
            .head(5)
        )

        items = ""

        for _, p in top5.iterrows():

            items += (
                f'<div class="li">'

                f'<div class="ini">'
                f'{esc(str(p["asset_type"])[:1].upper())}'
                f'</div>'

                f'<div>'
                f'<div class="nm">'
                f'{esc(p["asset_id"])}'
                f'</div>'

                f'<div class="sb">'
                f'{esc(p["asset_type"])}, '
                f'{esc(p.get("sector", ""))}'
                f'</div>'
                f'</div>'

                f'<div class="pc">'
                f'{p["loss_percent"]:.2f}%'
                f'</div>'

                f'<div class="am t-bad">'
                f'-{p["loss"]:,.0f}'
                f'</div>'

                f'</div>'
            )


        list_card = (
            '<div class="card">'
            '<div class="card-head">'
            '<h3 class="card-title">'
            'Largest Position Losses'
            '</h3>'
            '<span class="chip">'
            'Top 5'
            '</span>'
            '</div>'
            + items
            + '</div>'
        )


        minis = (
            '<div class="minis">'

            + mini(
                "wallet",
                "Value before",
                f"{portfolio_before:,.0f}",
                "Synthetic units",
            )

            + mini(
                "down",
                "Value after",
                f"{portfolio_after:,.0f}",
                f"-{loss_percent:.2f}%",
            )

            + mini(
                "trend",
                "Equity shock",
                f"{scenario['equity_shock']:+.0%}",
                esc(event_class),
            )

            + mini(
                "pulse",
                "Rate shock",
                f"{scenario['rate_shock']:+.0%}",
                f"Credit {scenario['credit_shock']:+.0%}",
            )

            + '</div>'
        )


        block(
            f'<div class="row r-bottom">'
            f'{goals_card}'
            f'{list_card}'
            f'{minis}'
            f'</div>'
        )


    else:

        no_stress = (
            '<div class="note">'
            '<b>No stress scenario triggered.</b>'
            '<br>'
            f'Impact score {impact_score:.1f} does not exceed '
            f'the threshold of {STRESS_THRESHOLD}, '
            'so the portfolio was not re-valued for this event.'
            '</div>'
        )

        block(
            f'<div class="row r-two">'
            f'{goals_card}'
            f'{no_stress}'
            f'</div>'
        )


# ============================================================
# STRESS TEST TAB
# ============================================================

with tab_stress:

    block(
        """
        <div class="title">
            Stress Test
        </div>

        <div class="subtitle">
            Scenario shocks mapped from the event class
            and applied to every portfolio position
        </div>
        """
    )


    if stress_trigger:

        block(
            '<div class="row r4">'

            + kpi(
                "Scenario",
                esc(event_class),
                f"Impact {impact_score:.1f}, "
                f"stress trigger > {STRESS_THRESHOLD}",
                "bad",
            )

            + kpi(
                "Equity Shock",
                f"{scenario['equity_shock']:+.0%}",
                "Applied to equity sensitivity",
                "mute",
            )

            + kpi(
                "Rate Shock",
                f"{scenario['rate_shock']:+.0%}",
                "Applied to rate sensitivity",
                "mute",
            )

            + kpi(
                "Credit Shock",
                f"{scenario['credit_shock']:+.0%}",
                "Applied to credit sensitivity",
                "mute",
            )

            + '</div>'
        )


        grouped = (
            positions
            .groupby("asset_type")[
                [
                    "market_value",
                    "stressed_value",
                ]
            ]
            .sum()
            .reset_index()
        )


        grouped_card = (
            '<div class="card">'

            '<div class="card-head">'
            '<h3 class="card-title">'
            'Value Before and After'
            '</h3>'
            '<span class="chip">'
            'By asset class'
            '</span>'
            '</div>'

            '<div class="legend-row">'
            '<span class="chip" '
            'style="background:#4d6b2a;'
            'border-color:#4d6b2a">'
            'Before'
            '</span>'

            '<span class="chip lime">'
            'After'
            '</span>'
            '</div>'

            +

            bars_svg(
                "grp",
                [
                    str(a)
                    for a in grouped["asset_type"]
                ],
                [
                    [
                        float(v)
                        for v in grouped["market_value"]
                    ],
                    [
                        float(v)
                        for v in grouped["stressed_value"]
                    ],
                ],
                colors=[
                    "#4d6b2a",
                    "#b8f53c",
                ],
            )

            +

            '</div>'
        )


        if "sector" in positions.columns:

            by_sector = (
                positions
                .groupby("sector")["loss"]
                .sum()
                .sort_values(
                    ascending=False
                )
                .reset_index()
            )

            sector_card = donut_card(
                "Loss by Sector",
                "All positions",
                by_sector,
                "sector",
                "loss",
                "Largest loss",
            )

        else:

            sector_card = ""


        block(
            f'<div class="row r-charts">'
            f'{grouped_card}'
            f'{sector_card}'
            f'</div>'
        )


        block(
            '<div class="row r-three">'

            f'<div class="card">'
            f'<div class="card-title" '
            f'style="margin-bottom:10px">'
            f'Portfolio before'
            f'</div>'
            f'<div class="kpi-val">'
            f'{portfolio_before:,.0f}'
            f'</div>'
            f'<div class="kpi-sub t-mute">'
            f'Synthetic portfolio units'
            f'</div>'
            f'</div>'

            f'<div class="card">'
            f'<div class="card-title" '
            f'style="margin-bottom:10px">'
            f'Portfolio after'
            f'</div>'
            f'<div class="kpi-val">'
            f'{portfolio_after:,.0f}'
            f'</div>'
            f'<div class="kpi-sub t-mute">'
            f'After scenario shocks'
            f'</div>'
            f'</div>'

            f'<div class="card">'
            f'<div class="card-title" '
            f'style="margin-bottom:10px">'
            f'Stress loss'
            f'</div>'
            f'<div class="kpi-val t-bad">'
            f'-{portfolio_loss:,.0f}'
            f'</div>'
            f'<div class="kpi-sub t-bad">'
            f'-{loss_percent:.2f}% of portfolio'
            f'</div>'
            f'</div>'

            '</div>'
        )


    else:

        block(
            f'<div class="note">'
            f'<b>No stress scenario triggered.</b>'
            f'<br>'
            f'Impact score {impact_score:.1f} does not exceed '
            f'the threshold of {STRESS_THRESHOLD}. '
            f'Select an event with a higher impact score '
            f'to see portfolio stress results.'
            f'</div>'
        )


# ============================================================
# POSITIONS TAB
# ============================================================

with tab_positions:

    block(
        """
        <div class="title">
            Positions
        </div>

        <div class="subtitle">
            Every portfolio position before and after
            the event-driven scenario
        </div>
        """
    )


    if stress_trigger:

        max_pct = max(
            float(
                positions["loss_percent"].max()
            ),
            0.01,
        )

        body = ""

        for _, p in positions.iterrows():

            width = max(
                p["loss_percent"]
                / max_pct
                * 70,
                0,
            )

            change = p["value_change"]

            body += (
                f'<tr>'

                f'<td>{esc(p["asset_id"])}</td>'

                f'<td>{esc(p["asset_type"])}</td>'

                f'<td>{esc(p.get("sector", ""))}</td>'

                f'<td>{p["market_value"]:,.0f}</td>'

                f'<td>{p["stressed_value"]:,.0f}</td>'

                f'<td class="t-bad">'
                f'{change:,.0f}'
                f'</td>'

                f'<td>{p["loss"]:,.0f}</td>'

                f'<td>'
                f'<div class="lbar">'
                f'<i style="width:{width:.0f}px"></i>'
                f'{p["loss_percent"]:.2f}%'
                f'</div>'
                f'</td>'

                f'</tr>'
            )


        block(
            '<div class="card">'

            '<div class="card-head">'
            '<h3 class="card-title">'
            'Position-Level Stress Impact'
            '</h3>'

            f'<span class="chip">'
            f'{len(positions)} positions'
            f'</span>'

            '</div>'

            '<div class="tbl-wrap">'

            '<table class="tbl">'

            '<thead>'
            '<tr>'
            '<th>Asset</th>'
            '<th>Type</th>'
            '<th>Sector</th>'
            '<th>Before</th>'
            '<th>After</th>'
            '<th>Change</th>'
            '<th>Loss</th>'
            '<th>Loss %</th>'
            '</tr>'
            '</thead>'

            f'<tbody>{body}</tbody>'

            '</table>'

            '</div>'

            '</div>'
        )


    else:

        block(
            '<div class="note">'
            '<b>No position data to show.</b>'
            '<br>'
            'Positions appear once an event crosses '
            'the stress threshold.'
            '</div>'
        )


# ============================================================
# METHODOLOGY TAB
# ============================================================

with tab_method:

    block(
        """
        <div class="title">
            Methodology and Scope
        </div>

        <div class="subtitle">
            How a financial text signal becomes
            a portfolio stress result
        </div>

        <div class="row r-three">

            <div class="card">

                <h3 class="card-title"
                    style="margin-bottom:8px">
                    Risk Engine
                </h3>

                <ul class="plain-list">

                    <li>
                        FinBERT financial sentiment analysis
                    </li>

                    <li>
                        Hybrid rule-based and zero-shot
                        event classification
                    </li>

                    <li>
                        Transparent 1–10 impact scoring
                    </li>

                    <li>
                        Configurable stress trigger
                    </li>

                </ul>

            </div>


            <div class="card">

                <h3 class="card-title"
                    style="margin-bottom:8px">
                    Stress Testing
                </h3>

                <ul class="plain-list">

                    <li>
                        Synthetic wholesale banking portfolio
                    </li>

                    <li>
                        Loans, bonds, equities and derivatives
                    </li>

                    <li>
                        Scenario-based sensitivity shocks
                    </li>

                    <li>
                        Strategic event-driven stress analysis
                    </li>

                </ul>

            </div>


            <div class="card">

                <h3 class="card-title"
                    style="margin-bottom:12px">
                    Base Impact by Event Class
                </h3>

                <div class="kv">
                    <span>Credit Event</span>
                    <span>8.0</span>
                </div>

                <div class="kv">
                    <span>Geopolitical</span>
                    <span>7.0</span>
                </div>

                <div class="kv">
                    <span>Macroeconomic, Regulatory</span>
                    <span>6.0</span>
                </div>

                <div class="kv">
                    <span>
                        Merger &amp; Acquisition, Earnings
                    </span>
                    <span>5.0</span>
                </div>

                <div class="kv">
                    <span>Product Launch</span>
                    <span>3.0</span>
                </div>

            </div>

        </div>


        <div class="row r-two">

            <div class="card">

                <h3 class="card-title"
                    style="margin-bottom:12px">
                    Risk Signal Flow
                </h3>

                <div class="kv">
                    <span>Sentiment</span>
                    <span>-1 to +1</span>
                </div>

                <div class="kv">
                    <span>Event Classification</span>
                    <span>Category + confidence</span>
                </div>

                <div class="kv">
                    <span>Impact</span>
                    <span>1–10 severity</span>
                </div>

                <div class="kv">
                    <span>Stress Decision</span>
                    <span>Impact &gt; 7</span>
                </div>

            </div>


            <div class="card">

                <h3 class="card-title"
                    style="margin-bottom:12px">
                    Important Scope Notes
                </h3>

                <ul class="plain-list">

                    <li>
                        Uses public historical datasets
                        for reproducibility.
                    </li>

                    <li>
                        Portfolio is synthetic and
                        assumption-driven.
                    </li>

                    <li>
                        Impact scoring is transparent
                        rule-based severity, not a trained
                        loss prediction model.
                    </li>

                    <li>
                        Stress results are scenario estimates,
                        not regulatory capital calculations.
                    </li>

                </ul>

            </div>

        </div>
        """
    )


# ============================================================
# FOOTER
# ============================================================

block(
    """
    <div class="footer">

        <b style="color:#dfe4e5">
            RiskPulse
        </b>
        is a reproducible prototype using public historical
        data and a synthetic portfolio.

        <br>

        Stress results are scenario-based estimates and are
        not regulatory capital or bank-grade valuation outputs.

    </div>
    """
)