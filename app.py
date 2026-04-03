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

# ── ROYAL UI STYLING ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.block-container { padding: 1.5rem 2rem 4rem 2rem; max-width: 1000px; }

/* Royal Dark Palette */
.stApp { background-color: #07101F !important; }
[data-testid="stAppViewContainer"] { background-color: #07101F !important; }
p, div, span, label { color: #EAE3D6; }

/* GOLD GRADIENT TEXT */
.gold-text {
    background: linear-gradient(to bottom, #C8A84B 0%, #E2CC8A 50%, #B38F36 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700;
    font-size: 64px !important;
    letter-spacing: -1px;
}

/* Navigation */
div[role="radiogroup"] { display: flex; gap: 8px; }
div[role="radiogroup"] label {
    background: #0C1A2E !important;
    border: 1px solid #1C3050 !important;
    border-radius: 10px !important;
    padding: 8px 18px !important;
    color: #5C7089 !important;
    font-size: 14px !important;
}
div[role="radiogroup"] label:has(input:checked) {
    background: rgba(200,168,75,0.12) !important;
    border-color: #C8A84B !important;
    color: #C8A84B !important;
}

/* Inputs & Buttons */
.stTextInput input { background: #112338 !important; border: 1px solid #1C3050 !important; color: #EAE3D6 !important; border-radius: 10px !important; }
.stButton button {
    background: linear-gradient(135deg, #C8A84B, #E2CC8A) !important;
    color: #07101F !important; font-weight: 600 !important; border-radius: 10px !important; border: none !important;
}

/* Action Cards */
.action-card-red { background: rgba(212, 88, 88, 0.08); border: 1px solid rgba(212, 88, 88, 0.4); border-left: 4px solid #D45858; border-radius: 12px; padding: 24px; min-height: 200px; }
.action-card-green { background: rgba(78, 175, 122, 0.08); border: 1px solid rgba(78, 175, 122, 0.4); border-left: 4px solid #4EAF7A; border-radius: 12px; padding: 24px; min-height: 200px; }

/* Strategy Box */
.strategy-box {
    background: rgba(200, 168, 75, 0.05);
    border: 1px dashed #C8A84B;
    border-radius: 12px;
    padding: 15px;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# ── DATA DEFS ─────────────────────────────────────────────────────────────────
CREDENTIALS = {"cm.narang": "Narang@2026"}
def fmt_cr(n): return f"₹{n/1e7:.2f} Cr"
def fmt_l(n):  return f"₹{n/1e5:.1f} L"

CMN = {
    "name": "CM Narang",
    "holdings": {
        "Mutual Funds (Equity)": 11000000,
        "Direct Equity": 400000,
        "Arbitrage (Wedding Fund)": 7000000,
        "Physical Gold": 7000000,
        "Savings Buffer": 6000000,
    }
}
TOTAL_NW = sum(CMN["holdings"].values())

# Updated Conservative Deployment Plan (₹7L)
SIP_BREAKDOWN = [
    {"name": "Nifty BEES (Large Cap)", "amt": 200000, "clr": "#52A2FF"},
    {"name": "Junior BEES (Next 50)",  "amt": 100000, "clr": "#57C785"},
    {"name": "MON100 ETF (Nasdaq)",    "amt": 100000, "clr": "#E2CC8A"}, # New Vehicle
    {"name": "Mid/Small Cap MFs",     "amt": 100000, "clr": "#A37CFF"},
    {"name": "Arbitrage / Debt Mix",   "amt": 200000, "clr": "#46C1C1"}  # Conservative pivot
]

# ── LOGIN ─────────────────────────────────────────────────────────────────────
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

# ── HEADER ────────────────────────────────────────────────────────────────────
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown(f"<div style='display:flex; align-items:center; gap:15px;'><div style='color:#C8A84B; font-size:24px;'>◈</div><div><div style='font-size:20px; font-weight:500;'>{CMN['name']}</div><div style='font-size:10px; color:#7A9BBF; letter-spacing:1px;'>THE 5-YEAR SPRINT · MARCH 2026</div></div></div>", unsafe_allow_html=True)
with c2:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown("<hr style='border:none; border-top:1px solid #1C3050; margin:15px 0;'>", unsafe_allow_html=True)
tab = st.radio("nav", ["Overview", "Portfolio", "Protection", "Actions"], horizontal=True, label_visibility="collapsed")

# ── TAB 1: OVERVIEW ───────────────────────────────────────────────────────────
if tab == "Overview":
    st.markdown(f"""
    <div style='background: linear-gradient(145deg, #0C1A2E, #112338); border: 1px solid #C8A84B40; border-radius: 20px; padding: 35px; text-align: center; margin-bottom: 25px;'>
        <p style='font-size: 11px; color: #7A9BBF; text-transform: uppercase; letter-spacing: 2px;'>Current Net Worth</p>
        <h1 class='gold-text'>{fmt_cr(TOTAL_NW)}</h1>
        <p style='font-size: 14px; color: #4EAF7A; margin-top: 10px;'>Target: ₹10 Cr by 2031 (Age 60)</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.markdown("<p style='font-size:11px; color:#C8A84B; font-weight:600; letter-spacing:1px; margin-bottom:15px;'>ASSET SNAPSHOT</p>", unsafe_allow_html=True)
        for asset, val in CMN["holdings"].items():
            st.markdown(f"<div style='display:flex; justify-content:space-between; font-size:13px; margin-bottom:8px;'><span style='color:#7A9BBF;'>{asset}</span><span style='font-family:\"DM Mono\";'>{fmt_l(val)}</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='background:#152440; height:3px; border-radius:2px; margin-bottom:12px;'><div style='background:#C8A84B; height:3px; width:{(val/TOTAL_NW)*100}%; border-radius:2px;'></div></div>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="strategy-box">
            <p style='color:#C8A84B; font-weight:600; font-size:12px; margin-bottom:5px;'>💍 WEDDING FUND STRATEGY</p>
            <p style='font-size:12px; color:#EAE3D6; line-height:1.5;'>
                Moving <b>₹70L FD → Arbitrage</b>.<br>
                <span style='color:#4EAF7A;'><b>Tax Win:</b></span> Arbitrage taxed as Equity (12.5% LTCG) vs. FD (30%+ Slab). Saves ~₹2L/yr in taxes.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("<p style='font-size:11px; color:#C8A84B; font-weight:600; letter-spacing:1px; margin-bottom:15px;'>CONSERVATIVE DEPLOYMENT (₹7L)</p>", unsafe_allow_html=True)
        for sip in SIP_BREAKDOWN:
            st.markdown(f"<div style='background:#0C1A2E; border:1px solid #1C3050; padding:12px 15px; border-radius:10px; margin-bottom:8px;'><div style='display:flex; justify-content:space-between; align-items:center;'><span>{sip['name']}</span><span style='font-family:\"DM Mono\"; color:{sip['clr']}; font-size:14px;'>{fmt_l(sip['amt'])}</span></div></div>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='background:rgba(82,162,255,0.05); border-radius:10px; padding:12px; margin-top:10px;'>
            <p style='font-size:11px; color:#7A9BBF; line-height:1.4;'>
                <b>Tactical Note:</b> MON100 ETF chosen for global exposure to avoid MF subscription limits. High Large-Cap tilt to protect capital as retirement nears.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ── TAB 2: PORTFOLIO ──────────────────────────────────────────────────────────
elif tab == "Portfolio":
    st.markdown("<p style='font-size:18px; color:#C8A84B; font-weight:500;'>Asset Distribution Profile</p>", unsafe_allow_html=True)
    
    fig = go.Figure(go.Pie(
        labels=list(CMN["holdings"].keys()), 
        values=list(CMN["holdings"].values()), 
        hole=0.55,
        marker=dict(colors=['#52A2FF','#57C785','#FFB84D','#E2CC8A','#46C1C1'], line=dict(color='#07101F', width=3))
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend=dict(font=dict(color="#EAE3D6")))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<p style='font-size:14px; color:#C8A84B; font-weight:500;'>Exit Strategy & Tax Sequencing</p>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#0C1A2E; border:1px solid #1C3050; border-radius:12px; padding:15px; font-size:13px; color:#7A9BBF; line-height:1.6;'>
        <b>Withdrawal Hierarchy:</b> To minimize tax liability post-retirement, withdrawals should prioritize 12.5% LTCG assets (Equity MFs) first. 
        <b>MON100 ETF</b> should be the <i>last resort</i>, liquidated only after active business income stops to potentially fall into a lower tax slab.
    </div>
    """, unsafe_allow_html=True)

# ── TAB 3: PROTECTION ─────────────────────────────────────────────────────────
elif tab == "Protection":
    st.markdown("<p style='font-size:11px; color:#C8A84B; font-weight:600; letter-spacing:1px;'>EXISTING PROTECTION SHIELD</p>", unsafe_allow_html=True)
    
    ins_data = [
        {"n": "Niva Bupa ReAssure 2.0", "c": "₹10 L", "w": "CM + Ritu", "r": "Nov 2026"},
        {"n": "Star Health Comp.",     "c": "₹10 L", "w": "CM + Ritu", "r": "Mar 2027"},
    ]
    
    for ins in ins_data:
        st.markdown(f"""
        <div style='background:#0C1A2E; border:1px solid #1C3050; border-radius:12px; padding:15px 20px; margin-bottom:10px; display:flex; justify-content:space-between;'>
            <div><div style='font-size:14px; font-weight:500;'>{ins['n']}</div><div style='font-size:11px; color:#7A9BBF;'>Covers: {ins['w']}</div></div>
            <div style='text-align:right;'><div style='color:#57C785; font-family:\"DM Mono\";'>{ins['c']}</div><div style='font-size:11px; color:#7A9BBF;'>Next Renewal: {ins['r']}</div></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><p style='font-size:11px; color:#C8A84B; font-weight:600; letter-spacing:1px;'>PROPOSED UPGRADE: HDFC ERGO OPTIMA SECURE</p>", unsafe_allow_html=True)
    st.markdown("""
    <table style='width:100%; border-collapse:collapse; margin-top:10px; background:#0C1A2E; border:1px solid #1C3050; border-radius:12px; overflow:hidden;'>
        <tr style='background:#1C3050;'>
            <th style='padding:12px; text-align:left; font-size:11px; color:#7A9BBF;'>Plan Variant</th>
            <th style='padding:12px; text-align:right; font-size:11px; color:#7A9BBF;'>Base Cover</th>
            <th style='padding:12px; text-align:right; font-size:11px; color:#7A9BBF;'>Approx Premium*</th>
        </tr>
        <tr><td style='padding:12px; border-bottom:1px solid #152440;'>Optima Secure</td><td style='padding:12px; text-align:right; border-bottom:1px solid #152440;'>₹25 Lakhs</td><td style='padding:12px; text-align:right; color:#C8A84B; border-bottom:1px solid #152440;'>₹45,000</td></tr>
        <tr><td style='padding:12px;'>Optima Secure</td><td style='padding:12px; text-align:right;'>₹50 Lakhs</td><td style='padding:12px; text-align:right; color:#C8A84B;'>₹68,000</td></tr>
    </table>
    <div style='margin-top:10px; padding:10px; background:rgba(200, 168, 75, 0.05); border-radius:8px;'>
        <p style='font-size:10px; color:#7A9BBF; line-height:1.4;'>
            * Estimates for CM + Ritu. Includes <i>'Secure'</i> benefit which doubles base cover from Day 1.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── TAB 4: ACTIONS ────────────────────────────────────────────────────────────
elif tab == "Actions":
    st.markdown("### Action Items & Next Steps")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div class="action-card-red"><p style='color:#D45858; font-weight:600; font-size:11px; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:15px;'>From Client</p><p style='font-size:14px; line-height:1.8;'>• FD maturity dates to avoid exit penalties<br>• Life Insurance policy PDFs for review<br>• Spouse medical history for final quotes</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="action-card-green"><p style='color:#4EAF7A; font-weight:600; font-size:11px; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:15px;'>From Vikram</p><p style='font-size:14px; line-height:1.8;'>• Side-by-side comparison of Optima Secure<br>• Asset Allocation Roadmap for ₹10 Cr target<br>• Execution of ₹20L Sprint SIP rebalancing</p></div>""", unsafe_allow_html=True)

st.markdown("<div style='text-align:center; margin-top:40px; font-size:10px; color:#3E5068;'>Wealth Strategist: Vikram Batra · Private & Confidential</div>", unsafe_allow_html=True)
