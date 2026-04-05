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
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.block-container { padding: 1.5rem 2rem 4rem 2rem; max-width: 1000px; }
.stApp { background-color: #07101F !important; }
[data-testid="stAppViewContainer"] { background-color: #07101F !important; }
p, div, span, label { color: #EAE3D6; }
.gold-text {
    background: linear-gradient(to bottom, #C8A84B 0%, #E2CC8A 50%, #B38F36 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700; font-size: 64px !important; letter-spacing: -1px;
}
div[role="radiogroup"] label {
    background: #0C1A2E !important; border: 1px solid #1C3050 !important;
    border-radius: 10px !important; padding: 8px 18px !important; color: #5C7089 !important;
}
div[role="radiogroup"] label:has(input:checked) {
    background: rgba(200,168,75,0.12) !important; border-color: #C8A84B !important; color: #C8A84B !important;
}
</style>
""", unsafe_allow_html=True)

# ── HELPERS ──────────────────────────────────────────────────────────────────
def fmt_cr(n): return f"₹{n/1e7:.2f} Cr"
def fmt_l(n):  return f"₹{n/1e5:.1f} L"

# ── LIVE DATA CONNECTION ─────────────────────────────────────────────────────
# Using the CLEAN URL to avoid '400 Bad Request' errors
URL = "https://docs.google.com/spreadsheets/d/1PZACfddE3VkcCWqYD-_0j_ERaBUT1SBQqPN63Vylvy0/export?format=csv"
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=300) 
def fetch_data():
    # Make sure the tab name in your Google Sheet is exactly "Portfolio"
    df = conn.read(spreadsheet=URL, worksheet="Portfolio")
    return df.dropna(subset=['Asset Name'])

try:
    data_df = fetch_data()
    # Ensure numeric types for calculations
    data_df['Current Value'] = pd.to_numeric(data_df['Current Value'], errors='coerce').fillna(0)
    total_nw = data_df['Current Value'].sum()
    
    # Overview Logic: Grouping categories as requested
    mf_val = data_df[data_df['Category'].str.contains('Aggressive|Stable|Legacy', na=False)]['Current Value'].sum()
    etf_val = data_df[data_df['Category'].str.contains('New Core|New Global', na=False)]['Current Value'].sum()
    gold_val = data_df[data_df['Category'].str.contains('Commodities', na=False)]['Current Value'].sum()
    fd_val = data_df[data_df['Category'].str.contains('Fixed Income', na=False)]['Current Value'].sum()
    cash_val = data_df[data_df['Category'].str.contains('Liquid', na=False)]['Current Value'].sum()

    OVERVIEW_MAP = {
        "Mutual Funds (Total)": mf_val,
        "ETFs (Equity)": etf_val,
        "Physical Gold": gold_val,
        "Fixed Deposits": fd_val,
        "Cash Buffer": cash_val
    }
except Exception as e:
    st.error(f"Error connecting to Sheet: {e}")
    st.stop()

# ── LOGIN ─────────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown("<div style='text-align:center; padding:50px 0;'><h2 style='color:#C8A84B;'>◈ PRIVATE WEALTH</h2><p style='font-size:12px; color:#7A9BBF;'>CHANDRA MOHAN NARANG</p></div>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Sign In", use_container_width=True):
            if u == "cm.narang" and p == "Narang@2026":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
    st.stop()

# ── MAIN UI ──────────────────────────────────────────────────────────────────
st.markdown(f"<div style='font-size:20px; font-weight:500; margin-bottom:5px;'>Chandra Mohan Narang</div><p style='font-size:10px; color:#7A9BBF;'>VALUATION AS OF {pd.Timestamp.now().strftime('%d %B, %Y')}</p>", unsafe_allow_html=True)
tab = st.radio("nav", ["Overview", "Portfolio", "Protection", "Actions"], horizontal=True, label_visibility="collapsed")

# ── TAB 1: OVERVIEW ───────────────────────────────────────────────────────────
if tab == "Overview":
    st.markdown(f"""
    <div style='background: linear-gradient(145deg, #0C1A2E, #112338); border: 1px solid #C8A84B40; border-radius: 20px; padding: 35px; text-align: center; margin-bottom: 25px;'>
        <p style='font-size: 11px; color: #7A9BBF; text-transform: uppercase; letter-spacing: 2px;'>Consolidated Net Worth</p>
        <h1 class='gold-text'>{fmt_cr(total_nw)}</h1>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        fig = go.Figure(go.Pie(labels=list(OVERVIEW_MAP.keys()), values=list(OVERVIEW_MAP.values()), hole=0.6,
                               marker=dict(colors=['#52A2FF','#57C785','#E2CC8A','#46C1C1','#A37CFF'])))
        fig.update_layout(showlegend=False, height=300, paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("<p style='font-size:11px; color:#C8A84B; font-weight:600; letter-spacing:1px;'>ALLOCATION SNAPSHOT</p>", unsafe_allow_html=True)
        for label, val in OVERVIEW_MAP.items():
            if val > 0:
                st.markdown(f"<div style='display:flex; justify-content:space-between; margin-bottom:12px; border-bottom:1px solid #1C3050; padding-bottom:4px;'><span style='color:#7A9BBF;'>{label}</span><span style='font-family:\"DM Mono\";'>{fmt_l(val)}</span></div>", unsafe_allow_html=True)

# ── TAB 2: PORTFOLIO ──────────────────────────────────────────────────────────
elif tab == "Portfolio":
    st.markdown("<p style='font-size:18px; color:#C8A84B; font-weight:500;'>Detailed Holdings Breakdown</p>", unsafe_allow_html=True)
    
    # Filter columns to only what we need for the table
    display_df = data_df[['Asset Name', 'Category', 'Units / Qty', 'Current Value']].copy()
    
    # Calculate live allocation percentages
    display_df['Allocation %'] = (display_df['Current Value'] / total_nw * 100).round(2).astype(str) + '%'
    
    # Format the Value column into Lakhs
    display_df['Current Value'] = display_df['Current Value'].apply(fmt_l)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ── TABS 3 & 4 ───────────────────────────────────────────────────────────────
elif tab == "Protection":
    st.info("Insurance Protection modules remain configured as per previous layout.")
elif tab == "Actions":
    st.info("Action Items tracking remains active for Vikram Batra.")
