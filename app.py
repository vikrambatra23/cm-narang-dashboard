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

# ── HELPERS ───────────────────────────────────────────────────────────────────
def fmt_cr(n): return f"₹{n/1e7:.2f} Cr"
def fmt_l(n):  return f"₹{n/1e5:.1f} L"

# ── DATA (Restored to stable state) ───────────────────────────────────────────
CREDENTIALS = {"cm.narang": "Narang@2026"}

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

# ── STYLING (The "Royal" CSS you liked) ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #07101F !important; }
#MainMenu, footer, header { visibility: hidden; }

/* Gold Text Styling */
.gold-text {
    background: linear-gradient(to bottom, #C8A84B 0%, #E2CC8A 50%, #B38F36 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700;
    font-size: 56px !important;
}

/* Nav Bar Styling */
div[role="radiogroup"] { display: flex; gap: 8px; }
div[role="radiogroup"] label {
    background: #0C1A2E !important;
    border: 1px solid #1C3050 !important;
    border-radius: 10px !important;
    padding: 8px 18px !important;
    color: #5C7089 !important;
}
div[role="radiogroup"] label:has(input:checked) {
    background: rgba(200,168,75,0.12) !important;
    border-color: #C8A84B !important;
    color: #C8A84B !important;
}

/* Action Cards */
.action-card-red { background: rgba(212, 88, 88, 0.05); border: 1px solid #D4585840; border-radius: 12px; padding: 20px; }
.action-card-green { background: rgba(78, 175, 122, 0.05); border: 1px solid #4EAF7A40; border-radius: 12px; padding: 20px; }
</style>
""", unsafe_allow_html=True)

# ── LOGIN ─────────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown("<div style='text-align:center; padding:50px 0;'><h2 style='color:#C8A84B;'>◈ PRIVATE WEALTH</h2></div>", unsafe_allow_html=True)
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
    st.markdown(f"### ◈ {CMN['name']}")
    st.markdown(f"<p style='color:#7A9BBF; margin-top:-15px;'>THE 5-YEAR SPRINT · MARCH 2026</p>", unsafe_allow_html=True)
with c2:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

st.divider()
tab = st.radio("nav", ["Overview", "Portfolio", "Protection", "Actions"], horizontal=True, label_visibility="collapsed")

# ── TABS ──────────────────────────────────────────────────────────────────────
if tab == "Overview":
    st.markdown(f"<p style='text-align:center; color:#7A9BBF;'>CURRENT NET WORTH</p>", unsafe_allow_html=True)
    st.markdown(f"<h1 class='gold-text' style='text-align:center;'>{fmt_cr(TOTAL_NW)}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#4EAF7A;'>Goal: ₹10 Cr by 2031</p>", unsafe_allow_html=True)

elif tab == "Actions":
    st.markdown("### Action Items & Next Steps")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="action-card-red"><p style="color:#D45858;">FROM CLIENT</p>• FD maturity dates<br>• Life Insurance PDFs<br>• Spouse medical history</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="action-card-green"><p style="color:#4EAF7A;">FROM VIKRAM</p>• Optima Secure Comparison<br>• ₹10 Cr Roadmap<br>• SIP Rebalancing</div>', unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<div style='text-align:center; margin-top:50px; font-size:10px; color:#3E5068;'>Wealth Strategist: Vikram Batra</div>", unsafe_allow_html=True)
