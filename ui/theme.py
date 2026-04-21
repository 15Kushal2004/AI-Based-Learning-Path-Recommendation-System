"""Shared premium CSS theme for all inner pages."""

PREMIUM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Instrument+Sans:wght@400;500;600;700&display=swap');

:root {
    --bg: #0a0e1a;
    --bg-card: rgba(255,255,255,0.04);
    --bg-card-hover: rgba(255,255,255,0.06);
    --bg-subtle: rgba(255,255,255,0.03);
    --bg-input: rgba(255,255,255,0.06);
    --border: rgba(255,255,255,0.08);
    --border-hover: rgba(255,255,255,0.14);
    --border-focus: rgba(99,102,241,0.5);
    --text: #e2e8f0;
    --text-secondary: rgba(255,255,255,0.55);
    --text-muted: rgba(255,255,255,0.35);
    --accent: #6366f1;
    --accent-light: #818cf8;
    --accent-bg: rgba(99,102,241,0.12);
    --accent-border: rgba(99,102,241,0.25);
    --success: #22c55e;
    --success-bg: rgba(34,197,94,0.1);
    --success-border: rgba(34,197,94,0.25);
    --warning: #f59e0b;
    --warning-bg: rgba(245,158,11,0.1);
    --error: #ef4444;
    --error-bg: rgba(239,68,68,0.1);
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
    --shadow-md: 0 4px 14px rgba(0,0,0,0.4);
    --shadow-lg: 0 8px 28px rgba(0,0,0,0.5);
    --radius: 12px;
    --radius-sm: 8px;
    --radius-lg: 16px;
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-display: 'Instrument Sans', 'Inter', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--font-sans) !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.stApp {
    background: var(--bg) !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(99,102,241,0.1), transparent),
        radial-gradient(ellipse 60% 40% at 80% 60%, rgba(139,92,246,0.06), transparent) !important;
}

/* Grid pattern overlay */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: linear-gradient(rgba(255,255,255,0.012) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(255,255,255,0.012) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ─────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0c0f1d !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    min-width: 250px !important;
}
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.55) !important; }
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
    border-radius: 8px !important;
    padding: 6px 10px !important;
    margin: 1px 0 !important;
    transition: all 0.15s ease !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {
    background: rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] {
    background: rgba(99,102,241,0.15) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] * {
    color: #a5b4fc !important;
    font-weight: 600 !important;
}
[data-testid="stSidebarContent"] {
    padding: 0.35rem 0.75rem 0.75rem !important;
    overflow: hidden !important;
}
[data-testid="stSidebar"] > div:first-child {
    overflow: hidden !important;
}

/* ── Main content ────────────────────────────────────── */
.block-container {
    padding: 2rem 2.5rem !important;
    max-width: 100% !important;
}
#MainMenu, footer { visibility: hidden; }

/* Lock the sidebar open and remove Streamlit's collapse control */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
button[aria-label="Toggle sidebar"],
button[aria-label*="sidebar"],
header button[kind="header"] {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
    width: 0 !important;
    height: 0 !important;
    opacity: 0 !important;
}

/* ── Form inputs ─────────────────────────────────────── */
.stTextInput > div > div > input {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    font-size: 0.875rem !important;
    font-weight: 400 !important;
    padding: 10px 13px !important;
    transition: all 0.15s ease !important;
    letter-spacing: -0.01em !important;
}
.stTextInput > div > div > input::placeholder {
    color: var(--text-muted) !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    background: rgba(255,255,255,0.08) !important;
}
.stTextInput > div > div > input:disabled {
    background: var(--bg-subtle) !important;
    color: var(--text-secondary) !important;
    border-color: var(--border) !important;
}
label {
    color: var(--text-secondary) !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
}

/* ── Selects ──────────────────────────────────────────── */
.stSelectbox > div > div,
div[data-baseweb="select"] > div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
}
div[data-baseweb="select"] > div > div {
    color: var(--text) !important;
}
/* Dropdown menu */
div[data-baseweb="popover"] > div {
    background: #111827 !important;
    border: 1px solid var(--border) !important;
}
div[data-baseweb="popover"] li {
    color: var(--text) !important;
}
div[data-baseweb="popover"] li:hover {
    background: rgba(99,102,241,0.15) !important;
}

/* ── Number input ─────────────────────────────────────── */
.stNumberInput > div > div > input {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
}
.stNumberInput button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
}

/* ── Buttons ──────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #818cf8) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.55rem 1.2rem !important;
    font-family: var(--font-sans) !important;
    letter-spacing: -0.01em !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 0 20px rgba(99,102,241,0.15) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 30px rgba(99,102,241,0.3) !important;
    filter: brightness(1.1) !important;
}
.stDownloadButton > button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-weight: 500 !important;
    border-radius: var(--radius-sm) !important;
}
.stDownloadButton > button:hover {
    background: rgba(255,255,255,0.1) !important;
    border-color: var(--border-hover) !important;
}

/* ── Tabs ─────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 10px !important;
    padding: 3px !important;
    gap: 2px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 7px !important;
    color: var(--text-muted) !important;
    font-weight: 500 !important;
    padding: 7px 16px !important;
    font-size: 0.82rem !important;
    transition: all 0.15s ease !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #818cf8) !important;
    color: white !important;
    font-weight: 600 !important;
    box-shadow: 0 0 15px rgba(99,102,241,0.2) !important;
}

/* ── Checkbox & Slider ────────────────────────────────── */
.stCheckbox > label > div { border-color: var(--accent-border) !important; }
.stCheckbox label span { color: var(--text) !important; }
.stSlider > div > div > div > div {
    background: linear-gradient(90deg, var(--accent), var(--accent-light)) !important;
}
.stSlider [data-baseweb="slider"] div {
    color: var(--text) !important;
}

/* ── Cards ────────────────────────────────────────────── */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    box-shadow: var(--shadow-sm);
    margin-bottom: 14px;
    transition: all 0.2s ease;
    backdrop-filter: blur(10px);
}
.card:hover {
    box-shadow: var(--shadow-md);
    border-color: var(--border-hover);
}
.card-title {
    font-family: var(--font-display);
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 4px;
    letter-spacing: -0.02em;
}
.card-sub {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-bottom: 14px;
}

/* ── Stat cards ───────────────────────────────────────── */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 16px;
}
.stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
    transition: all 0.2s ease;
    backdrop-filter: blur(10px);
}
.stat-card:hover {
    box-shadow: var(--shadow-md);
    border-color: var(--border-hover);
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent-light));
}
.stat-icon {
    width: 34px; height: 34px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; margin-bottom: 10px;
}
.stat-num {
    font-family: var(--font-display);
    font-size: 1.75rem; font-weight: 700; color: var(--text);
    line-height: 1; letter-spacing: -0.03em;
}
.stat-lbl {
    font-size: 0.7rem; color: var(--text-muted);
    font-weight: 500; margin-top: 4px;
    letter-spacing: 0.01em;
}

/* ── Week label ───────────────────────────────────────── */
.wk {
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--accent-bg); border: 1px solid var(--accent-border);
    border-radius: 6px; padding: 4px 12px; margin: 10px 0 5px;
    font-family: var(--font-display);
    font-size: 0.75rem; font-weight: 600; color: var(--accent-light);
}

/* ── Topic row ────────────────────────────────────────── */
.trow {
    display: flex; align-items: center; gap: 10px;
    background: var(--bg-subtle); border: 1px solid var(--border);
    border-radius: var(--radius-sm); padding: 8px 12px; margin: 3px 0;
    transition: all 0.15s ease;
}
.trow:hover { border-color: var(--border-hover); background: var(--bg-card-hover); }
.trow.done { background: var(--success-bg); border-color: var(--success-border); }
.tstep {
    background: var(--accent-bg); color: var(--accent-light);
    font-size: 0.62rem; font-weight: 700;
    width: 22px; height: 22px; border-radius: 5px;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.tname { flex: 1; font-size: 0.82rem; font-weight: 500; color: var(--text); }
.tname.done { text-decoration: line-through; color: var(--text-muted); }
.tcat {
    background: var(--accent-bg); color: var(--accent-light);
    font-size: 0.62rem; font-weight: 600; padding: 2px 7px; border-radius: 4px;
}
.tdur {
    font-size: 0.72rem; font-weight: 600; color: var(--accent-light);
    min-width: 30px; text-align: right;
}

/* Level badges */
.lbeg { background: rgba(34,197,94,0.15); color: #4ade80; font-size: 0.6rem; font-weight: 600; padding: 2px 6px; border-radius: 3px; }
.lint  { background: rgba(99,102,241,0.15); color: #a5b4fc; font-size: 0.6rem; font-weight: 600; padding: 2px 6px; border-radius: 3px; }
.ladv  { background: rgba(245,158,11,0.15); color: #fbbf24; font-size: 0.6rem; font-weight: 600; padding: 2px 6px; border-radius: 3px; }

/* ── Cluster banner ───────────────────────────────────── */
.cl-ban {
    border-radius: var(--radius); padding: 14px 18px; margin-bottom: 16px;
    display: flex; align-items: center; gap: 14px; border: 1px solid;
    backdrop-filter: blur(10px);
}

/* ── Progress bar ────────────────────────────────────── */
.pb { background: rgba(255,255,255,0.06); border-radius: 6px; height: 6px; overflow: hidden; }
.pbf { height: 100%; border-radius: 6px; transition: width 0.5s ease; }

/* ── Skill row ────────────────────────────────────────── */
.skrow { margin-bottom: 10px; }
.sktop { display: flex; justify-content: space-between; margin-bottom: 3px; }
.skname {
    font-size: 0.78rem; font-weight: 500; color: var(--text-secondary);
    display: flex; align-items: center; gap: 6px;
}
.skpct { font-size: 0.78rem; font-weight: 600; }

/* ── Divider ──────────────────────────────────────────── */
.fdiv {
    height: 1px; background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 16px 0;
}

/* ── Alerts ───────────────────────────────────────────── */
.awarn {
    background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.25); border-radius: var(--radius-sm);
    padding: 11px 14px; margin: 8px 0; font-size: 0.82rem; color: #fbbf24;
}
.ainfo {
    background: rgba(56,189,248,0.1); border: 1px solid rgba(56,189,248,0.2); border-radius: var(--radius-sm);
    padding: 11px 14px; margin: 8px 0; font-size: 0.82rem; color: #38bdf8;
}
.asuc {
    background: var(--success-bg); border: 1px solid var(--success-border); border-radius: var(--radius-sm);
    padding: 11px 14px; margin: 8px 0; font-size: 0.82rem; color: #4ade80;
}

/* ── Resource ─────────────────────────────────────────── */
.res {
    display: flex; align-items: center; gap: 12px;
    background: var(--bg-subtle); border: 1px solid var(--border);
    border-radius: var(--radius-sm); padding: 10px 14px; margin: 6px 0;
    transition: all 0.15s ease;
}
.res:hover { border-color: var(--border-hover); box-shadow: var(--shadow-sm); }
.res-btn {
    background: linear-gradient(135deg, #6366f1, #818cf8); color: white;
    border: none; border-radius: 6px; padding: 5px 12px;
    font-size: 0.7rem; font-weight: 600; text-decoration: none;
    flex-shrink: 0; margin-left: auto;
    transition: all 0.15s ease;
}
.res-btn:hover { filter: brightness(1.15); color: white; box-shadow: 0 0 15px rgba(99,102,241,0.3); }

/* ── Schedule ─────────────────────────────────────────── */
.sched { display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; margin-top: 10px; }
.sdlbl { font-size: 0.62rem; font-weight: 600; color: var(--text-muted); text-align: center; margin-bottom: 3px; }
.sdslot { border-radius: 6px; padding: 6px 3px; font-size: 0.68rem; font-weight: 600; text-align: center; }
.sdslot.a { background: linear-gradient(135deg, #6366f1, #818cf8); color: white; }
.sdslot.r { background: var(--accent-bg); color: var(--accent-light); }
.sdslot.x { background: var(--bg-subtle); color: var(--text-muted); }

/* ── Roadmap preview ──────────────────────────────────── */
.rpnode { display: flex; align-items: center; gap: 10px; margin: 4px 0; }
.rpdot {
    width: 26px; height: 26px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.68rem; font-weight: 700; color: white;
    flex-shrink: 0; box-shadow: 0 0 12px rgba(99,102,241,0.2);
}
.rpline { width: 2px; height: 14px; background: var(--border); margin-left: 12px; }
.rplbl { font-size: 0.78rem; font-weight: 500; color: var(--text-secondary); flex: 1; }

/* ── Expanders ────────────────────────────────────────── */
.streamlit-expanderHeader {
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
    background: transparent !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
details {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    background: var(--bg-card) !important;
}
details summary {
    color: var(--text) !important;
}

/* ── Metrics ──────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 12px !important;
}
[data-testid="stMetricLabel"] { color: var(--text-muted) !important; }
[data-testid="stMetricValue"] { color: var(--text) !important; }

/* ── Info/Warning/Success boxes ───────────────────────── */
.stAlert > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: var(--radius-sm) !important;
}

/* ── Spinner ──────────────────────────────────────────── */
.stSpinner > div { color: var(--text-muted) !important; }

/* ── Caption ─────────────────────────────────────────── */
.stCaption, .stMarkdown small { color: var(--text-muted) !important; }
</style>
"""
