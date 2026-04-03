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

# ── ENHANCED STYLING (High Contrast & Readability) ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.block-container { padding: 1.5rem 2rem 4rem 2rem; max-width: 1100px; }

/* Dark Luxury Theme */
.stApp { background-color: #050B14 !important; }
[data-testid="stAppViewContainer"] { background-color: #050B14 !important; }
p, div, span, label { color: #EAE3D6; }

/* Better Navigation Buttons */
div[role="radiogroup"] { display: flex; gap: 10px; }
div[role="radiogroup"] label {
    background: #0C1A2E !important;
    border: 1px solid #1C3050 !important;
    border-radius: 12px !important;
    padding: 10px 20px !important;
    color: #7A9BBF !important;
    font-weight: 500 !important;
}
div[role="radiogroup"] label:has(input:checked) {
    background: rgba(200,168,75,0.15) !important;
    border-color: #C8A84B !important;
    color: #E2CC8A !important;
}

/* Input Fields */
.stTextInput input {
    background: #0C1A2E !important;
    border: 1px solid #1C3050 !important;
    border-radius: 10px !important;
    color: #EAE3D6 !important;
}

/* Main Action Button */
.stButton button {
    background: linear-gradient(135deg, #C8A84B, #B38F36) !important;
    color: #050B14 !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

# ── DATA & CALCULATIONS (Updated per March 9 MOM) ─────────────────────────────
CREDENTIALS = {"cm.narang": "Narang@2026"}

def fmt_cr(n): return f"₹{n/1e7:.2f} Cr"
def fmt_l(n):  return f"₹{n/1e5:.1f} L"

CMN = {
    "name": "CM Narang",
    "age": 55,
    "target_age": 60,
    "current_corpus": 31400000, # ₹3.14 Cr
    "monthly_surplus": 700000,   # ₹7 Lakhs
    "holdings": {
        "Mutual Funds (Equity)": 11000000,
        "Physical Gold": 7000000,
        "Arbitrage (Wedding Fund)": 7000000, # Moved from FD
        "Savings Buffer": 6000000,
        "Direct Equity": 400000
    }
}

# SIP Re-allocation per MOM (Wedding SIP removed as FD is enough)
SIP_PLAN = [
    {"name": "Nifty BEES (Large Cap)", "amt": 100000, "clr": "#4E87D4"},
    {"name": "Junior BEES (Next 50)",  "amt": 100000, "clr": "#4EAF7A"},
    {"name": "Midcap / Smallcap Core", "amt": 150000, "clr": "#9B72D0"},
    {"name": "Debt / GILT Mix",       "amt": 100000, "clr": "#3DAFB8"},
    {"name": "Sprint Surplus (TBD)",  "amt": 250000, "clr": "#C8A84B"} # Increased for the 10Cr goal
]

# ── LOGIN LOGIC ───────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center; color:#C8A84B;'>◈ NARANG</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#7A9BBF; font-size:12px;'>PRIVATE WEALTH DASHBOARD</p>", unsafe_allow_html=True)
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Access Dashboard", use_container_width=True):
            if user in CREDENTIALS and CREDENTIALS[user] == pw:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Invalid Credentials")
    st.stop()

# ── HEADER ────────────────────────────────────────────────────────────────────
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown(f"## The 5-Year Sprint: {CMN['name']}")
    st.markdown(f"<p style='color:#7A9BBF; margin-top:-15px;'>Strategy Roadmap · Updated March 2026 · Consultant: Vikram Batra</p>", unsafe_allow_html=True)
with c2:
    if st.button("Sign Out"):
        st.session_state.logged_in = False
        st.rerun()

tab = st.radio("NAV", ["Overview", "Portfolio", "Protection", "Action Items"], horizontal=True, label_visibility="collapsed")
st.divider()

# ── TAB: OVERVIEW ─────────────────────────────────────────────────────────────
if tab == "Overview":
    # Hero Card
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #0C1A2E 0%, #162B45 100%); padding: 40px; border-radius: 20px; border: 1px solid #C8A84B40; text-align: center;'>
        <p style='letter-spacing: 2px; color: #7A9BBF; font-size: 12px; text-transform: uppercase;'>Total Current Net Worth</p>
        <h1 style='font-size: 64px; color: #E2CC8A; margin: 10px 0;'>{fmt_cr(CMN['current_corpus'])}</h1>
        <div style='display: inline-block; padding: 6px 15px; background: rgba(78, 175, 122, 0.1); border-radius: 20px; border: 1px solid #4EAF7A;'>
            <span style='color: #4EAF7A; font-size: 14px;'>On Track for ₹10 Cr Empire</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Key Stats
    k1, k2, k3 = st.columns(3)
    k1.metric("Monthly Surplus", "₹7,00,000", "Updated Strategy")
    k2.metric("Sprint Target", "₹10.00 Cr", "By Age 60")
    k3.metric("Wedding Fund", "₹70.00 L", "Fully Funded (Arbitrage)")

    st.markdown("### Monthly Deployment Plan")
    for s in SIP_PLAN:
        pct = (s['amt'] / 700000) * 100
        st.markdown(f"""
        <div style='background:#0C1A2E; padding:12px 20px; border-radius:12px; border-left: 5px solid {s['clr']}; margin-bottom:8px;'>
            <div style='display:flex; justify-content:space-between;'>
                <span style='font-weight:500;'>{s['name']}</span>
                <span style='font-family: "DM Mono"; color:{s['clr']};'>{fmt_l(s['amt'])}/mo</span>
            </div>
            <div style='background:#152440; height:4px; border-radius:2px; margin-top:8px;'>
                <div style='background:{s['clr']}; height:4px; width:{pct}%; border-radius:2px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── TAB: PORTFOLIO ────────────────────────────────────────────────────────────
elif tab == "Portfolio":
    st.subheader("Asset Allocation Breakdown")
    labels = list(CMN["holdings"].keys())
    values = list(CMN["holdings"].values())
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5, marker_colors=['#4E87D4','#C8A84B','#3DAFB8','#D45858','#4EAF7A'])])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#EAE3D6", margin=dict(t=0,b=0,l=0,r=0))
    st.plotly_chart(fig, use_container_width=True)

    st.info("💡 Strategic Note: The ₹70L FD has been officially integrated into Arbitrage Funds. No further monthly SIPs are required for the Wedding Fund as the current corpus + growth will hit the target.")

# ── TAB: PROTECTION ───────────────────────────────────────────────────────────
elif tab == "Protection":
    st.subheader("Insurance Comparison: HDFC ERGO Optima Secure")
    
    st.markdown("""
    <table style='width:100%; border-collapse: collapse; background: #0C1A2E; border-radius: 15px; overflow: hidden;'>
        <tr style='background: #1C3050; text-align: left;'>
            <th style='padding: 15px;'>Feature</th>
            <th style='padding: 15px; color: #7A9BBF;'>Option A (₹25L)</th>
            <th style='padding: 15px; color: #C8A84B;'>Option B (₹50L)</th>
        </tr>
        <tr style='border-bottom: 1px solid #1C3050;'>
            <td style='padding: 15px;'>Base Cover</td>
            <td style='padding: 15px;'>₹25 Lakhs</td>
            <td style='padding: 15px;'>₹50 Lakhs</td>
        </tr>
        <tr style='border-bottom: 1px solid #1C3050;'>
            <td style='padding: 15px;'>Secure Benefit (Instant)</td>
            <td style='padding: 15px;'>₹50 Lakhs Total</td>
            <td style='padding: 15px;'>₹1 Crore Total</td>
        </tr>
        <tr>
            <td style='padding: 15px;'>Suitability</td>
            <td style='padding: 15px; font-size: 12px;'>Standard Protection</td>
            <td style='padding: 15px; font-size: 12px; color: #4EAF7A;'>Recommended for HNI Wealth Protection</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)
    
    st.warning("⚠️ Action Required: Spouse (Ritu Narang) DOB and Medical History needed for final underwriting.")

# ── TAB: ACTION ITEMS ─────────────────────────────────────────────────────────
elif tab == "Action Items":
    st.subheader("Immediate Steps")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### ⏳ From Client (CM Narang)")
        st.error("• FD Maturity Schedule (to avoid penalties)")
        st.error("• Medical history of spouse")
        st.error("• Life Insurance PDF copies for audit")
    
    with col_b:
        st.markdown("#### ✅ From Vikram Batra")
        st.success("• Full 5-Year Roadmap (Completed)")
        st.info("• Final Insurance Quotes (Awaiting Client Data)")
        st.info("• Deployment of ₹2.5L Sprint Surplus")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#3E5068; font-size:11px;'>Strictly Private & Confidential · Wealth Management Division · 2026</p>", unsafe_allow_html=True)
