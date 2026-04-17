import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection
import base64
from pathlib import Path

# ── 0. LOGO (Quantis Capital brand mark) ──────────────────────────────────────
@st.cache_data
def _logo_b64():
    p = Path(__file__).parent / "assets" / "quantis_icon.png"
    return base64.b64encode(p.read_bytes()).decode()

def logo_lockup(icon_px=40, text_px=11, gap=12, align="left"):
    b64 = _logo_b64()
    text_align = "left" if align == "left" else "center"
    return (
        f"<div style='display:inline-flex; align-items:center; gap:{gap}px; text-align:{text_align};'>"
        f"<img src='data:image/png;base64,{b64}' style='height:{icon_px}px; width:auto; "
        f"filter: drop-shadow(0 0 10px rgba(200,168,75,0.18));'/>"
        f"<div style='line-height:1.2;'>"
        f"<div style='font-weight:700; font-size:{text_px}px; letter-spacing:4px; "
        f"background: linear-gradient(90deg, #C8A84B, #E2CC8A); "
        f"-webkit-background-clip: text; -webkit-text-fill-color: transparent;'>QUANTIS</div>"
        f"<div style='color:#7A9BBF; font-size:{max(8, text_px-2)}px; letter-spacing:5px; margin-top:1px;'>CAPITAL</div>"
        f"</div>"
        f"</div>"
    )

# ── 1. PAGE CONFIGURATION ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wealth Dashboard · CM Narang",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
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
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=3600) 
def fetch_data():
    df = conn.read(spreadsheet=URL)
    if 'Current Value' in df.columns:
        df['Val_Num'] = pd.to_numeric(df['Current Value'].astype(str).replace('[₹,L,Cr, ,]', '', regex=True), errors='coerce').fillna(0)
    assets = df[~df['Asset Name'].str.contains('Total|TOTAL|Sum|Subtotal', na=False)]
    return assets.dropna(subset=['Asset Name'])

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
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.write("##")
    st.write("##")
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown(
            f"<div class='login-card'>"
            f"<div style='display:flex; justify-content:center; margin-bottom:18px;'>{logo_lockup(icon_px=56, text_px=14, gap=14)}</div>"
            f"<p style='color:#C8A84B; font-size:11px; letter-spacing:3px; margin:0 0 4px 0; font-weight:600;'>PRIVATE WEALTH</p>"
            f"<p style='color:#7A9BBF; font-size:11px; letter-spacing:2px; margin-bottom:30px;'>CHANDRA MOHAN NARANG</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
        u = st.text_input("Username", placeholder="Identity")
        p = st.text_input("Password", type="password", placeholder="Secret Key")
        if st.button("AUTHENTICATE & ACCESS"):
            if u == "cm.narang" and p == "Narang@2026":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
    st.stop()

# ── 7. HEADER ─────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([2, 1])
with col_h1:
    st.markdown(
        f"<div style='display:flex; align-items:center; gap:16px;'>"
        f"<img src='data:image/png;base64,{_logo_b64()}' style='height:48px; width:auto; "
        f"filter: drop-shadow(0 0 10px rgba(200,168,75,0.2));'/>"
        f"<div>"
        f"<div style='color:#C8A84B; font-size:10px; letter-spacing:4px; font-weight:700; margin-bottom:2px;'>QUANTIS CAPITAL</div>"
        f"<h1 style='background: linear-gradient(90deg, #C8A84B, #E2CC8A); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; font-size: 34px; margin:0; padding:0; line-height:1.1;'>Chandra Mohan Narang</h1>"
        f"<p style='color: #7A9BBF; font-size: 11px; text-transform: uppercase; letter-spacing: 2.5px; margin: 2px 0 0 0;'>Family Office Dashboard</p>"
        f"<div class='header-accent'></div>"
        f"</div></div>",
        unsafe_allow_html=True,
    )
with col_h2:
    st.markdown(f"<div style='text-align: right; padding-top: 18px;'><p style='color: #5C7089; font-size: 10px; letter-spacing: 2px; margin-bottom: 2px;'>VALUATION DATE</p><p style='color: #EAE3D6; font-size: 14px; font-weight: 500; font-family: \"JetBrains Mono\", monospace;'>{pd.Timestamp.now().strftime('%d %B, %Y')}</p></div>", unsafe_allow_html=True)

st.markdown("<hr style='margin: 12px 0 18px 0; border: 0; border-top: 1px solid #1C3050;'>", unsafe_allow_html=True)
tab = st.radio("nav", ["Overview", "Portfolio", "Protection", "Actions"], horizontal=True, label_visibility="collapsed")

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
    st.markdown("<p style='font-size:20px; color:#C8A84B; font-weight:500; letter-spacing:0.5px;'>Detailed Holding Inventory</p>", unsafe_allow_html=True)
    disp = assets_df[['Asset Name', 'Category', 'Units / Qty', 'Current Value', 'Val_Num']].copy()
    disp = disp.sort_values(by='Val_Num', ascending=False) 
    disp['Alloc %'] = (disp['Val_Num'] / total_nw * 100).round(1).astype(str) + '%'
    html = "<table class='static-table'><thead><tr><th>Asset Name</th><th>Category</th><th>Qty</th><th>Value</th><th>Alloc %</th></tr></thead><tbody>"
    for _, r in disp.iterrows():
        html += f"<tr><td>{r['Asset Name']}</td><td>{r['Category']}</td><td>{r['Units / Qty']}</td><td>{fmt_l(r['Val_Num'])}</td><td>{r['Alloc %']}</td></tr>"
    st.markdown(html + "</tbody></table>", unsafe_allow_html=True)

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
