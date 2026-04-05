import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wealth Dashboard · CM Narang",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── ROYAL UI STYLING ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #07101F; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.block-container { padding: 1.5rem 2rem 4rem 2rem; max-width: 1100px; }
.stApp { background-color: #07101F !important; }
p, div, span, label { color: #EAE3D6; }

.gold-text {
    background: linear-gradient(to bottom, #C8A84B 0%, #E2CC8A 50%, #B38F36 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700; font-size: 72px !important; letter-spacing: -2px; line-height: 1.1;
}

div[role="radiogroup"] label {
    background: #0C1A2E !important; border: 1px solid #1C3050 !important;
    border-radius: 12px !important; padding: 10px 24px !important; color: #5C7089 !important;
}
div[role="radiogroup"] label:has(input:checked) {
    background: rgba(200,168,75,0.12) !important; border-color: #C8A84B !important; color: #C8A84B !important;
}

.static-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
.static-table th { background: #0C1A2E; color: #C8A84B; text-align: left; padding: 15px; font-size: 12px; text-transform: uppercase; border-bottom: 2px solid #1C3050; }
.static-table td { padding: 15px; border-bottom: 1px solid #1C3050; font-size: 14px; color: #EAE3D6; }
</style>
""", unsafe_allow_html=True)

# ── HELPERS ──────────────────────────────────────────────────────────────────
def fmt_cr(n): return f"₹{n/1e7:.2f} Cr"
def fmt_l(n):  return f"₹{n/1e5:.1f} L"

# ── LIVE DATA CONNECTION ─────────────────────────────────────────────────────
URL = "https://docs.google.com/spreadsheets/d/1PZACfddE3VkcCWqYD-_0j_ERaBUT1SBQqPN63Vylvy0/export?format=csv"
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60) 
def fetch_data():
    df = conn.read(spreadsheet=URL)
    if 'Current Value' in df.columns:
        df['Val_Num'] = pd.to_numeric(df['Current Value'].astype(str).replace('[₹,L,Cr, ,]', '', regex=True), errors='coerce').fillna(0)
    return df.dropna(subset=['Asset Name'])

try:
    data_df = fetch_data()
    
    # ANTI-DOUBLE COUNTING LOGIC:
    # We only count rows that DO NOT have the word "Total" in the Asset Name.
    active_assets = data_df[~data_df['Asset Name'].str.contains('Total|TOTAL|Sum', na=False)]
    # Also ignore rows where Current Value is 0
    active_assets = active_assets[active_assets['Val_Num'] > 0]
    
    total_nw = active_assets['Val_Num'].sum()
    
    # Categorization
    mf_v = active_assets[active_assets['Category'].str.contains('Aggressive|Stable|Legacy', na=False)]['Val_Num'].sum()
    etf_v = active_assets[active_assets['Category'].str.contains('New Core|New Global|New Stability', na=False)]['Val_Num'].sum()
    gold_v = active_assets[active_assets['Category'].str.contains('Commodities', na=False)]['Val_Num'].sum()
    fd_v = active_assets[active_assets['Category'].str.contains('Fixed Income', na=False)]['Val_Num'].sum()
    cash_v = active_assets[active_assets['Category'].str.contains('Liquid', na=False)]['Val_Num'].sum()

    OVERVIEW_MAP = {"Mutual Funds": mf_v, "ETFs": etf_v, "Gold": gold_v, "Fixed Deposits": fd_v, "Cash": cash_v}
except:
    st.stop()

# ── LOGIN ─────────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div style='text-align:center; padding:60px 0;'><h2 style='color:#C8A84B;'>◈ PRIVATE WEALTH</h2><p style='color:#7A9BBF;'>CHANDRA MOHAN NARANG</p></div>", unsafe_allow_html=True)
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Sign In", use_container_width=True):
            if u == "cm.narang" and p == "Narang@2026":
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# ── MAIN UI ──────────────────────────────────────────────────────────────────
st.markdown(f"<div style='font-size:22px; font-weight:500;'>Chandra Mohan Narang</div><p style='font-size:11px; color:#7A9BBF; margin-top:-15px;'>FAMILY OFFICE DASHBOARD</p>", unsafe_allow_html=True)
tab = st.radio("nav", ["Overview", "Portfolio", "Protection", "Actions"], horizontal=True, label_visibility="collapsed")

# ── TAB 1: OVERVIEW ───────────────────────────────────────────────────────────
if tab == "Overview":
    st.markdown(f"<div style='background:#0C1A2E; border:1px solid #1C3050; border-radius:24px; padding:50px; text-align:center; margin-bottom:30px;'><p style='font-size:12px; color:#7A9BBF; text-transform:uppercase; letter-spacing:3px;'>Consolidated Net Worth</p><h1 class='gold-text'>{fmt_cr(total_nw)}</h1></div>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        fig = go.Figure(go.Pie(labels=list(OVERVIEW_MAP.keys()), values=list(OVERVIEW_MAP.values()), hole=0.7, marker=dict(colors=['#52A2FF','#57C785','#E2CC8A','#46C1C1','#A37CFF'])))
        fig.update_layout(showlegend=False, height=350, paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("<p style='font-size:12px; color:#C8A84B; font-weight:600; letter-spacing:1px; margin-bottom:20px;'>ALLOCATION SUMMARY</p>", unsafe_allow_html=True)
        for l, v in OVERVIEW_MAP.items():
            if v > 0: st.markdown(f"<div style='display:flex; justify-content:space-between; margin-bottom:18px; border-bottom:1px solid #1C3050; padding-bottom:6px;'><span>{l}</span><span style='font-family:\"DM Mono\";'>{fmt_l(v)}</span></div>", unsafe_allow_html=True)

# ── TAB 2: PORTFOLIO ──────────────────────────────────────────────────────────
elif tab == "Portfolio":
    st.markdown("<p style='font-size:20px; color:#C8A84B; font-weight:500;'>Detailed Holding Inventory</p>", unsafe_allow_html=True)
    disp = active_assets[['Asset Name', 'Category', 'Units / Qty', 'Current Value', 'Val_Num']].copy()
    disp['Alloc %'] = (disp['Val_Num'] / total_nw * 100).round(1).astype(str) + '%'
    html = "<table class='static-table'><thead><tr><th>Asset Name</th><th>Category</th><th>Units / Qty</th><th>Value</th><th>Alloc %</th></tr></thead><tbody>"
    for _, r in disp.iterrows():
        html += f"<tr><td>{r['Asset Name']}</td><td>{r['Category']}</td><td>{r['Units / Qty']}</td><td>{fmt_l(r['Val_Num'])}</td><td>{r['Alloc %']}</td></tr>"
    st.markdown(html + "</tbody></table>", unsafe_allow_html=True)

# ── TAB 3: PROTECTION ─────────────────────────────────────────────────────────
elif tab == "Protection":
    st.markdown("<p style='font-size:20px; color:#C8A84B; font-weight:500;'>Insurance & Protection</p>", unsafe_allow_html=True)
    cols = st.columns(3)
    data = [("Term Life Cover", "₹5.0 Cr", "HDFC Life · Active"), ("Health Floater", "₹25.0 L", "Niva Bupa · Active"), ("Critical Illness", "₹50.0 L", "ICICI Lombard · Active")]
    for i, (title, val, co) in enumerate(data):
        with cols[i]:
            st.markdown(f"<div style='background:#0C1A2E; padding:25px; border-radius:15px; border:1px solid #1C3050;'><p style='color:#7A9BBF; font-size:12px;'>{title}</p><h2 style='margin:0;'>{val}</h2><p style='color:#C8A84B; font-size:11px;'>{co}</p></div>", unsafe_allow_html=True)
    st.markdown("<br><div style='background:rgba(82,162,255,0.05); padding:20px; border-radius:15px; border:1px solid #52A2FF30;'><p style='color:#52A2FF; font-weight:600;'>◈ Nominee Verification</p><p style='font-size:14px; color:#EAE3D6;'>All policies and investment folios are verified with <b>Shubha Jain</b> as 100% Nominee.</p></div>", unsafe_allow_html=True)

# ── TAB 4: ACTIONS ────────────────────────────────────────────────────────────
elif tab == "Actions":
    st.markdown("<p style='font-size:20px; color:#C8A84B; font-weight:500;'>Strategic Actions</p>", unsafe_allow_html=True)
    actions = [
        ("Monthly SIP Execution", "₹7.0 L auto-debit scheduled for the 25th.", "Vikram Batra"),
        ("Legacy Fund Exit", "Phased redemption of 'Legacy (Exit)' funds into NiftyBees.", "Vikram Batra"),
        ("Quarterly Rebalancing", "Review asset weightage vs target allocation in July.", "CM Narang"),
        ("Tax Efficiency", "Harvesting ₹1.25L LTCG before April 30th.", "Vikram Batra")
    ]
    for act, desc, owner in actions:
        st.markdown(f"<div style='padding:20px; border-bottom:1px solid #1C3050;'><div style='display:flex; justify-content:space-between;'><span style='color:#C8A84B; font-weight:600;'>{act}</span><span style='color:#7A9BBF; font-size:11px;'>{owner}</span></div><p style='font-size:13px; color:#EAE3D6; margin-top:5px;'>{desc}</p></div>", unsafe_allow_html=True)
