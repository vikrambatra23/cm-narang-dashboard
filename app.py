import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Wealth Terminal · CM Narang", page_icon="◈", layout="wide")

# ── TERMINAL UI STYLING ───────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #050A14; }
    .stApp { background-color: #050A14 !important; }
    #MainMenu, footer, header { visibility: hidden; }
    
    .gold-header {
        background: linear-gradient(90deg, #C8A84B, #E2CC8A);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 700; font-size: 38px; letter-spacing: -1px;
    }
    
    /* Table Styling */
    .static-table { width: 100%; border-collapse: collapse; margin-top: 10px; border: 1px solid #1C3050; }
    .static-table th { background: #0C1A2E; color: #C8A84B; text-align: left; padding: 12px; font-size: 11px; text-transform: uppercase; border-bottom: 2px solid #1C3050; }
    .static-table td { padding: 12px; border-bottom: 1px solid #1C3050; font-size: 13px; color: #EAE3D6; }
</style>
""", unsafe_allow_html=True)

# ── DATA ENGINE ───────────────────────────────────────────────────────────────
URL = "https://docs.google.com/spreadsheets/d/1PZACfddE3VkcCWqYD-_0j_ERaBUT1SBQqPN63Vylvy0/export?format=csv"
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def get_data():
    df = conn.read(spreadsheet=URL)
    df['Val_Num'] = pd.to_numeric(df['Current Value'].astype(str).replace('[₹,L,Cr, ,]', '', regex=True), errors='coerce').fillna(0)
    # Ignore "Total" rows to prevent 2x calculation
    assets = df[~df['Asset Name'].str.contains('Total|TOTAL|Sum|Subtotal', na=False)]
    assets = assets[assets['Val_Num'] > 0]
    
    # History Handling
    try:
        hist = conn.read(spreadsheet=URL, worksheet="History")
        hist['Date'] = pd.to_datetime(hist['Date'])
        hist['Net Worth'] = pd.to_numeric(hist['Net Worth'])
    except: hist = pd.DataFrame(columns=['Date', 'Net Worth'])
    return assets, hist

assets, history = get_data()
total_nw = assets['Val_Num'].sum()

# ── LOGIN CHECK ───────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div style='text-align:center; padding:60px 0;'><h2 style='color:#C8A84B;'>◈ PRIVATE WEALTH</h2><p style='color:#7A9BBF;'>CHANDRA MOHAN NARANG</p></div>", unsafe_allow_html=True)
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Sign In", use_container_width=True):
            if u == "cm.admin" and p == "Narang@2026": # Updated to Admin creds
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("<h1 class='gold-header'>Wealth Terminal</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#5C7089; margin-top:-15px;'>CM NARANG • FAMILY OFFICE • {pd.Timestamp.now().strftime('%d %b %Y')}</p>", unsafe_allow_html=True)
tab = st.radio("nav", ["Overview", "Portfolio", "Protection", "Actions"], horizontal=True, label_visibility="collapsed")

# ── TAB 1: OVERVIEW (ANALYTICAL) ──────────────────────────────────────────────
if tab == "Overview":
    # 10Cr Gauge
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number", value = total_nw / 10000000,
        number = {'suffix': " Cr", 'font': {'color': '#E2CC8A'}},
        gauge = {'axis': {'range': [None, 10]}, 'bar': {'color': "#C8A84B"}, 'bgcolor': "#0C1A2E", 'steps': [{'range': [0, 10], 'color': '#0C1A2E'}]}
    ))
    fig_gauge.update_layout(height=280, paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=40, b=0, l=10, r=10))
    st.plotly_chart(fig_gauge, use_container_width=True)

    c1, c2 = st.columns([1, 1.5])
    with c1:
        st.markdown("<p style='font-size:11px; color:#C8A84B; font-weight:600;'>ALLOCATION BREAKDOWN</p>", unsafe_allow_html=True)
        fig_pie = px.pie(assets, values='Val_Num', names='Category', hole=0.6, color_discrete_sequence=px.colors.sequential.Gold_r)
        fig_pie.update_layout(showlegend=True, paper_bgcolor='rgba(0,0,0,0)', legend=dict(font=dict(color="#7A9BBF", size=10), orientation="h", y=-0.2), margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        st.markdown("<p style='font-size:11px; color:#C8A84B; font-weight:600;'>JOURNEY TRAJECTORY</p>", unsafe_allow_html=True)
        if not history.empty:
            fig_line = px.line(history, x="Date", y="Net Worth")
            fig_line.update_traces(line_color='#C8A84B', fill='tozeroy')
            fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, yaxis=dict(showgrid=True, gridcolor="#1C3050"))
            st.plotly_chart(fig_line, use_container_width=True)
        else: st.info("Add a 'History' tab in Sheets to see the trend.")

# ── TAB 2: PORTFOLIO (DETAILED) ───────────────────────────────────────────────
elif tab == "Portfolio":
    st.markdown("<p style='color:#C8A84B; font-weight:600;'>DETAILED ASSET INVENTORY</p>", unsafe_allow_html=True)
    disp = assets[['Asset Name', 'Category', 'Units / Qty', 'Current Value', 'Val_Num']].copy()
    disp['Alloc %'] = (disp['Val_Num'] / total_nw * 100).round(1).astype(str) + '%'
    html = "<table class='static-table'><thead><tr><th>Asset Name</th><th>Category</th><th>Qty</th><th>Value (L)</th><th>Alloc %</th></tr></thead><tbody>"
    for _, r in disp.iterrows():
        html += f"<tr><td>{r['Asset Name']}</td><td>{r['Category']}</td><td>{r['Units / Qty']}</td><td>{fmt_l(r['Val_Num'])}</td><td>{r['Alloc %']}</td></tr>"
    st.markdown(html + "</tbody></table>", unsafe_allow_html=True)

# ── TAB 3: PROTECTION (TERM & HEALTH) ─────────────────────────────────────────
elif tab == "Protection":
    st.markdown("<p style='color:#C8A84B; font-weight:600;'>TERM LIFE PROTECTION</p>", unsafe_allow_html=True)
    st.markdown("<div style='background:#0C1A2E; padding:20px; border-radius:10px; border:1px solid #1C3050;'><h2 style='margin:0;'>₹1.00 Crore</h2><p style='color:#7A9BBF; font-size:12px;'>Primary Cover · Active · Nominee: Shubha Jain</p></div>", unsafe_allow_html=True)
    
    st.markdown("<br><p style='color:#C8A84B; font-weight:600;'>HEALTH INSURANCE (FLOATERS)</p>", unsafe_allow_html=True)
    h1, h2 = st.columns(2)
    with h1: st.markdown("<div style='background:#0C1A2E; padding:15px; border-radius:10px; border:1px solid #1C3050;'><p style='color:#7A9BBF; font-size:11px;'>Star Health (Family)</p><p style='font-size:18px; margin:0;'>₹20.0 L</p><p style='color:#57C785; font-size:10px;'>Incl. 10L Loyalty Bonus</p></div>", unsafe_allow_html=True)
    with h2: st.markdown("<div style='background:#0C1A2E; padding:15px; border-radius:10px; border:1px solid #1C3050;'><p style='color:#7A9BBF; font-size:11px;'>Niva Bupa (Couple)</p><p style='font-size:18px; margin:0;'>₹10.0 L</p><p style='color:#57C785; font-size:10px;'>ReAssure 2.0 Titanium+</p></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:rgba(200,168,75,0.05); padding:20px; border-radius:10px; border:1px solid #C8A84B; margin-top:20px;'>
        <p style='color:#C8A84B; font-weight:700; font-size:13px;'>◈ ADVISOR PROPOSAL: HDFC ERGO OPTIMA SECURE</p>
        <p style='font-size:12px; color:#EAE3D6;'><b>Recommended Base:</b> ₹30.0 L (Doubles to 60L on Day 1).<br><b>Total Shield:</b> Combined protection hits ₹90L immediately.</p>
    </div>""", unsafe_allow_html=True)

# ── TAB 4: ACTIONS ────────────────────────────────────────────────────────────
elif tab == "Actions":
    st.markdown("<p style='color:#C8A84B; font-weight:600;'>STRATEGIC ACTIONS</p>", unsafe_allow_html=True)
    actions = [("Monthly Wealth Infusion", "₹7.0 L SIP on the 25th.", "Vikram Batra"), ("Health Shield Upgrade", "Initiate HDFC Ergo Optima Secure 30L.", "Vikram Batra"), ("Legacy Portfolio Exit", "Phased liquidation into NiftyBees.", "Vikram Batra")]
    for act, desc, owner in actions:
        st.markdown(f"<div style='padding:15px; border-bottom:1px solid #1C3050;'><p style='color:#C8A84B; font-weight:600; margin:0;'>{act}</p><p style='font-size:12px; color:#EAE3D6; margin-top:3px;'>{desc} <span style='color:#7A9BBF;'>• {owner}</span></p></div>", unsafe_allow_html=True)
