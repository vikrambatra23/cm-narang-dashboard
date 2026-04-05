import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #050A14; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.block-container { padding: 1.5rem 2rem 4rem 2rem; max-width: 1100px; }
.stApp { background-color: #050A14 !important; }
p, div, span, label { color: #EAE3D6; }

/* The Speedometer Gold Number */
.gold-text {
    background: linear-gradient(to bottom, #C8A84B 0%, #E2CC8A 50%, #B38F36 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700; font-size: 72px !important; letter-spacing: -2px; line-height: 1.1;
}

/* Tab Radio Styling */
div[role="radiogroup"] label {
    background: #0C1A2E !important; border: 1px solid #1C3050 !important;
    border-radius: 12px !important; padding: 10px 24px !important; color: #5C7089 !important;
}
div[role="radiogroup"] label:has(input:checked) {
    background: rgba(200,168,75,0.12) !important; border-color: #C8A84B !important; color: #C8A84B !important;
}

/* Static Table Styling - Full Page (No Internal Scroll) */
.static-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
.static-table th { background: #0C1A2E; color: #C8A84B; text-align: left; padding: 15px; font-size: 11px; text-transform: uppercase; border-bottom: 2px solid #1C3050; }
.static-table td { padding: 15px; border-bottom: 1px solid #1C3050; font-size: 13px; color: #EAE3D6; }
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
        # Scrub currency symbols and cast to number
        df['Val_Num'] = pd.to_numeric(df['Current Value'].astype(str).replace('[₹,L,Cr, ,]', '', regex=True), errors='coerce').fillna(0)
    # Ignore "Total" rows from the sheet to prevent double-counting
    assets = df[~df['Asset Name'].str.contains('Total|TOTAL|Sum|Subtotal', na=False)]
    return assets.dropna(subset=['Asset Name'])

try:
    assets_df = fetch_data()
    # Net Worth calculation (Ignores subtotals)
    total_nw = assets_df['Val_Num'].sum()
    
    # Category Math for Pie Chart
    mf_v = assets_df[assets_df['Category'].str.contains('Aggressive|Stable|Legacy', na=False)]['Val_Num'].sum()
    etf_v = assets_df[assets_df['Category'].str.contains('New Core|New Global|New Stability', na=False)]['Val_Num'].sum()
    gold_v = assets_df[assets_df['Category'].str.contains('Commodities', na=False)]['Val_Num'].sum()
    fd_v = assets_df[assets_df['Category'].str.contains('Fixed Income', na=False)]['Val_Num'].sum()
    cash_v = assets_df[assets_df['Category'].str.contains('Liquid', na=False)]['Val_Num'].sum()

    OVERVIEW_MAP = {"Mutual Funds": mf_v, "ETFs": etf_v, "Gold": gold_v, "Fixed Income": fd_v, "Cash": cash_v}
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
            if u == "cm.admin" and p == "Narang@2026":
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# ── HEADER SECTION ────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([2, 1])
with col_h1:
    st.markdown("<h1 style='background: linear-gradient(90deg, #C8A84B, #E2CC8A); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; font-size: 38px; margin-bottom: 0px;'>Chandra Mohan Narang</h1><p style='color: #7A9BBF; font-size: 11px; text-transform: uppercase; letter-spacing: 2px; margin-top: -5px;'>Family Office Dashboard</p>", unsafe_allow_html=True)
with col_h2:
    st.markdown(f"<div style='text-align: right; padding-top: 20px;'><p style='color: #5C7089; font-size: 10px; margin-bottom: 0;'>VALUATION DATE</p><p style='color: #EAE3D6; font-size: 14px; font-weight: 500;'>{pd.Timestamp.now().strftime('%d %B, %Y')}</p></div>", unsafe_allow_html=True)

st.markdown("<hr style='margin: 5px 0 15px 0; border: 1px solid #1C3050;'>", unsafe_allow_html=True)
tab = st.radio("nav", ["Overview", "Portfolio", "Protection", "Actions"], horizontal=True, label_visibility="collapsed")

# ── TAB 1: OVER
