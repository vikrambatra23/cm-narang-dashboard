import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
        df['Val_Num'] = pd.to_numeric(df['Current Value'].astype(str).replace('[₹,L,Cr, ,]', '', regex=True), errors='coerce').fillna(0)
    assets = df[~df['Asset Name'].str.contains('Total|TOTAL|Sum|Subtotal', na=False)]
    return assets.dropna(subset=['Asset Name'])

try:
    assets_df = fetch_data()
    total_nw = assets_df['Val_Num'].sum()
    
    mf_v = assets_df[assets_df['Category'].str.contains('Aggressive|Stable|Legacy', na=False)]['Val_Num'].sum()
    etf_v = assets_df[assets_df['Category'].str.contains('New Core|New Global|New Stability', na=False)]['Val_Num'].sum()
    gold_v = assets_df[assets_df['Category'].str.contains('Commodities', na=False)]['Val_Num'].sum()
    fd_v = assets_df[assets_df['Category'].str.contains('Fixed Income', na=False)]['Val_Num'].sum()
    cash_v = assets_df[assets_df['Category'].str.contains('Liquid', na=False)]['Val_Num'].sum()

    OVERVIEW_MAP = {"Mutual Funds": mf_v, "ETFs": etf_v, "Gold": gold_v, "Fixed Income": fd_v, "Cash": cash_v}
except:
    st.stop()

# ── LOGIN SYSTEM ──────────────────────────────────────────────────────────────
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
            else:
                st.error("Invalid Credentials")
    st.stop()

# ── HEADER SECTION ────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([2, 1])
with col_h1:
    st.markdown("<h1 style='background: linear-gradient(90deg, #C8A84B, #E2CC8A); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; font-size: 38px; margin-bottom: 0px;'>Chandra Mohan Narang</h1><p style='color: #7A9BBF; font-size: 11px; text-transform: uppercase; letter-spacing: 2px; margin-top: -5px;'>Family Office Dashboard</p>", unsafe_allow_html=True)
with col_h2:
    st.markdown(f"<div style='text-align: right; padding-top: 20px;'><p style='color: #5C7089; font-size: 10px; margin-bottom: 0;'>VALUATION DATE</p><p style='color: #EAE3D6; font-size: 14px; font-weight: 500;'>{pd.Timestamp.now().strftime('%d %B, %Y')}</p></div>", unsafe_allow_html=True)

st.markdown("<hr style='margin: 5px 0 15px 0; border: 1px solid #1C3050;'>", unsafe_allow_html=True)
tab = st.radio("nav", ["Overview", "Portfolio", "Protection", "Actions"], horizontal=True, label_visibility="collapsed")

# ── TABS ──────────────────────────────────────────────────────────────────────
if tab == "Overview":
    # 10Cr SPEEDOMETER GAUGE
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = total_nw / 10000000, 
        number = {'suffix': " Cr", 'font': {'color': '#E2CC8A', 'size': 50}},
        title = {'text': "GOAL PROGRESS: 10 CR JOURNEY", 'font': {'size': 12, 'color': '#7A9BBF'}},
        gauge = {
            'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "#1C3050"},
            'bar': {'color': "#C8A84B"},
            'bgcolor': "#0C1A2E",
            'borderwidth': 2,
            'bordercolor': "#1C3050",
            'steps': [{'range': [0, 10], 'color': '#0C1A2E'}],
            'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': 10}
        }
    ))
    fig_gauge.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=50, b=20, l=20, r=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # ── DOUBLE LINE SEPARATION ──
    st.markdown("""
        <div style="margin: 10px 0 30px 0;">
            <hr style="border: 0; border-top: 1px solid #1C3050; margin-bottom: 3px;">
            <hr style="border: 0; border-top: 1px solid #1C3050;">
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        fig = go.Figure(go.Pie(labels=list(OVERVIEW_MAP.keys()), values=list(OVERVIEW_MAP.values()), hole=0.7, marker=dict(colors=['#52A2FF','#57C785','#E2CC8A','#46C1C1','#A37CFF'])))
        fig.update_layout(showlegend=True, paper_bgcolor='rgba(0,0,0,0)', legend=dict(font=dict(color="#7A9BBF", size=10), orientation="h", y=-0.2), margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("<p style='font-size:12px; color:#C8A84B; font-weight:600; letter-spacing:1px; margin-bottom:20px;'>ALLOCATION SUMMARY</p>", unsafe_allow_html=True)
        for label, val in OVERVIEW_MAP.items():
            if val > 0: st.markdown(f"<div style='display:flex; justify-content:space-between; margin-bottom:18px; border-bottom:1px solid #1C3050; padding-bottom:6px;'><span>{label}</span><span style='font-family:\"JetBrains Mono\";'>{fmt_l(val)}</span></div>", unsafe_allow_html=True)

elif tab == "Portfolio":
    st.markdown("<p style='font-size:20px; color:#C8A84B; font-weight:500;'>Detailed Holding Inventory</p>", unsafe_allow_html=True)
    disp = assets_df[['Asset Name', 'Category', 'Units / Qty', 'Current Value', 'Val_Num']].copy()
    disp = disp.sort_values(by='Val_Num', ascending=False) 
    disp['Alloc %'] = (disp['Val_Num'] / total_nw * 100).round(1).astype(str) + '%'
    
    html = "<table class='static-table'><thead><tr><th>Asset Name</th><th>Category</th><th>Qty</th><th>Value</th><th>Alloc %</th></tr></thead><tbody>"
    for _, r in disp.iterrows():
        html += f"<tr><td>{r['Asset Name']}</td><td>{r['Category']}</td><td>{r['Units / Qty']}</td><td>{fmt_l(r['Val_Num'])}</td><td>{r['Alloc %']}</td></tr>"
    st.markdown(html + "</tbody></table>", unsafe_allow_html=True)

elif tab == "Protection":
    st.markdown("<p style='font-size:20px; color:#C8A84B; font-weight:500;'>Term Life Protection</p>", unsafe_allow_html=True)
    st.markdown("<div style='background:#0C1A2E; padding:25px; border-radius:15px; border:1px solid #1C3050;'><p style='color:#7A9BBF; font-size:12px;'>Sum Insured</p><h2 style='margin:0;'>₹1.00 Crore</h2><p style='color:#C8A84B; font-size:11px;'>Primary Policy · Active · Nominee: Shubha Jain</p></div>", unsafe_allow_html=True)
    st.markdown("<br><p style='font-size:20px; color:#C8A84B; font-weight:500;'>Family Health Shield</p>", unsafe_allow_html=True)
    h1, h2 = st.columns(2)
    with h1: st.markdown("<div style='background:#0C1A2E; padding:20px; border-radius:12px; border:1px solid #1C3050;'><p style='color:#7A9BBF; font-size:11px;'>Star Comprehensive (Family)</p><p style='font-size:18px; margin:0;'>₹20.0 L</p><p style='color:#57C785; font-size:10px;'>Incl. 10L Loyalty Bonus · Covers Son</p></div>", unsafe_allow_html=True)
    with h2: st.markdown("<div style='background:#0C1A2E; padding:20px; border-radius:12px; border:1px solid #1C3050;'><p style='color:#7A9BBF; font-size:11px;'>Niva Bupa ReAssure 2.0 (Couple)</p><p style='font-size:18px; margin:0;'>₹10.0 L</p><p style='color:#57C785; font-size:10px;'>Titanium+ Variant · No Claim Bonus</p></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:rgba(200,168,75,0.05); padding:25px; border-radius:15px; border:2px solid #C8A84B; margin-top:20px;'><p style='color:#C8A84B; font-weight:700; font-size:14px;'>◈ PROPOSED: HDFC ERGO OPTIMA SECURE (30L BASE)</p><p style='font-size:13px; color:#EAE3D6; line-height:1.6;'><b>Benefit:</b> Doubles to <b>60L</b> on Day 1.<br><b>Total Protection:</b> Immediate <b>90L</b> shield, growing to 1.20Cr+ via Plus Benefit.</p></div>", unsafe_allow_html=True)

elif tab == "Actions":
    st.markdown("<p style='font-size:20px; color:#C8A84B; font-weight:500;'>Strategic Actions</p>", unsafe_allow_html=True)
    actions = [("Monthly Wealth Infusion", "₹7.0 L SIP on the 25th.", "Vikram Batra"), ("Health Upgrade", "Initiate HDFC Ergo Optima Secure 30L.", "Vikram Batra"), ("Legacy Portfolio Exit", "Phased liquidation into NiftyBees / Gold.", "Vikram Batra")]
    for act, desc, owner in actions:
        st.markdown(f"<div style='padding:20px; border-bottom:1px solid #1C3050;'><div style='display:flex; justify-content:space-between;'><span style='color:#C8A84B; font-weight:600;'>{act}</span><span style='color:#7A9BBF; font-size:11px;'>{owner}</span></div><p style='font-size:13px; color:#EAE3D6; margin-top:5px;'>{desc}</p></div>", unsafe_allow_html=True)
