import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wealth Dashboard · CM Narang",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── HELPERS & FORMATTING (Defined First to avoid NameError) ──────────────────
def fmt_cr(n): return f"₹{n/1e7:.2f} Cr"
def fmt_l(n):  return f"₹{n/1e5:.1f} L"

# ── REAL-TIME ASSET DATA (April 2026 Estimates) ──────────────────────────────
NAV_DATA = {
    "DSP Small Cap": 191.06,
    "HDFC Mid Cap": 189.41,
    "HDFC Hybrid Equity": 116.63,
    "Invesco India Contra": 132.14,
    "MON100 ETF": 239.47,
    "JUNIORBEES": 668.77,
    "NIFTYBEES": 254.10
}

# Approved Conservative Deployment Plan (₹7L)
SIP_EXECUTION = [
    {"name": "Nifty BEES (Large Cap)", "amt": 200000, "clr": "#52A2FF", "date": "5th"},
    {"name": "Junior BEES (Next 50)",  "amt": 100000, "clr": "#57C785", "date": "5th"},
    {"name": "MON100 ETF (Nasdaq)",    "amt": 100000, "clr": "#E2CC8A", "date": "5th"},
    {"name": "Mid/Small Cap MFs",     "amt": 100000, "clr": "#A37CFF", "date": "10th"},
    {"name": "Arbitrage Fund",        "amt": 200000, "clr": "#46C1C1", "date": "1st"}
]

# ── STYLING ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #07101F !important; }
#MainMenu, footer, header { visibility: hidden; }

/* GOLD GRADIENT */
.gold-text {
    background: linear-gradient(to bottom, #C8A84B 0%, #E2CC8A 50%, #B38F36 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700;
    font-size: 56px !important;
}

/* CARDS */
.action-card-red { background: rgba(212, 88, 88, 0.08); border: 1px solid rgba(212, 88, 88, 0.4); border-left: 4px solid #D45858; border-radius: 12px; padding: 24px; min-height: 200px; }
.action-card-green { background: rgba(78, 175, 122, 0.08); border: 1px solid rgba(78, 175, 122, 0.4); border-left: 4px solid #4EAF7A; border-radius: 12px; padding: 24px; min-height: 200px; }
</style>
""", unsafe_allow_html=True)

# ── LOGIN LOGIC ───────────────────────────────────────────────────────────────
CREDENTIALS = {"cm.narang": "Narang@2026"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown("<div style='text-align:center; padding:50px 0;'><h2 style='color:#C8A84B;'>◈ PRIVATE WEALTH</h2><p style='font-size:12px; color:#7A9BBF;'>CHANDRA MOHAN NARANG</p></div>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Sign In", use_container_width=True):
            if u in CREDENTIALS and CREDENTIALS[u] == p:
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# ── MAIN DATA ─────────────────────────────────────────────────────────────────
TOTAL_NW = 32850000 # Calculated based on real-time holdings provided

# ── HEADER ────────────────────────────────────────────────────────────────────
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown(f"<div style='display:flex; align-items:center; gap:15px;'><div style='color:#C8A84B; font-size:24px;'>◈</div><div><div style='font-size:20px; font-weight:500; color:#EAE3D6;'>CM Narang</div><div style='font-size:10px; color:#7A9BBF; letter-spacing:1px;'>THE 5-YEAR SPRINT · MARCH 2026</div></div></div>", unsafe_allow_html=True)
with c2:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown("<hr style='border:none; border-top:1px solid #1C3050; margin:15px 0;'>", unsafe_allow_html=True)
tab = st.tabs(["◈ Overview", "◉ Portfolio", "🛡 Protection", "📋 Actions"])

# ── OVERVIEW ──────────────────────────────────────────────────────────────────
with tab[0]:
    st.markdown("<p style='text-align:center; color:#7A9BBF; font-size:11px; letter-spacing:2px;'>CURRENT NET WORTH JOURNEY</p>", unsafe_allow_html=True)
    st.markdown(f"<h1 class='gold-text' style='text-align:center;'>{fmt_cr(TOTAL_NW)}</h1>", unsafe_allow_html=True)
    
    # Journey Path Graph
    years = [2026, 2027, 2028, 2029, 2030, 2031]
    actual_path = [TOTAL_NW, 45000000, 58000000, 72000000, 88000000, 105000000]
    target_line = [31400000, 45000000, 58000000, 72000000, 86000000, 100000000]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=target_line, name="Target Line", line=dict(color='#1C3050', dash='dash')))
    fig.add_trace(go.Scatter(x=years, y=actual_path, name="Projected Path", fill='tozeroy', line=dict(color='#C8A84B', width=4)))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#7A9BBF", height=300, margin=dict(t=10,b=10,l=0,r=0), xaxis=dict(showgrid=False), yaxis=dict(showgrid=False, showticklabels=False))
    st.plotly_chart(fig, use_container_width=True)

# ── PORTFOLIO ─────────────────────────────────────────────────────────────────
with tab[1]:
    st.markdown("### Real-Time Asset Breakdown")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Holdings Status**")
        for asset, price in NAV_DATA.items():
            st.markdown(f"<div style='display:flex; justify-content:space-between; font-size:13px; color:#7A9BBF; border-bottom:1px solid #1C3050; padding:5px 0;'><span>{asset}</span><span>₹{price}</span></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("**Monthly SIP Execution**")
        for sip in SIP_EXECUTION:
            st.markdown(f"<div style='background:#0C1A2E; padding:10px; border-radius:8px; margin-bottom:5px; border-left:3px solid {sip['clr']}; display:flex; justify-content:space-between;'><span>{sip['name']} (On {sip['date']})</span><span style='color:{sip['clr']}'>{fmt_l(sip['amt'])}</span></div>", unsafe_allow_html=True)

# ── PROTECTION ────────────────────────────────────────────────────────────────
with tab[2]:
    st.markdown("### Coverage Summary")
    ins_plans = [
        {"n": "Term Life Insurance", "c": "₹1.00 Cr", "w": "CM Narang", "r": "Annual"},
        {"n": "Niva Bupa ReAssure 2.0", "c": "₹10 L", "w": "CM + Ritu", "r": "Nov 2026"},
        {"n": "Star Health Comp.", "c": "₹10 L", "w": "CM + Ritu", "r": "Mar 2027"},
    ]
    for ins in ins_plans:
        st.markdown(f"<div style='background:#0C1A2E; border:1px solid #1C3050; padding:15px; border-radius:12px; margin-bottom:10px; display:flex; justify-content:space-between;'><div><b>{ins['n']}</b><br><small style='color:#7A9BBF;'>Covers: {ins['w']}</small></div><div style='text-align:right;'><b style='color:#C8A84B;'>{ins['c']}</b><br><small style='color:#7A9BBF;'>Renewal: {ins['r']}</small></div></div>", unsafe_allow_html=True)

# ── ACTIONS ───────────────────────────────────────────────────────────────────
with tab[3]:
    st.markdown("### Action Items & Next Steps")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="action-card-red"><p style="color:#D45858; font-weight:600; font-size:11px; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:15px;">From Client</p><p style="font-size:14px; line-height:1.8; color:#EAE3D6;">• FD maturity dates to avoid exit penalties<br>• Life Insurance policy PDFs for review<br>• Spouse medical history for final quotes</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="action-card-green"><p style="color:#4EAF7A; font-weight:600; font-size:11px; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:15px;">From Vikram</p><p style="font-size:14px; line-height:1.8; color:#EAE3D6;">• Side-by-side comparison of Optima Secure<br>• Asset Allocation Roadmap for ₹10 Cr target<br>• Execution of ₹25L Sprint SIP rebalancing</p></div>', unsafe_allow_html=True)
