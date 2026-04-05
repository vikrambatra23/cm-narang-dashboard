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

/* The Royal Gold Header */
.gold-text {
    background: linear-gradient(to bottom, #C8A84B 0%, #E2CC8A 50%, #B38F36 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700; font-size: 72px !important; letter-spacing: -2px; line-height: 1;
}

/* Tab Radio Styling */
div[role="radiogroup"] { gap: 1rem; }
div[role="radiogroup"] label {
    background: #0C1A2E !important; border: 1px solid #1C3050 !important;
    border-radius: 12px !important; padding: 10px 24px !important; 
    color: #5C7089 !important; transition: 0.3s;
}
div[role="radiogroup"] label:has(input:checked) {
    background: rgba(200,168,75,0.12) !important; border-color: #C8A84B !important; color: #C8A84B !important;
    box-shadow: 0 0 15px rgba(200,168,75,0.1);
}

/* Remove Table Scroll & Match Design */
.stDataFrame { border: 1px solid #1C3050 !important; border-radius: 12px !important; }
[data-testid="stTable"] { background-color: transparent !important; }

/* Table Heading Contrast */
thead tr th { background-color: #0C1A2E !important; color: #C8A84B !important; font-size: 12px !important; text-transform: uppercase; }
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
    # CLEANING: Remove currency symbols and commas so Python can do MATH
    if 'Current Value' in df.columns:
        df['Current Value'] = df['Current Value'].replace('[₹,L,Cr, ]', '', regex=True)
        df['Current Value'] = pd.to_numeric(df['Current Value'], errors='coerce').fillna(0)
    return df.dropna(subset=['Asset Name'])

try:
    data_df = fetch_data()
    total_nw = data_df['Current Value'].sum()
    
    # Precise Calculation Logic
    mf_total = data_df[data_df['Category'].str.contains('Aggressive|Stable|Legacy', na=False)]['Current Value'].sum()
    etf_total = data_df[data_df['Category'].str.contains('New Core|New Global|New Stability', na=False)]['Current Value'].sum()
    gold_total = data_df[data_df['Category'] == 'Commodities']['Current Value'].sum()
    fd_total = data_df[data_df['Category'] == 'Fixed Income']['Current Value'].sum()
    cash_total = data_df[data_df['Category'] == 'Liquid']['Current Value'].sum()

    OVERVIEW_MAP = {
        "Mutual Funds (Total)": mf_total,
        "ETFs & New Assets": etf_total,
        "Physical Gold": gold_total,
        "Fixed Deposits": fd_total,
        "Cash Buffer": cash_total
    }
except Exception as e:
    st.error(f"Sync Error: {e}")
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
st.markdown(f"<div style='font-size:22px; font-weight:500;'>Chandra Mohan Narang</div><p style='font-size:11px; color:#7A9BBF; margin-top:-15px;'>CONSOLIDATED FAMILY WEALTH DASHBOARD</p>", unsafe_allow_html=True)
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
                st.markdown(f"<div style='display:flex; justify-content:space-between; margin-bottom:18px; border-bottom:1px solid #1C3050; padding-bottom:6px;'><span>{label}</span><span style='font-family:\"DM Mono\"; font-weight:500;'>{fmt_l(val)}</span></div>", unsafe_allow_html=True)

# ── TAB 2: PORTFOLIO ──────────────────────────────────────────────────────────
elif tab == "Portfolio":
    st.markdown("<p style='font-size:20px; color:#C8A84B; font-weight:500; margin-bottom:20px;'>Detailed Holding Inventory</p>", unsafe_allow_html=True)
    
    # Create display version of the table
    disp = data_df[['Asset Name', 'Category', 'Units / Qty', 'Current Value']].copy()
    disp['Allocation %'] = (disp['Current Value'] / total_nw * 100).round(1).astype(str) + '%'
    disp['Current Value'] = disp['Current Value'].apply(fmt_l)
    
    # Use st.table instead of st.dataframe to REMOVE the scrollbar and show full list
    st.table(disp)

# ── TABS 3 & 4 ───────────────────────────────────────────────────────────────
else:
    st.info("Module active and syncing with Google Sheets...")
