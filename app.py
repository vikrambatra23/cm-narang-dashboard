import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection
from datetime import date, datetime

# ── 1. PAGE CONFIGURATION ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wealth Dashboard · CM Narang",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── 1b. PWA BOOTSTRAP ─────────────────────────────────────────────────────────
# Streamlit doesn't expose <head>, so we inject manifest + SW registration
# from inside an iframe component using window.parent.
components.html(
    """
    <script>
    (function () {
      try {
        const parentWin = window.parent;
        const doc = parentWin.document;
        const head = doc.head;
        // Streamlit serves /static/* relative to the app base URL.
        const base = parentWin.location.pathname.replace(/\\/$/, '');
        const staticUrl = (f) => base + '/app/static/' + f;
        const ensure = (selector, build) => {
          if (!doc.querySelector(selector)) head.appendChild(build());
        };
        ensure('link[rel="manifest"]', () => {
          const l = doc.createElement('link');
          l.rel = 'manifest';
          l.href = staticUrl('manifest.json');
          return l;
        });
        ensure('meta[name="theme-color"]', () => {
          const m = doc.createElement('meta');
          m.name = 'theme-color';
          m.content = '#050A14';
          return m;
        });
        ensure('meta[name="apple-mobile-web-app-capable"]', () => {
          const m = doc.createElement('meta');
          m.name = 'apple-mobile-web-app-capable';
          m.content = 'yes';
          return m;
        });
        ensure('meta[name="apple-mobile-web-app-status-bar-style"]', () => {
          const m = doc.createElement('meta');
          m.name = 'apple-mobile-web-app-status-bar-style';
          m.content = 'black-translucent';
          return m;
        });
        ensure('meta[name="apple-mobile-web-app-title"]', () => {
          const m = doc.createElement('meta');
          m.name = 'apple-mobile-web-app-title';
          m.content = 'CM Narang';
          return m;
        });
        ensure('link[rel="apple-touch-icon"]', () => {
          const l = doc.createElement('link');
          l.rel = 'apple-touch-icon';
          l.href = staticUrl('icon-192.png');
          return l;
        });
        const nav = parentWin.navigator;
        if (nav && 'serviceWorker' in nav) {
          nav.serviceWorker.register(staticUrl('service-worker.js')).catch(() => {});
        }
      } catch (e) { /* ignore */ }
    })();
    </script>
    """,
    height=0,
)

# ── 2. ROYAL UI STYLING (CSS) ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #050A14; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.block-container { padding: 1.5rem 2rem 4rem 2rem; max-width: 1100px; }
.stApp {
    background:
        radial-gradient(ellipse at top left, rgba(200,168,75,0.05) 0%, transparent 45%),
        radial-gradient(ellipse at bottom right, rgba(87,135,199,0.04) 0%, transparent 45%),
        #050A14 !important;
}
p, div, span, label { color: #EAE3D6; }

.gold-text {
    background: linear-gradient(to bottom, #C8A84B 0%, #E2CC8A 50%, #B38F36 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700; font-size: 72px !important; letter-spacing: -2px; line-height: 1.1;
}

.login-card {
    background: rgba(12, 26, 46, 0.85);
    border: 1px solid #C8A84B;
    border-radius: 20px;
    padding: 40px;
    box-shadow: 0 10px 40px rgba(200,168,75,0.15), inset 0 1px 0 rgba(226,204,138,0.1);
    text-align: center;
}

div.stButton > button:first-child {
    background: linear-gradient(90deg, #C8A84B, #B38F36) !important;
    color: #050A14 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    width: 100%;
    transition: all 0.3s ease !important;
}
div.stButton > button:first-child:hover {
    box-shadow: 0 6px 22px rgba(200,168,75,0.35) !important;
    transform: translateY(-1px);
}

div[role="radiogroup"] label {
    background: #0C1A2E !important; border: 1px solid #1C3050 !important;
    border-radius: 12px !important; padding: 10px 24px !important; color: #5C7089 !important;
    transition: all 0.25s ease !important;
}
div[role="radiogroup"] label:hover { border-color: rgba(200,168,75,0.4) !important; color: #E2CC8A !important; }
div[role="radiogroup"] label:has(input:checked) {
    background: rgba(200,168,75,0.12) !important; border-color: #C8A84B !important; color: #C8A84B !important;
    box-shadow: 0 0 18px rgba(200,168,75,0.15);
}

/* Header accent */
.header-accent {
    height: 3px; width: 80px;
    background: linear-gradient(90deg, #C8A84B, transparent);
    border-radius: 2px; margin: 6px 0 0 0;
}
.monogram {
    display: inline-block; color: #C8A84B; font-size: 34px;
    margin-right: 14px; vertical-align: middle;
    filter: drop-shadow(0 0 10px rgba(200,168,75,0.35));
}

/* KPI Tiles */
.kpi-tile {
    background: linear-gradient(145deg, #0C1A2E 0%, #0A1528 100%);
    border: 1px solid #1C3050;
    border-radius: 14px;
    padding: 18px 22px;
    transition: all 0.3s ease;
    position: relative; overflow: hidden;
    margin-bottom: 4px;
}
.kpi-tile::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent 0%, #C8A84B 50%, transparent 100%);
    opacity: 0.7;
}
.kpi-tile:hover {
    border-color: rgba(200,168,75,0.5);
    box-shadow: 0 8px 24px rgba(200,168,75,0.12);
    transform: translateY(-2px);
}
.kpi-label { color: #7A9BBF; font-size: 10px; letter-spacing: 1.5px; text-transform: uppercase; margin: 0 0 8px 0; font-weight: 500; }
.kpi-value { color: #E2CC8A; font-size: 24px; font-weight: 600; font-family: 'JetBrains Mono', monospace; margin: 0; }
.kpi-icon { float: right; color: #C8A84B; font-size: 22px; opacity: 0.55; margin-top: -2px; }

/* Section divider */
.section-divider { display: flex; align-items: center; gap: 14px; margin: 32px 0 20px 0; }
.section-divider::before, .section-divider::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, transparent, #1C3050 35%, #1C3050 65%, transparent);
}
.section-divider-mark { color: #C8A84B; font-size: 12px; letter-spacing: 6px; opacity: 0.8; }

/* Insurance cards */
.insurance-card {
    background: linear-gradient(145deg, #0C1A2E 0%, #0A1528 100%);
    padding: 22px; border-radius: 14px; border: 1px solid #1C3050;
    transition: all 0.3s ease; position: relative; overflow: hidden;
}
.insurance-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #C8A84B, transparent);
}
.insurance-card:hover {
    border-color: rgba(200,168,75,0.4);
    box-shadow: 0 6px 20px rgba(200,168,75,0.1);
    transform: translateY(-2px);
}
.insurance-icon { font-size: 22px; color: #C8A84B; opacity: 0.85; margin-bottom: 10px; display: block; }

/* Action cards */
.action-card {
    padding: 20px 24px;
    border-left: 3px solid #1C3050;
    background: linear-gradient(90deg, rgba(12,26,46,0.45) 0%, transparent 100%);
    margin-bottom: 12px;
    border-radius: 0 12px 12px 0;
    transition: all 0.3s ease;
}
.action-card:hover {
    border-left-color: #C8A84B;
    background: linear-gradient(90deg, rgba(200,168,75,0.08) 0%, transparent 100%);
    transform: translateX(4px);
}
.action-number {
    display: inline-flex;
    align-items: center; justify-content: center;
    width: 28px; height: 28px;
    background: linear-gradient(135deg, #E2CC8A, #B38F36);
    color: #050A14;
    border-radius: 50%;
    font-weight: 700; font-size: 12px;
    margin-right: 14px;
    vertical-align: middle;
    box-shadow: 0 2px 10px rgba(200,168,75,0.3);
    flex-shrink: 0;
}

/* Portfolio table polish */
.static-table { width: 100%; border-collapse: collapse; margin-top: 20px; border-radius: 12px; overflow: hidden; }
.static-table th { background: #0C1A2E; color: #C8A84B; text-align: left; padding: 15px; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 2px solid #C8A84B; }
.static-table td { padding: 14px 15px; border-bottom: 1px solid #1C3050; font-size: 13px; color: #EAE3D6; }
.static-table tbody tr { transition: background 0.2s ease; }
.static-table tbody tr:nth-child(even) td { background: rgba(12,26,46,0.35); }
.static-table tbody tr:hover td { background: rgba(200,168,75,0.07); color: #E2CC8A; }
</style>
""", unsafe_allow_html=True)

# ── 3. DATA HELPERS ───────────────────────────────────────────────────────────
def fmt_cr(n): return f"₹{n/1e7:.2f} Cr"
def fmt_l(n):  return f"₹{n/1e5:.1f} L"

# ── 4. LIVE GOOGLE SHEETS CONNECTION ──────────────────────────────────────────
URL = "https://docs.google.com/spreadsheets/d/1PZACfddE3VkcCWqYD-_0j_ERaBUT1SBQqPN63Vylvy0/export?format=csv"
PLAN_URL = "https://docs.google.com/spreadsheets/d/1PZACfddE3VkcCWqYD-_0j_ERaBUT1SBQqPN63Vylvy0/export?format=csv&gid=1751726483"
LIVE_RATES_URL = "https://docs.google.com/spreadsheets/d/1PZACfddE3VkcCWqYD-_0j_ERaBUT1SBQqPN63Vylvy0/export?format=csv&gid=1691255921"
conn = st.connection("gsheets", type=GSheetsConnection)

PRICE_TTL = 900    # 15 min — live market prices (GOOGLEFINANCE-backed)
PLAN_TTL  = 3600   # 1 hour — planning data changes rarely

@st.cache_data(ttl=PRICE_TTL)
def fetch_data():
    df = conn.read(spreadsheet=URL, ttl=PRICE_TTL)
    if 'Current Value' in df.columns:
        df['Val_Num'] = pd.to_numeric(df['Current Value'].astype(str).replace('[₹,L,Cr, ,]', '', regex=True), errors='coerce').fillna(0)
    assets = df[~df['Asset Name'].str.contains('Total|TOTAL|Sum|Subtotal', na=False)]
    return assets.dropna(subset=['Asset Name'])

@st.cache_data(ttl=PLAN_TTL)
def fetch_plan():
    df = conn.read(spreadsheet=PLAN_URL, ttl=PLAN_TTL).dropna(how='all')
    return df.fillna('').astype(str).replace({'nan': '', 'NaN': ''})

@st.cache_data(ttl=PRICE_TTL)
def fetch_live_rates():
    """Live GOOGLEFINANCE prices from the 'Live Rates' tab, keyed by ticker/symbol (col A → col B)."""
    df = conn.read(spreadsheet=LIVE_RATES_URL, ttl=PRICE_TTL)
    prices = {}
    for _, r in df.iterrows():
        key = str(r.iloc[0]).strip().upper()
        try:
            prices[key] = float(r.iloc[1])
        except (ValueError, TypeError, IndexError):
            continue
    return prices

# ── 4b. NEW INVESTMENTS LEDGER (post-2026-05-11, ICICI Direct lump sums) ──────
# `ltp` here is only a FALLBACK — live prices are pulled per-render from the
# 'Live Rates' tab (GOOGLEFINANCE) and matched on the symbol. Symbols not in
# that tab (e.g. LIQUIDBEES, fixed NAV) keep the ltp below.
# Future SIPs on Zerodha Coin appended to SIPS_PLANNED.
NEW_LUMPSUM = [
    # symbol,        name,                            kind,     qty,    buy,     ltp,     date,         platform,        theme
    ("AVANTIFEED",   "Avanti Feeds",                  "Equity", 72,     1417.00, 1417.90, "2026-05-11", "ICICI Direct",  "Animal protein · defensive"),
    ("SOUTHBANK",    "South Indian Bank",             "Equity", 2400,   40.67,   40.65,   "2026-05-11", "ICICI Direct",  "PSU/private bank rerating"),
    ("COALINDIA",    "Coal India",                    "Equity", 217,    460.75,  460.70,  "2026-05-11", "ICICI Direct",  "Energy · high dividend"),
    ("MOTHERSON",    "Samvardhana Motherson",         "Equity", 760,    131.02,  130.87,  "2026-05-11", "ICICI Direct",  "Auto ancillary"),
    ("SHILPAMED",    "Shilpa Medicare",               "Equity", 222,    449.40,  447.85,  "2026-05-11", "ICICI Direct",  "Pharma · midcap"),
    ("LIQUIDBEES",   "Nippon India Liquid BeES",      "Liquid", 3500,   999.99,  999.99,  "2026-05-11", "ICICI Direct",  "Dry powder · staged for MF deployment via Coin"),
]

# SIPs / Direct MF holdings on Zerodha Coin — populate from Jan 2027 onwards
SIPS_PLANNED = [
    # ("MOTILAL_MIDCAP", "Motilal Oswal Midcap Direct G", "MF",  25000, "Monthly",  "2027-01-05", "Zerodha Coin", "18% of catch-up bucket"),
]

# Liquid-to-MF deployment plan (the ₹35L LIQUIDBEES → 4 funds via Coin)
DEPLOYMENT_PLAN = {
    "source":         "LIQUIDBEES (₹35.0 L)",
    "target":         "4 Direct MFs on Zerodha Coin",
    "start_target":   "Jun 2026",
    "duration_mo":    8,
    "deployed_l":     0.0,   # update as STP tranches execute
    "total_l":        35.0,
}

# ── 5. CALCULATIONS (UPDATED FOR INDIVIDUAL STOCKS) ───────────────────────────
try:
    assets_df = fetch_data()
    total_nw = assets_df['Val_Num'].sum()
    
    # Categorize specifically matching your sheet labels
    mf_v = assets_df[assets_df['Category'].str.contains('Aggressive|Stable|Legacy \(Exit\)', na=False)]['Val_Num'].sum()
    etf_v = assets_df[assets_df['Category'].str.contains('New Core|New Global|New Stability', na=False)]['Val_Num'].sum()
    equity_v = assets_df[assets_df['Category'] == "Legacy"]['Val_Num'].sum() # Individual Stocks
    gold_v = assets_df[assets_df['Category'].str.contains('Commodities', na=False)]['Val_Num'].sum()
    fd_v = assets_df[assets_df['Category'].str.contains('Fixed Income', na=False)]['Val_Num'].sum()
    cash_v = assets_df[assets_df['Category'].str.contains('Liquid', na=False)]['Val_Num'].sum()

    OVERVIEW_MAP = {
        "Mutual Funds": mf_v, 
        "Direct Equity": equity_v, 
        "ETFs": etf_v, 
        "Gold": gold_v, 
        "Fixed Income": fd_v, 
        "Cash": cash_v
    }
except:
    st.stop()

# ── 6. LOGIN SYSTEM ───────────────────────────────────────────────────────────
ACCESS_PIN = "2323"
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.write("##")
    st.write("##")
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div class='login-card'><h2 style='color:#C8A84B; margin-bottom:0;'>◈ PRIVATE WEALTH</h2><p style='color:#7A9BBF; font-size:12px; letter-spacing:2px; margin-bottom:8px;'>CHANDRA MOHAN NARANG</p><p style='color:#7A9BBF; font-size:11px; letter-spacing:1.5px; margin-bottom:30px;'>ENTER 4-DIGIT ACCESS PIN</p></div>", unsafe_allow_html=True)
        with st.form("pin_form", clear_on_submit=False):
            pin = st.text_input(
                "Access PIN",
                type="password",
                max_chars=4,
                placeholder="• • • •",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("UNLOCK")
        if submitted:
            if pin == ACCESS_PIN:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid PIN")
    st.stop()

# ── 7. HEADER ─────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([2, 1])
with col_h1:
    st.markdown("<div style='display:flex; align-items:center;'><span class='monogram'>◈</span><div><h1 style='background: linear-gradient(90deg, #C8A84B, #E2CC8A); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; font-size: 38px; margin:0; padding:0;'>Chandra Mohan Narang</h1><p style='color: #7A9BBF; font-size: 11px; text-transform: uppercase; letter-spacing: 2.5px; margin: 2px 0 0 0;'>Family Office Dashboard</p><div class='header-accent'></div></div></div>", unsafe_allow_html=True)
with col_h2:
    st.markdown(f"<div style='text-align: right; padding-top: 18px;'><p style='color: #5C7089; font-size: 10px; letter-spacing: 2px; margin-bottom: 2px;'>VALUATION DATE</p><p style='color: #EAE3D6; font-size: 14px; font-weight: 500; font-family: \"JetBrains Mono\", monospace;'>{pd.Timestamp.now().strftime('%d %B, %Y')}</p></div>", unsafe_allow_html=True)

st.markdown("<hr style='margin: 12px 0 18px 0; border: 0; border-top: 1px solid #1C3050;'>", unsafe_allow_html=True)
tab = st.radio("nav", ["Overview", "Portfolio", "New", "Plan", "Protection", "Actions"], horizontal=True, label_visibility="collapsed")

# ── 8. TABS ───────────────────────────────────────────────────────────────────
if tab == "Overview":
    deployed_v = total_nw - cash_v
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"<div class='kpi-tile'><span class='kpi-icon'>◈</span><p class='kpi-label'>Net Worth</p><p class='kpi-value'>{fmt_cr(total_nw)}</p></div>", unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='kpi-tile'><span class='kpi-icon'>▲</span><p class='kpi-label'>Deployed Capital</p><p class='kpi-value'>{fmt_cr(deployed_v)}</p></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='kpi-tile'><span class='kpi-icon'>✦</span><p class='kpi-label'>Cash · Ready to Deploy</p><p class='kpi-value'>{fmt_l(cash_v)}</p></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-divider'><span class='section-divider-mark'>◆ ◆ ◆</span></div>", unsafe_allow_html=True)

    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = total_nw / 10000000,
        number = {'suffix': " Cr", 'font': {'color': '#E2CC8A', 'size': 50}},
        title = {'text': "GOAL PROGRESS: 10 CR JOURNEY", 'font': {'size': 12, 'color': '#7A9BBF'}},
        gauge = {'axis': {'range': [0, 10], 'tickcolor': '#1C3050', 'tickfont': {'color': '#5C7089', 'size': 10}}, 'bar': {'color': "#C8A84B", 'thickness': 0.85}, 'bgcolor': "#0C1A2E", 'borderwidth': 0, 'steps': [{'range': [0, 10], 'color': '#0C1A2E'}], 'threshold': {'line': {'color': '#E2CC8A', 'width': 2}, 'thickness': 0.9, 'value': total_nw / 10000000}}
    ))
    fig_gauge.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=50, b=20, l=20, r=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("<div class='section-divider'><span class='section-divider-mark'>◆ ◆ ◆</span></div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        # Pie Chart with extra slice for Individual Stocks
        fig = go.Figure(go.Pie(labels=list(OVERVIEW_MAP.keys()), values=list(OVERVIEW_MAP.values()), hole=0.7, marker=dict(colors=['#52A2FF','#FF8E52','#57C785','#E2CC8A','#46C1C1','#A37CFF'])))
        fig.update_layout(showlegend=True, paper_bgcolor='rgba(0,0,0,0)', legend=dict(font=dict(color="#7A9BBF", size=10), orientation="h", y=-0.2), margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("<p style='font-size:12px; color:#C8A84B; font-weight:600; letter-spacing:1px; margin-bottom:20px;'>ALLOCATION SUMMARY</p>", unsafe_allow_html=True)
        for label, val in OVERVIEW_MAP.items():
            if val > 0:
                badge = " <span style='background:rgba(87,199,133,0.15); color:#57C785; font-size:9px; padding:2px 8px; border-radius:10px; margin-left:8px; font-weight:600; letter-spacing:0.5px; vertical-align:middle;'>READY TO DEPLOY</span>" if label == "Cash" else ""
                st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:18px; border-bottom:1px solid #1C3050; padding-bottom:6px;'><span>{label}{badge}</span><span style='font-family:\"JetBrains Mono\";'>{fmt_l(val)}</span></div>", unsafe_allow_html=True)

elif tab == "Portfolio":
    st.markdown("<p style='font-size:20px; color:#C8A84B; font-weight:500; letter-spacing:0.5px; margin-bottom:4px;'>Detailed Holding Inventory</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#7A9BBF; font-size:11px; letter-spacing:1.5px; margin-bottom:18px;'>LEGACY BOOK · ICICI DIRECT (REGULAR PLANS) + EXISTING DIRECT EQUITY · POST-MAY-2026 PURCHASES TRACKED IN <strong style='color:#C8A84B;'>NEW</strong> TAB</p>", unsafe_allow_html=True)
    disp = assets_df[['Asset Name', 'Category', 'Units / Qty', 'Current Value', 'Val_Num']].copy()
    disp = disp.sort_values(by='Val_Num', ascending=False)
    disp['Alloc %'] = (disp['Val_Num'] / total_nw * 100).round(1).astype(str) + '%'
    html = "<table class='static-table'><thead><tr><th>Asset Name</th><th>Category</th><th>Qty</th><th>Value</th><th>Alloc %</th></tr></thead><tbody>"
    for _, r in disp.iterrows():
        html += f"<tr><td>{r['Asset Name']}</td><td>{r['Category']}</td><td>{r['Units / Qty']}</td><td>{fmt_l(r['Val_Num'])}</td><td>{r['Alloc %']}</td></tr>"
    st.markdown(html + "</tbody></table>", unsafe_allow_html=True)

elif tab == "New":
    today = pd.Timestamp.now().date()

    # Live prices for the new equities (GOOGLEFINANCE via the 'Live Rates' tab).
    # Falls back to the hardcoded ltp for any symbol not in the sheet (e.g. LIQUIDBEES).
    live_prices = fetch_live_rates()

    # Build per-holding metrics
    rows = []
    for sym, name, kind, qty, buy, ltp, dt, plat, theme in NEW_LUMPSUM:
        ltp = live_prices.get(sym.upper(), ltp)
        d = datetime.strptime(dt, "%Y-%m-%d").date()
        invested = qty * buy
        current  = qty * ltp
        pnl      = current - invested
        ret_pct  = (pnl / invested * 100) if invested else 0
        rows.append(dict(symbol=sym, name=name, kind=kind, qty=qty, buy=buy, ltp=ltp,
                         date=d, days=(today - d).days, invested=invested, current=current,
                         pnl=pnl, ret=ret_pct, platform=plat, theme=theme))

    eq  = [r for r in rows if r['kind'] == 'Equity']
    liq = [r for r in rows if r['kind'] == 'Liquid']

    inv_eq  = sum(r['invested'] for r in eq)
    cur_eq  = sum(r['current']  for r in eq)
    pnl_eq  = cur_eq - inv_eq
    ret_eq  = (pnl_eq / inv_eq * 100) if inv_eq else 0
    inv_liq = sum(r['invested'] for r in liq)
    cur_liq = sum(r['current']  for r in liq)
    inv_total = inv_eq + inv_liq
    cur_total = cur_eq + cur_liq
    pnl_total = cur_total - inv_total
    ret_total = (pnl_total / inv_total * 100) if inv_total else 0

    st.markdown("<p style='font-size:20px; color:#C8A84B; font-weight:500; letter-spacing:0.5px; margin-bottom:4px;'>New Investments · Live Tracking</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#7A9BBF; font-size:11px; letter-spacing:1.5px; margin-bottom:18px;'>POST 2026-05-11 · LUMP SUMS VIA ICICI DIRECT · ZERODHA COIN (DIRECT) ONBOARDING JUN 2026</p>", unsafe_allow_html=True)

    # KPI Row
    k1, k2, k3, k4 = st.columns(4)
    pnl_color = "#57C785" if pnl_total >= 0 else "#FF6B6B"
    sig = "+" if pnl_total >= 0 else ""
    with k1:
        st.markdown(f"<div class='kpi-tile'><span class='kpi-icon'>◈</span><p class='kpi-label'>New Deployed</p><p class='kpi-value'>{fmt_l(inv_total)}</p></div>", unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='kpi-tile'><span class='kpi-icon'>▲</span><p class='kpi-label'>Direct Equity</p><p class='kpi-value'>{fmt_l(inv_eq)}</p></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='kpi-tile'><span class='kpi-icon'>✦</span><p class='kpi-label'>Liquid · Dry Powder</p><p class='kpi-value'>{fmt_l(inv_liq)}</p></div>", unsafe_allow_html=True)
    with k4:
        st.markdown(f"<div class='kpi-tile'><span class='kpi-icon'>±</span><p class='kpi-label'>Net P&amp;L</p><p class='kpi-value' style='color:{pnl_color};'>{sig}{ret_total:.2f}%</p></div>", unsafe_allow_html=True)

    # Direct Equity table
    st.markdown("<div class='section-divider'><span class='section-divider-mark'>◆ ◆ ◆</span></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:14px; color:#C8A84B; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; margin:8px 0 12px 0;'>◈ Direct Equity · ICICI Direct</p>", unsafe_allow_html=True)
    eq_html = "<table class='static-table'><thead><tr><th>Symbol</th><th>Theme</th><th>Qty</th><th>Buy ₹</th><th>LTP ₹</th><th>Invested</th><th>Current</th><th>Return</th><th>Held</th></tr></thead><tbody>"
    for r in eq:
        rc = "#57C785" if r['ret'] >= 0 else "#FF6B6B"
        rs = "+" if r['ret'] >= 0 else ""
        eq_html += (
            f"<tr><td><strong>{r['symbol']}</strong><br><span style='color:#7A9BBF; font-size:10px;'>{r['name']}</span></td>"
            f"<td style='color:#7A9BBF; font-size:11px;'>{r['theme']}</td>"
            f"<td>{r['qty']}</td>"
            f"<td style='font-family:\"JetBrains Mono\";'>{r['buy']:.2f}</td>"
            f"<td style='font-family:\"JetBrains Mono\";'>{r['ltp']:.2f}</td>"
            f"<td>{fmt_l(r['invested'])}</td>"
            f"<td>{fmt_l(r['current'])}</td>"
            f"<td style='color:{rc}; font-family:\"JetBrains Mono\"; font-weight:600;'>{rs}{r['ret']:.2f}%</td>"
            f"<td style='font-family:\"JetBrains Mono\";'>{r['days']}d</td></tr>"
        )
    sub_c = "#57C785" if ret_eq >= 0 else "#FF6B6B"
    sub_s = "+" if ret_eq >= 0 else ""
    eq_html += (
        f"<tr style='font-weight:700; color:#E2CC8A;'>"
        f"<td colspan='5' style='border-top:2px solid #C8A84B;'>SUBTOTAL · {len(eq)} HOLDINGS</td>"
        f"<td style='border-top:2px solid #C8A84B;'>{fmt_l(inv_eq)}</td>"
        f"<td style='border-top:2px solid #C8A84B;'>{fmt_l(cur_eq)}</td>"
        f"<td style='color:{sub_c}; border-top:2px solid #C8A84B;'>{sub_s}{ret_eq:.2f}%</td>"
        f"<td style='border-top:2px solid #C8A84B;'>—</td></tr>"
    )
    eq_html += "</tbody></table>"
    st.markdown(eq_html, unsafe_allow_html=True)

    # Liquid / Dry Powder
    st.markdown("<div class='section-divider'><span class='section-divider-mark'>◆ ◆ ◆</span></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:14px; color:#C8A84B; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; margin:8px 0 12px 0;'>◈ Liquid · Dry Powder Staged for MF Deployment</p>", unsafe_allow_html=True)

    lr        = liq[0]
    deployed  = DEPLOYMENT_PLAN['deployed_l']
    pool_l    = DEPLOYMENT_PLAN['total_l']
    pct       = (deployed / pool_l * 100) if pool_l else 0
    remaining = pool_l - deployed

    st.markdown(
        f"<div class='insurance-card'>"
        f"<div style='display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:14px;'>"
        f"<div>"
        f"<p style='color:#7A9BBF; font-size:10px; letter-spacing:1.5px; margin:0 0 4px 0;'>HOLDING</p>"
        f"<h3 style='color:#C8A84B; font-size:18px; font-weight:700; margin:0;'>{lr['symbol']}</h3>"
        f"<p style='color:#EAE3D6; font-size:12px; margin:2px 0 0 0;'>{lr['name']}</p>"
        f"<p style='color:#7A9BBF; font-size:11px; margin:6px 0 0 0;'>{lr['qty']} units · bought {lr['date']} · {lr['days']}d held</p>"
        f"</div>"
        f"<div style='text-align:right;'>"
        f"<p style='color:#7A9BBF; font-size:10px; letter-spacing:1.5px; margin:0;'>VALUE</p>"
        f"<p style='font-family:\"JetBrains Mono\"; color:#E2CC8A; font-size:24px; font-weight:600; margin:2px 0;'>{fmt_l(lr['current'])}</p>"
        f"<p style='color:#57C785; font-size:11px; margin:0;'>~6-7% p.a. daily distribution</p>"
        f"</div>"
        f"</div>"
        f"<p style='color:#7A9BBF; font-size:11px; line-height:1.5; margin:8px 0 18px 0; font-style:italic;'>"
        f"LIQUIDBEES NAV is fixed at ₹1,000; returns accrue as <strong style='color:#EAE3D6;'>daily distribution of fractional units</strong>, not price appreciation. Refresh unit count periodically to capture growth."
        f"</p>"
        f"<div style='border-top:1px solid #1C3050; padding-top:14px;'>"
        f"<div style='display:flex; justify-content:space-between; align-items:baseline; margin-bottom:10px;'>"
        f"<p style='color:#C8A84B; font-size:11px; letter-spacing:1.5px; margin:0; font-weight:600;'>DEPLOYMENT PROGRESS → 4 DIRECT MFs ON COIN</p>"
        f"<p style='font-family:\"JetBrains Mono\"; color:#E2CC8A; font-size:14px; margin:0; font-weight:600;'>{pct:.0f}%</p>"
        f"</div>"
        f"<div style='background:#0A1528; height:12px; border-radius:6px; overflow:hidden; border:1px solid #1C3050;'>"
        f"<div style='height:100%; width:{pct}%; background:linear-gradient(90deg, #C8A84B, #E2CC8A); box-shadow: 0 0 12px rgba(200,168,75,0.4);'></div>"
        f"</div>"
        f"<div style='display:flex; justify-content:space-between; margin-top:10px; gap:12px;'>"
        f"<p style='color:#7A9BBF; font-size:10px; margin:0;'>Deployed: <strong style='color:#57C785;'>₹{deployed:.1f}L</strong></p>"
        f"<p style='color:#7A9BBF; font-size:10px; margin:0;'>Remaining: <strong style='color:#E2CC8A;'>₹{remaining:.1f}L</strong></p>"
        f"<p style='color:#7A9BBF; font-size:10px; margin:0; text-align:right;'>Start: <strong style='color:#EAE3D6;'>{DEPLOYMENT_PLAN['start_target']}</strong> · {DEPLOYMENT_PLAN['duration_mo']}-mo STP</p>"
        f"</div>"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True
    )

    # SIPs section (placeholder until Jan 2027)
    st.markdown("<div class='section-divider'><span class='section-divider-mark'>◆ ◆ ◆</span></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:14px; color:#C8A84B; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; margin:8px 0 12px 0;'>◈ SIPs · Zerodha Coin (Direct Plans)</p>", unsafe_allow_html=True)
    if not SIPS_PLANNED:
        st.markdown(
            "<div class='insurance-card' style='text-align:center; padding:32px;'>"
            "<p style='color:#7A9BBF; font-size:11px; letter-spacing:2px; margin:0;'>NO ACTIVE SIPs YET</p>"
            "<p style='color:#EAE3D6; font-size:13px; margin:14px 0 6px 0; line-height:1.65;'>"
            "Coin account opens in the next <strong style='color:#C8A84B;'>1-2 weeks</strong>; first STP/SIP tranches scheduled <strong style='color:#C8A84B;'>Jun 2026</strong>. Direct-plan SIPs in "
            "<strong>Motilal Midcap</strong>, <strong>HDFC Mid-Cap Opp</strong>, <strong>Nippon Small Cap</strong>, and "
            "<strong>Bandhan Small Cap</strong> will populate here once the first auto-debit clears."
            "</p>"
            "<p style='color:#7A9BBF; font-size:10px; font-style:italic; margin:16px 0 0 0; line-height:1.5;'>"
            "Each SIP will track: installments completed · weighted-avg buy NAV · time-weighted return · days since first installment"
            "</p>"
            "</div>",
            unsafe_allow_html=True
        )

    # Segregation footer
    st.markdown("""
    <div style='background:rgba(200,168,75,0.08); border-left:3px solid #C8A84B; padding:14px 18px; border-radius:8px; margin-top:24px;'>
    <p style='color:#C8A84B; font-size:11px; letter-spacing:1.5px; margin:0 0 6px 0; font-weight:600;'>SEGREGATION</p>
    <p style='color:#EAE3D6; font-size:12px; margin:0; line-height:1.65;'>
    This view tracks <strong>only new investments made from 2026-05-11 onwards</strong>. Legacy holdings —
    existing Regular-plan MFs, older direct equity, FDs, gold — continue to live in the <strong style='color:#C8A84B;'>Portfolio</strong> tab from the master Google Sheet.
    Fresh SIPs on Coin from <strong>Jun 2026</strong> will be appended below.
    </p>
    </div>
    """, unsafe_allow_html=True)

elif tab == "Plan":
    plan_df = fetch_plan()
    cf = plan_df[plan_df['Section'] == 'Cashflow']

    # ── Hero summary ──
    st.markdown("<p style='font-size:20px; color:#C8A84B; font-weight:500; letter-spacing:0.5px; margin-bottom:4px;'>Strategic Plan · 5-Year Horizon</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#7A9BBF; font-size:12px; letter-spacing:1px; margin-bottom:24px;'>CASH FLOW MAP · TWO-PHASE ALLOCATION</p>", unsafe_allow_html=True)

    # ── Cash Flow ──
    st.markdown("<p style='font-size:14px; color:#C8A84B; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; margin:8px 0 12px 0;'>◈ Cash Flow Map (8 Months)</p>", unsafe_allow_html=True)
    cf_html = "<table class='static-table'><thead><tr><th>Month</th><th>Source</th><th>Inflow (₹L)</th><th>Notes</th></tr></thead><tbody>"
    for _, r in cf.iterrows():
        is_total = 'TOTAL' in str(r['Item'])
        bold = "font-weight:700; color:#E2CC8A;" if is_total else ""
        cf_html += f"<tr style='{bold}'><td>{r['Item']}</td><td>{r['Detail']}</td><td>{r['Amount (Rs L)']}</td><td>{r['Notes']}</td></tr>"
    cf_html += "</tbody></table>"
    st.markdown(cf_html, unsafe_allow_html=True)

    # ── Two-Phase Allocation ──
    st.markdown("<div class='section-divider'><span class='section-divider-mark'>◆ ◆ ◆</span></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:14px; color:#C8A84B; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; margin:8px 0 12px 0;'>◈ Two-Phase Allocation · Catch-up → De-risk</p>", unsafe_allow_html=True)

    PHASES = [
        {
            'tag':      'NOW · 2026-27',
            'title':    'Catch-up · Aggressive',
            'subtitle': 'Target: 14-15% pre-tax',
            'note':     'Mid/smallcap has been ~flat for 2 years. Front-load equity to ride the mean-reversion.',
            'rows': [
                ('Mid + Small Cap MF',     '50%', 'Mean-reversion bet · 2-yr flat → ~16-17%'),
                ('Flexi Cap MF',           '25%', 'Active anchor · ~13-14%'),
                ('Tactical Direct Equity', '10%', 'Energy + Pharma sectors · ~17-18%'),
                ('International',          '10%', 'US/Global feeder · ~12%'),
                ('Liquid Buffer',          '5%',  'Dry powder for dips · ~7%'),
            ]
        },
        {
            'tag':      'FROM 2027',
            'title':    'De-risk · Moderate',
            'subtitle': 'Target: 11-12% pre-tax',
            'note':     'After Y1 catch-up, lock in gains and rebuild downside cushion. Same engine, lower beta.',
            'rows': [
                ('Mid + Small Cap MF',     '35%', 'Trimmed from 50% · ~14%'),
                ('Flexi Cap MF',           '30%', 'Increased anchor · ~12%'),
                ('Large Cap Index',        '10%', 'NIFTYBEES + Junior · ~11%'),
                ('International',          '10%', 'Hold steady · ~12%'),
                ('Debt (Arbitrage+Bonds)', '15%', 'New cushion · ~7%'),
            ]
        }
    ]

    cols = st.columns(2)
    for col, phase in zip(cols, PHASES):
        body = "".join([
            f"<div style='display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #1C3050;'>"
            f"<span style='font-size:12px; color:#EAE3D6;'>{item}</span>"
            f"<span style='font-size:12px; color:#C8A84B; font-family:\"JetBrains Mono\"; font-weight:600;'>{detail}</span>"
            f"</div>"
            f"<p style='font-size:10px; color:#7A9BBF; margin:2px 0 8px 0; line-height:1.4;'>{note}</p>"
            for item, detail, note in phase['rows']
        ])
        with col:
            st.markdown(
                f"<div class='insurance-card' style='min-height:100%;'>"
                f"<p style='color:#7A9BBF; font-size:10px; letter-spacing:2px; margin:0;'>{phase['tag']}</p>"
                f"<h3 style='margin:4px 0 4px 0; font-size:16px; color:#C8A84B; font-weight:700;'>{phase['title']}</h3>"
                f"<p style='color:#E2CC8A; font-size:13px; font-family:\"JetBrains Mono\"; margin:0 0 8px 0;'>{phase['subtitle']}</p>"
                f"<p style='color:#7A9BBF; font-size:11px; margin:0 0 14px 0; line-height:1.5; font-style:italic;'>{phase['note']}</p>"
                f"{body}"
                f"</div>",
                unsafe_allow_html=True
            )

    # Transition mechanics note
    st.markdown("""
    <div style='background:rgba(200,168,75,0.08); border-left:3px solid #C8A84B; padding:14px 18px; border-radius:8px; margin-top:18px;'>
    <p style='color:#C8A84B; font-size:11px; letter-spacing:1.5px; margin:0 0 6px 0; font-weight:600;'>TRANSITION MECHANICS (END OF Y1)</p>
    <p style='color:#EAE3D6; font-size:12px; margin:0; line-height:1.6;'>
    Trim Mid/Small <strong>50% → 35%</strong> (-15%), exit Tactical Equity <strong>10% → 0%</strong>, drain Liquid <strong>5% → 0%</strong>.
    Redeploy 30% into: Flexi <strong>+5%</strong>, Large Cap Index <strong>+10%</strong>, Debt <strong>+15%</strong>.
    Holdings sold after May 2027 qualify for LTCG @ 14.95% — modest tax cost in exchange for downside cushion entering Y2.
    </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Footnote ──
    st.markdown("""
    <div style='background:rgba(200,168,75,0.08); border-left:3px solid #C8A84B; padding:14px 18px; border-radius:8px; margin-top:24px;'>
    <p style='color:#C8A84B; font-size:11px; letter-spacing:1.5px; margin:0 0 6px 0; font-weight:600;'>DEPLOYMENT NOTE</p>
    <p style='color:#EAE3D6; font-size:12px; margin:0; line-height:1.6;'>Lump-sum maturities (₹52L Dec FD) routed via <strong>STP over 12 months</strong>; monthly ₹5L surplus deployed as fresh SIP per the Phase 1 weights, transitioning to Phase 2 from Apr 2027. Existing ₹1L Aggressive (Top 3) SIP continues unchanged.</p>
    </div>
    """, unsafe_allow_html=True)

elif tab == "Protection":
    st.markdown("<p style='font-size:20px; color:#C8A84B; font-weight:500; letter-spacing:0.5px;'>Term Life Protection</p>", unsafe_allow_html=True)
    st.markdown("<div class='insurance-card' style='padding:28px;'><span class='insurance-icon'>◈</span><p style='color:#7A9BBF; font-size:11px; letter-spacing:1.5px; text-transform:uppercase; margin:0 0 6px 0;'>Sum Insured</p><h2 style='margin:0; font-size:32px; background: linear-gradient(90deg, #C8A84B, #E2CC8A); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight:700;'>₹1.00 Crore</h2><p style='color:#C8A84B; font-size:11px; margin-top:8px; letter-spacing:0.5px;'>Primary Policy · Nominee: Ritu Narang</p></div>", unsafe_allow_html=True)
    st.markdown("<br><p style='font-size:20px; color:#C8A84B; font-weight:500; letter-spacing:0.5px;'>Family Health Shield</p>", unsafe_allow_html=True)
    h1, h2 = st.columns(2)
    with h1: st.markdown("<div class='insurance-card'><span class='insurance-icon'>✦</span><p style='color:#7A9BBF; font-size:11px; letter-spacing:1px; text-transform:uppercase; margin:0 0 4px 0;'>Star Comprehensive</p><p style='font-size:20px; margin:0; font-weight:600; font-family:\"JetBrains Mono\", monospace; color:#EAE3D6;'>₹20.0 L</p></div>", unsafe_allow_html=True)
    with h2: st.markdown("<div class='insurance-card'><span class='insurance-icon'>✦</span><p style='color:#7A9BBF; font-size:11px; letter-spacing:1px; text-transform:uppercase; margin:0 0 4px 0;'>Niva Bupa ReAssure 2.0</p><p style='font-size:20px; margin:0; font-weight:600; font-family:\"JetBrains Mono\", monospace; color:#EAE3D6;'>₹10.0 L</p></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:rgba(200,168,75,0.08); border-left:3px solid #C8A84B; padding:16px 20px; border-radius:8px; margin-top:24px;'>
    <p style='color:#C8A84B; font-size:11px; letter-spacing:1.5px; margin:0 0 8px 0; font-weight:600;'>ADVISORY NOTE</p>
    <p style='color:#EAE3D6; font-size:13px; margin:0; line-height:1.6;'>Current health cover stands at <strong>₹30 L</strong>; recommended total exposure is closer to <strong>₹1 Crore</strong>. We recommend adding a <strong>₹30 L HDFC ERGO Optima Secure</strong> policy, which provides <strong>₹60 L effective cover from Day 1<sup style='color:#C8A84B;'>*</sup></strong>.</p>
    <p style='color:#7A9BBF; font-size:10px; margin:10px 0 0 0; font-style:italic;'>* Day-1 enhanced cover feature to be verified with the HDFC ERGO agent.</p>
    </div>
    """, unsafe_allow_html=True)

elif tab == "Actions":
    st.markdown("<p style='font-size:20px; color:#C8A84B; font-weight:500; letter-spacing:0.5px;'>Strategic Actions</p>", unsafe_allow_html=True)
    actions = [
        ("Monthly Wealth Infusion", "SIP auto-debits begin on the 25th. ₹6 L flows systematically across allocations; ₹1 L into MON100 will be manually deployed by Vikram Batra to avoid poor entry rates.", "Vikram Batra"),
        ("FD Tax Efficiency", "₹75 L in fixed deposits will be rolled into arbitrage funds as each matures, to improve post-tax yield.", "Vikram Batra"),
        ("Legacy Exit Strategy", "Phase out of Satellite MFs over the next 5 years in a tax-efficient manner.", "Vikram Batra"),
        ("Tactical Equity Allocation", "Select names in the Energy & Pharma sectors appear technically strong. Seeking client approval for ₹10–15 L direct equity deployment across these sectors.", "Vikram Batra"),
        ("Health Cover Expansion", "Obtain quotes and initiate an additional ₹30 L base HDFC ERGO Optima Secure policy.", "CM Narang"),
    ]
    for i, (act, desc, owner) in enumerate(actions, 1):
        st.markdown(
            f"<div class='action-card'>"
            f"<div style='display:flex; justify-content:space-between; align-items:flex-start;'>"
            f"<div style='display:flex; align-items:center; flex:1;'>"
            f"<span class='action-number'>{i}</span>"
            f"<span style='color:#C8A84B; font-weight:600; font-size:15px; letter-spacing:0.3px;'>{act}</span>"
            f"</div>"
            f"<span style='color:#7A9BBF; font-size:10px; letter-spacing:1.2px; text-transform:uppercase; padding-top:8px; white-space:nowrap;'>{owner}</span>"
            f"</div>"
            f"<p style='font-size:13px; color:#EAE3D6; margin:10px 0 0 42px; line-height:1.65;'>{desc}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
