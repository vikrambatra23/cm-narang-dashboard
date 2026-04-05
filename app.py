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

/* Custom Table Styling to remove internal scroll */
.static-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
.static-table th { background: #0C1A2E; color: #C8A84B; text-align: left; padding: 12px; font-size: 12px; text-transform: uppercase; border-bottom: 2px solid #1C3050; }
.static-table td { padding: 12px; border-bottom: 1px solid #1C3050; font-size: 14px; color: #EAE3D6; }
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
    # Clean the 'Current Value' column to ensure it is purely numeric
    if 'Current Value' in df.columns:
        df['Current Value'] = df['Current Value'].astype(str).replace('[₹,L,Cr, ]', '', regex=True)
        df['Current Value'] = pd.to_numeric(df['Current Value'], errors='coerce').fillna(0)
    return df.dropna(subset=['Asset Name'])

try:
    data_df = fetch_data()
    # Filter out rows that are zero or headers to get the TRUE total
    active_assets = data_df[data_df['Current Value'] > 0]
    total_nw = active_assets['Current Value'].sum()
    
    # Categorization Logic
    mf_total = active_assets[active_assets['Category'].str.contains('Aggressive|Stable|Legacy', na=False)]['Current Value'].sum()
    etf_total = active_assets[active_assets['Category'].str.contains('New Core|New Global|New Stability', na=False)]['Current Value'].sum()
    gold_total = active_assets[active_assets['Category'].str.contains('Commodities', na=False)]['Current Value'].sum()
    fd_total = active_assets[active_assets['Category'].str.contains('Fixed Income', na=False)]['Current Value'].sum()
    cash_total = active_assets[active_assets['Category'].str.contains('Liquid', na=False)]['Current Value'].sum()

    OVERVIEW_MAP = {
        "Mutual Funds": mf_total,
        "ETFs & New Equity": etf_total,
        "Physical Gold": gold_total,
        "Fixed Deposits": fd_total,
        "Cash Buffer": cash_total
    }
except:
    st.stop()

# ── LOGIN ─────────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div style='text-align:center; padding:60px 0;'><h2 style='color:#C8A84B;'>◈ PRIVATE WEALTH</h2><p style='color:#7A9BBF;'>CHANDRA MOHAN NARANG</p></div>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
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
    st.markdown(f"""
    <div style='background: #0C1A2E; border: 1px solid #1C3050; border-radius: 24px; padding: 50px; text-align: center; margin-bottom: 30px;'>
        <p style='font-size: 12px; color: #7A9BBF; text-transform: uppercase; letter-spacing: 3px;'>Consolidated Net Worth</p>
        <h1 class='gold-text'>{fmt_cr(total_nw)}</h1>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        fig = go.Figure(go.Pie(labels=list(OVERVIEW_MAP.keys()), values=list(OVERVIEW_MAP.values()), hole=0.7,
                               marker=dict(colors=['#52A2FF','#57C785','#E2CC8A','#46C1C1','#A37CFF'])))
        fig.update_layout(showlegend=False, height=350, paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("<p style='font-size:12px; color:#C8A84B; font-weight:600; letter-spacing:1px; margin-bottom:20px;'>ALLOCATION SUMMARY</p>", unsafe_allow_html=True)
        for label, val in OVERVIEW_MAP.items():
            if val > 0:
                st.markdown(f"<div style='display:flex; justify-content:space-between; margin-bottom:18px; border-bottom:1px solid #1C3050; padding-bottom:6px;'><span>{label}</span><span style='font-family:\"DM Mono\";'>{fmt_l(val)}</span></div>", unsafe_allow_html=True)

# ── TAB 2: PORTFOLIO ──────────────────────────────────────────────────────────
elif tab == "Portfolio":
    st.markdown("<p style='font-size:20px; color:#C8A84B; font-weight:500;'>Detailed Holding Inventory</p>", unsafe_allow_html=True)
    disp = active_assets[['Asset Name', 'Category', 'Units / Qty', 'Current Value']].copy()
    disp['Allocation %'] = (disp['Current Value'] / total_nw * 100).round(1).astype(str) + '%'
    disp['Current Value'] = disp['Current Value'].apply(fmt_l)
    
    # Render as a static HTML table to avoid internal scrollbars
    html = "<table class='static-table'><thead><tr>"
    for col in disp.columns: html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"
    for _, row in disp.iterrows():
        html += "<tr>" + "".join([f"<td>{val}</td>" for val in row]) + "</tr>"
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)

# ── TAB 3: PROTECTION (RESTORED) ──────────────────────────────────────────────
elif tab == "Protection":
    st.markdown("<p style='font-size:20px; color:#C8A84B; font-weight:500;'>Insurance & Safety Net</p>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Term Life Cover", "₹5.00 Cr", "Active")
    with c2:
        st.metric("Health (Family Floater)", "₹25.0 L", "Active")
    with c3:
        st.metric("Critical Illness", "₹50.0 L", "Active")
    
    st.markdown("""
    <div style='background:#0C1A2E; padding:20px; border-radius:15px; margin-top:20px; border:1px solid #1C3050;'>
        <p style='color:#C8A84B; font-weight:600;'>Primary Nominee Status</p>
        <p style='font-size:14px; color:#7A9BBF;'>All policies updated with Shubha Jain (Wife) as 100% Nominee.</p>
    </div>
    """, unsafe_allow_html=True)

# ── TAB 4: ACTIONS (RESTORED) ─────────────────────────────────────────────────
elif tab == "Actions":
    st.markdown("<p style='font-size:20px; color:#C8A84B; font-weight:500;'>Pending Tasks (Vikram Batra)</p>", unsafe_allow_html=True)
    tasks = [
        ("Monthly SIP Execution", "Scheduled for 25th"),
        ("Quarterly Rebalancing", "Pending June 2026"),
        ("Annual Tax Filing", "In Progress"),
        ("Physical Gold Audit", "Completed Mar 2026")
    ]
    for t, status in tasks:
        st.markdown(f"<div style='display:flex; justify-content:space-between; padding:15px; border-bottom:1px solid #1C3050;'><span>{t}</span><span style='color:#C8A84B;'>{status}</span></div>", unsafe_allow_html=True)
