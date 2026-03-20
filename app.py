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

# ── STYLING ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=DM+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.block-container { padding: 1.5rem 2rem 4rem 2rem; max-width: 1000px; }

/* Dark background */
.stApp { background-color: #07101F !important; }
section[data-testid="stSidebar"] { background-color: #0C1A2E !important; }
[data-testid="stAppViewContainer"] { background-color: #07101F !important; }
[data-testid="stHeader"] { background-color: #07101F !important; }
p, div, span, label { color: #EAE3D6; }

div[role="radiogroup"] { display: flex; gap: 6px; flex-wrap: wrap; }
div[role="radiogroup"] label {
    background: #0C1A2E !important;
    border: 1px solid #1C3050 !important;
    border-radius: 8px !important;
    padding: 6px 16px !important;
    color: #3E5068 !important;
    cursor: pointer !important;
    font-size: 13px !important;
    transition: all 0.2s !important;
}
div[role="radiogroup"] label:has(input:checked) {
    background: rgba(200,168,75,0.12) !important;
    border-color: rgba(200,168,75,0.45) !important;
    color: #C8A84B !important;
}
div[role="radiogroup"] label input { display: none !important; }

.stTextInput input {
    background: #112338 !important;
    border: 1px solid #1C3050 !important;
    border-radius: 10px !important;
    color: #EAE3D6 !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput input:focus { border-color: rgba(200,168,75,0.4) !important; }

.stButton button {
    background: linear-gradient(135deg, #C8A84B, #E2CC8A) !important;
    color: #07101F !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    padding: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# ── CREDENTIALS ───────────────────────────────────────────────────────────────
CREDENTIALS = {
    "cm.narang": "Narang@2026"
}

# ── HELPERS ───────────────────────────────────────────────────────────────────
def fmt_cr(n):    return f"₹{n/1e7:.2f} Cr"
def fmt_l(n):     return f"₹{n/1e5:.1f} L"
def fmt_smart(n): return fmt_cr(n) if n >= 1e7 else fmt_l(n)
def fv(pv, yrs, r=0.12): return pv * (1 + r) ** yrs

# ── COLORS ────────────────────────────────────────────────────────────────────
COLORS = {
    "Mutual Funds (Equity)": "#4E87D4",
    "Direct Equity":         "#4EAF7A",
    "Fixed Deposits":        "#F0A500",
    "Gold":                  "#C8A84B",
    "Savings Buffer":        "#3DAFB8",
}

# ── DATA ──────────────────────────────────────────────────────────────────────
YEAR = 2026

CMN = {
    "name":        "CM Narang",
    "full_name":   "Chandra Mohan Narang",
    "spouse":      "Ritu Narang",
    "age":         55,
    "retire_age":  60,           # 5-Year Sprint target (MOM: 9 March 2026)
    "retire_year": 2031,
    "swp_age":     64,           # SWP drawdown age
    "swp_year":    2035,
    "color":       "#4E87D4",
    "holdings": {
        "Mutual Funds (Equity)": 11000000,   # ₹1.10 Cr (conviction core ₹75L + satellite ₹35L)
        "Direct Equity":            400000,   # ₹4 L
        "Fixed Deposits":          7000000,   # ₹70 L → moving to Arbitrage (Wedding Bridge)
        "Gold":                    7000000,   # ₹70 L physical gold (MOM update)
        "Savings Buffer":          6000000,   # ₹60 L (8-month cushion for business volatility)
    },
    "sip_monthly": 700000,   # ₹7 L/month investible surplus (MOM update)
}

TOTAL_CORPUS = sum(CMN["holdings"].values())   # ₹3.14 Cr current

# Monthly SIP breakdown (PDF roadmap + MOM)
SIP_BREAKDOWN = [
    {"name": "Nifty BEES (Large Cap)",   "amount": 100000, "color": "#4E87D4"},
    {"name": "Junior BEES (Next 50)",    "amount": 100000, "color": "#4EAF7A"},
    {"name": "MiD150 BEES (Midcap)",     "amount":  50000, "color": "#9B72D0"},
    {"name": "Arbitrage / GILT Mix",     "amount": 200000, "color": "#3DAFB8"},
    {"name": "Wedding Arbitrage SIP",    "amount":  50000, "color": "#C8A84B"},
    {"name": "Deployment TBD (₹2L)",     "amount": 200000, "color": "#3E5068"},
]
TOTAL_SIP = sum(s["amount"] for s in SIP_BREAKDOWN)

# Goals
WEDDING_TARGET_TODAY = 10000000    # ₹1 Cr
WEDDING_YEARS        = 5
WEDDING_YEAR         = 2031

# Retirement SWP: ₹4L/month at 5% safe withdrawal → ₹9.6 Cr corpus
SWP_MONTHLY          = 400000
RETIRE_CORPUS_TARGET = SWP_MONTHLY * 12 / 0.05   # ₹9.6 Cr at age 64

# 5-Year Empire Target
EMPIRE_TARGET        = 10e7        # ₹10 Cr by age 60

# Projected corpus in 5 yrs (current corpus + SIPs at blended ~11% return)
PROJECTED_5YR_MODERATE = 9.73e7    # Moderate scenario (PDF: ₹9.97–11.61 Cr range)
PROJECTED_5YR_AGGRESSIVE = 10.77e7 # Aggressive scenario

GOALS = [
    {"icon": "💍", "name": "Son's Wedding",    "sub": "Target: ₹1 Cr in 5 years",        "today": 10000000, "years": 5, "year": 2031, "color": "#C8A84B"},
    {"icon": "🏠", "name": "Lifestyle Upgrade","sub": "Post-retirement metro living",     "today": 5000000,  "years": 9, "year": 2035, "color": "#4EAF7A"},
]

# Insurance
INSURANCE = [
    {"name": "Niva Bupa ReAssure 2.0",          "cover": "₹10 L",    "type": "Health (Floater)", "who": "CM Narang + Ritu", "until": "Nov 2026", "cat": "health"},
    {"name": "Star Health Comprehensive",        "cover": "₹10 L",    "type": "Health (Floater)", "who": "CM Narang",        "until": "Mar 2027", "cat": "health"},
    {"name": "HDFC ERGO Optima Secure (Prop.)",  "cover": "₹25–50 L", "type": "Health Top-Up",   "who": "CM Narang + Ritu", "until": "TBD",      "cat": "health"},
    {"name": "Life Insurance",                   "cover": "TBD",       "type": "Life",             "who": "CM Narang",        "until": "TBD",      "cat": "life"},
]

LIFE_COVER_CMN = {
    "current": 0,
    "target":  20000000,   # ₹2 Cr (placeholder — policy details pending)
    "gap":     20000000,
    "buy":     "TBD — policy documents awaited",
    "policies": []         # Pending — client to share PDFs
}

ALERTS = [
    {"icon": "⚠️", "color": "#D45858", "msg": "Niva Bupa ReAssure 2.0 expires November 2026 — health cover renewal / porting due in ~8 months"},
    {"icon": "⚠️", "color": "#D49040", "msg": "Star Health Comprehensive expires March 2027 — renewal in ~12 months. Consider porting to HDFC ERGO Optima Secure"},
    {"icon": "💰", "color": "#4EAF7A", "msg": "₹70L FD to move to Arbitrage Fund — Wedding Bridge strategy. Pending FD maturity schedule from client"},
    {"icon": "🎯", "color": "#4E87D4", "msg": "Son's Wedding goal: ₹1 Cr by 2031 — ₹70L FD in Arbitrage + ₹50K/month SIP should reach ~₹95L–1.1 Cr"},
    {"icon": "🛡️", "color": "#9B72D0", "msg": "HDFC ERGO Optima Secure quote pending — ₹25L vs ₹50L comparison + Ritu Narang DOB & medical history required"},
    {"icon": "📋", "color": "#C8A84B", "msg": "FD maturity dates pending from client — must be shared to avoid premature exit penalties"},
    {"icon": "📋", "color": "#C8A84B", "msg": "Life insurance policy details pending — cover may be insufficient. Client to share all policy PDFs"},
    {"icon": "📅", "color": "#4EAF7A", "msg": "Annual LTCG harvest due every March — sell ₹4–5L of satellite funds (₹35L pool) to utilise ₹1.25L exemption"},
    {"icon": "🏦", "color": "#3DAFB8", "msg": "₹60L Savings Buffer allocated — held as 8-month business volatility cushion. Review quarterly"},
    {"icon": "📊", "color": "#4E87D4", "msg": "Conviction portfolio (₹75L): DSP Small Cap · HDFC Midcap · Invesco India — retain these 3 funds long-term"},
]

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ══════════════════════════════════════════════════════════════════════════════
# LOGIN SCREEN
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown("""
        <div style='text-align:center; padding:48px 0 28px;'>
            <div style='display:inline-block; font-size:9px; letter-spacing:3px; text-transform:uppercase;
                color:#C8A84B; background:rgba(200,168,75,0.08); border:1px solid rgba(200,168,75,0.2);
                border-radius:20px; padding:5px 14px; margin-bottom:18px;'>Private Wealth Dashboard</div>
            <div style='font-size:40px; color:#EAE3D6; line-height:1.1; margin-bottom:6px;'>
                CM Narang</div>
            <div style='font-size:13px; color:#7A9BBF; margin-bottom:6px;'>Chandra Mohan Narang</div>
            <div style='font-family:"DM Mono",monospace; font-size:11px; color:#7A9BBF;'>
                Sign in to view your portfolio</div>
        </div>
        """, unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Enter username", label_visibility="collapsed")
        password = st.text_input("Password", type="password", placeholder="Enter password", label_visibility="collapsed")
        login    = st.button("Sign In", use_container_width=True)

        if login:
            if username in CREDENTIALS and CREDENTIALS[username] == password:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Incorrect username or password.")

        st.markdown("""
        <div style='text-align:center; font-size:10px; color:#7A9BBF; margin-top:16px;'>
            Read-only · Secure · Private</div>
        """, unsafe_allow_html=True)

    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

# ── TOP NAV ───────────────────────────────────────────────────────────────────
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown(f"""
    <div style='display:flex; align-items:center; gap:12px; padding:4px 0 0;'>
        <div style='width:32px; height:32px; border-radius:8px; background:rgba(200,168,75,0.08);
            border:1px solid rgba(200,168,75,0.25); display:flex; align-items:center;
            justify-content:center; color:#C8A84B; font-size:14px; flex-shrink:0;'>◈</div>
        <div>
            <div style='font-size:17px; color:#EAE3D6; line-height:1;'>CM Narang</div>
            <div style='font-family:"DM Mono",monospace; font-size:9px; color:#7A9BBF;'>
                Wealth Dashboard · March 2026 · The 5-Year Sprint</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    if st.button("Sign Out", key="signout"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown("<hr style='border:none; border-top:1px solid #1C3050; margin:12px 0 20px;'>", unsafe_allow_html=True)

# ── TAB NAVIGATION ────────────────────────────────────────────────────────────
tab = st.radio("nav", ["◈  Overview", "◉  Portfolio", "◎  Goals", "◇  Protection", "🔔  Alerts"],
               horizontal=True, label_visibility="collapsed")
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if tab == "◈  Overview":
    st.markdown('<div style="font-size:32px; color:#EAE3D6; margin-bottom:4px;">Where you are today</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'DM Mono\',monospace; font-size:11px; color:#7A9BBF; margin-bottom:20px;">Complete snapshot of wealth · March 2026 · The 5-Year Sprint to ₹10 Cr</div>', unsafe_allow_html=True)

    # ── Hero card ─────────────────────────────────────────────────────────────
    SIP_PCT = TOTAL_SIP / CMN["sip_monthly"] * 100
    st.markdown(f"""
    <div style='background:linear-gradient(140deg,#0C1A2E,#112338); border:1px solid #1C3050;
        border-radius:20px; padding:40px 32px; text-align:center; margin-bottom:20px;'>
        <div style='font-size:10px; letter-spacing:2.5px; text-transform:uppercase; color:#7A8A9E;
            margin-bottom:12px;'>Current Net Worth</div>
        <div style='font-size:clamp(42px,6vw,68px); font-weight:500; color:#C8A84B; line-height:1; margin-bottom:8px;'>
            {fmt_cr(TOTAL_CORPUS)}</div>
        <div style='font-family:"DM Mono",monospace; font-size:11px; color:#7A9BBF; margin-bottom:30px;'>
            Chandra Mohan Narang · Self-Employed · Age 55 · Delhi</div>
        <div style='max-width:480px; margin:0 auto;'>
            <div style='display:flex; justify-content:space-between; font-size:11px; margin-bottom:8px;'>
                <span style='color:#7A8A9E;'>Monthly Surplus Deployed</span>
                <span style='font-family:"DM Mono",monospace; color:#C8A84B;'>
                    {fmt_l(TOTAL_SIP)} <span style='color:#7A9BBF;'>/ {fmt_l(CMN["sip_monthly"])}</span></span>
            </div>
            <div style='height:6px; background:#152440; border-radius:3px; overflow:hidden;'>
                <div style='height:100%; width:{SIP_PCT:.1f}%;
                    background:linear-gradient(90deg,#C8A84B,#E2CC8A); border-radius:3px;'></div>
            </div>
            <div style='display:flex; justify-content:space-between; margin-top:6px; font-size:10px;'>
                <span style='color:#7A9BBF;'>{SIP_PCT:.0f}% of ₹7L monthly surplus</span>
                <span style='color:#D45858; font-family:"DM Mono",monospace;'>
                    ₹2L deployment plan pending</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Summary stat cards ────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    for col, icon, lbl, val, sub, color in [
        (col1, "📅", "Years to Sprint Goal", f"{CMN['retire_year'] - YEAR}", "Age 60 · 5-Year Empire",    "#4E87D4"),
        (col2, "💰", "Monthly Surplus",      "₹7.0 L",                      "Investible post expenses",   "#4EAF7A"),
        (col3, "🎯", "Empire Target",        "₹10 Cr+",                     "By 2031 · Moderate scenario","#C8A84B"),
        (col4, "📊", "Risk Profile",         "Moderate",                    "Hold on 20% correction",     "#9B72D0"),
    ]:
        with col:
            st.markdown(f"""
            <div style='background:#0C1A2E; border:1px solid {color}25; border-radius:14px; padding:18px; margin-bottom:20px;'>
                <div style='font-size:22px; margin-bottom:8px;'>{icon}</div>
                <div style='font-size:9px; color:#7A9BBF; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:4px;'>{lbl}</div>
                <div style='font-family:"DM Mono",monospace; font-size:22px; color:{color}; margin-bottom:4px;'>{val}</div>
                <div style='font-size:10px; color:#7A9BBF;'>{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Portfolio breakdown ───────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background:#0C1A2E; border:1px solid #4E87D430; border-top:3px solid #4E87D4;
        border-radius:16px; padding:24px 24px 8px; margin-bottom:4px;'>
        <div style='display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;'>
            <div>
                <div style='display:flex; align-items:center; gap:8px; margin-bottom:4px;'>
                    <div style='width:8px; height:8px; border-radius:50%; background:#4E87D4;'></div>
                    <span style='font-size:11px; color:#7A8A9E; letter-spacing:2px; text-transform:uppercase;'>CM Narang · Full Portfolio</span>
                </div>
                <div style='font-size:30px; font-weight:500; color:#EAE3D6;'>{fmt_l(TOTAL_CORPUS)}</div>
            </div>
            <div style='background:#4E87D415; border:1px solid #4E87D440;
                border-radius:8px; padding:8px 12px; text-align:center;'>
                <div style='font-family:"DM Mono",monospace; font-size:22px; color:#4E87D4; line-height:1;'>
                    {CMN["retire_year"] - YEAR}</div>
                <div style='font-size:9px; color:#7A9BBF; margin-top:2px; text-transform:uppercase; letter-spacing:1px;'>
                    yrs to sprint</div>
            </div>
        </div>
        <div style='font-size:11px; color:#7A9BBF; margin-bottom:12px;'>
            Age {CMN["age"]} · Target Age {CMN["retire_age"]} · {CMN["retire_year"]} · Self-Employed · Metro</div>
    </div>
    """, unsafe_allow_html=True)

    for asset, val in CMN["holdings"].items():
        pct   = val / TOTAL_CORPUS
        color = COLORS.get(asset, "#7A8A9E")
        tag   = ""
        if asset == "Fixed Deposits":    tag = "<span style='font-size:9px; color:#F0A500; background:#F0A50015; border-radius:4px; padding:1px 6px; margin-left:6px;'>→ Moving to Arbitrage</span>"
        if asset == "Savings Buffer":    tag = "<span style='font-size:9px; color:#3DAFB8; background:#3DAFB815; border-radius:4px; padding:1px 6px; margin-left:6px;'>8-month cushion</span>"
        if asset == "Mutual Funds (Equity)": tag = "<span style='font-size:9px; color:#4E87D4; background:#4E87D415; border-radius:4px; padding:1px 6px; margin-left:6px;'>₹75L conviction · ₹35L satellite</span>"
        st.markdown(f"""
        <div style='background:#0C1A2E; padding:4px 24px; margin-top:-4px;'>
            <div style='display:flex; justify-content:space-between; margin-bottom:4px; align-items:center;'>
                <span style='font-size:11px; color:#7A8A9E; display:flex; align-items:center;'>{asset}{tag}</span>
                <span style='font-family:"DM Mono",monospace; font-size:11px; color:#7A9BBF;'>{fmt_l(val)}</span>
            </div>
            <div style='height:3px; background:#152440; border-radius:2px; margin-bottom:8px;'>
                <div style='height:100%; width:{pct*100:.1f}%; background:{color}; border-radius:2px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background:#0C1A2E; border:1px solid #1C3050; border-top:none;
        border-radius:0 0 16px 16px; padding:10px 24px 16px; margin-top:-4px; margin-bottom:20px;'>
        <div style='border-top:1px solid #152440; padding-top:10px;
            display:flex; justify-content:space-between; font-size:11px;'>
            <span style='color:#7A8A9E;'>Monthly SIPs (active)</span>
            <span style='font-family:"DM Mono",monospace; color:#4E87D4;'>{fmt_l(TOTAL_SIP - 200000)}/mo · ₹2L deployment TBD</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Monthly SIP plan ──────────────────────────────────────────────────────
    st.markdown('<div style="font-size:11px; color:#A0B8D0; font-weight:600; margin-bottom:12px; letter-spacing:1.5px; text-transform:uppercase;">Monthly Investment Deployment — ₹7L Plan</div>', unsafe_allow_html=True)
    for sip in SIP_BREAKDOWN:
        pct = sip["amount"] / CMN["sip_monthly"] * 100
        opacity = "60" if sip["name"].startswith("Deployment") else ""
        st.markdown(f"""
        <div style='background:#0C1A2E; padding:10px 20px; border-radius:10px; margin-bottom:6px;
            border:1px solid {sip["color"]}20; opacity:{"0.6" if opacity else "1"};'>
            <div style='display:flex; justify-content:space-between; margin-bottom:6px; align-items:center;'>
                <span style='font-size:12px; color:#7A8A9E;'>{sip["name"]}</span>
                <span style='font-family:"DM Mono",monospace; font-size:12px; color:{sip["color"]};'>
                    {fmt_l(sip["amount"])}/mo</span>
            </div>
            <div style='height:3px; background:#152440; border-radius:2px;'>
                <div style='height:100%; width:{pct:.1f}%; background:{sip["color"]}; border-radius:2px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Gold note ─────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background:#0C1A2E; border:1px solid #1C3050; border-radius:12px;
        padding:16px 20px; margin-top:16px; display:flex; align-items:center;
        justify-content:space-between; flex-wrap:wrap; gap:8px;'>
        <div style='display:flex; align-items:center; gap:12px;'>
            <span style='font-size:22px;'>🥇</span>
            <div>
                <div style='font-size:14px; color:#EAE3D6;'>Physical Gold — Now in the Plan</div>
                <div style='font-size:11px; color:#7A9BBF; margin-top:2px;'>
                    Integrated as wealth store · Not for active trading · Held long-term</div>
            </div>
        </div>
        <div style='text-align:right;'>
            <div style='font-family:"DM Mono",monospace; font-size:16px; color:#C8A84B;'>₹70 L</div>
            <div style='font-size:10px; color:#7A9BBF; margin-top:3px;'>Physical gold holdings</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PORTFOLIO
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "◉  Portfolio":
    st.markdown('<div style="font-size:32px; color:#EAE3D6; margin-bottom:4px;">Your portfolio breakdown</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'DM Mono\',monospace; font-size:11px; color:#7A9BBF; margin-bottom:20px;">Asset allocation · Conviction core · Satellite clean-up plan</div>', unsafe_allow_html=True)

    labels = list(CMN["holdings"].keys())
    values = list(CMN["holdings"].values())
    colors = [COLORS.get(l, "#7A8A9E") for l in labels]

    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.62,
        marker=dict(colors=colors, line=dict(color="#07101F", width=3)),
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    fig.add_annotation(text=fmt_cr(TOTAL_CORPUS), x=0.5, y=0.56,
                       font=dict(family="DM Mono", size=18, color="#C8A84B"), showarrow=False)
    fig.add_annotation(text="net worth", x=0.5, y=0.44,
                       font=dict(family='Inter', size=11, color="#3E5068"), showarrow=False)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=0, r=0), height=320,
        legend=dict(font=dict(color="#7A8A9E", family='Inter', size=12),
                   bgcolor="rgba(0,0,0,0)", x=1.02, y=0.5, xanchor="left"),
    )
    st.plotly_chart(fig, use_container_width=True)

    mf_pct  = CMN["holdings"]["Mutual Funds (Equity)"] / TOTAL_CORPUS * 100
    gold_pct = CMN["holdings"]["Gold"] / TOTAL_CORPUS * 100
    fd_pct  = CMN["holdings"]["Fixed Deposits"] / TOTAL_CORPUS * 100

    st.markdown(f"""
    <div style='background:rgba(200,168,75,0.04); border:1px solid rgba(200,168,75,0.12);
        border-radius:10px; padding:14px 18px; font-size:12px; color:#7A8A9E; line-height:1.6; margin-bottom:24px;'>
        <strong style='color:#C8A84B;'>Portfolio note:</strong> Equity MFs form {mf_pct:.0f}% of the portfolio
        — the primary long-term growth engine with a conviction core of 3 funds (DSP Small Cap · HDFC Midcap · Invesco India).
        Gold at {gold_pct:.0f}% acts as a stable wealth store. FDs ({fd_pct:.0f}%) are being repositioned into
        Arbitrage for tax efficiency and the wedding goal.
    </div>
    """, unsafe_allow_html=True)

    # ── Conviction core breakdown ─────────────────────────────────────────────
    st.markdown('<div style="font-size:11px; color:#A0B8D0; font-weight:600; margin-bottom:12px; letter-spacing:1.5px; text-transform:uppercase;">Mutual Fund Strategy</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style='background:#0C1A2E; border:1px solid #4E87D430; border-radius:14px; padding:20px; margin-bottom:16px;'>
            <div style='font-size:10px; color:#4E87D4; letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;'>
                ◉ Conviction Core — Retain ₹75 L</div>
            <div style='font-size:12px; color:#7A8A9E; margin-bottom:16px; line-height:1.6;'>
                Three high-conviction funds held as the anchor of your wealth. Never touch these.</div>
            <div style='display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #152440;'>
                <div style='display:flex; align-items:center; gap:8px;'>
                    <div style='width:6px; height:6px; border-radius:50%; background:#4EAF7A;'></div>
                    <span style='font-size:12px; color:#EAE3D6;'>DSP Small Cap</span>
                </div>
                <span style='font-size:10px; color:#4EAF7A;'>HOLD</span>
            </div>
            <div style='display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #152440;'>
                <div style='display:flex; align-items:center; gap:8px;'>
                    <div style='width:6px; height:6px; border-radius:50%; background:#4EAF7A;'></div>
                    <span style='font-size:12px; color:#EAE3D6;'>HDFC Midcap</span>
                </div>
                <span style='font-size:10px; color:#4EAF7A;'>HOLD</span>
            </div>
            <div style='display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #152440;'>
                <div style='display:flex; align-items:center; gap:8px;'>
                    <div style='width:6px; height:6px; border-radius:50%; background:#4EAF7A;'></div>
                    <span style='font-size:12px; color:#EAE3D6;'>Invesco India</span>
                </div>
                <span style='font-size:10px; color:#4EAF7A;'>HOLD</span>
            </div>
            <div style='margin-top:12px; font-family:"DM Mono",monospace; font-size:20px; color:#4E87D4;'>₹75 L</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style='background:#0C1A2E; border:1px solid #D4585830; border-radius:14px; padding:20px; margin-bottom:16px;'>
            <div style='font-size:10px; color:#D45858; letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;'>
                ◎ Satellite Clean-up — ₹35 L over 9 yrs</div>
            <div style='font-size:12px; color:#7A8A9E; margin-bottom:14px; line-height:1.6;'>
                12+ remaining funds to be liquidated gradually via annual tax harvesting.</div>
            <div style='background:#D4585810; border:1px solid #D4585830; border-radius:8px; padding:12px 14px; margin-bottom:12px;'>
                <div style='font-size:10px; color:#D45858; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;'>Method</div>
                <div style='font-size:11px; color:#7A9BBF; line-height:1.6;'>
                    Sell ₹4–5L every March · Utilise ₹1.25L annual LTCG exemption · Zero tax leakage</div>
            </div>
            <div style='font-family:"DM Mono",monospace; font-size:20px; color:#D45858;'>₹35 L → ₹0</div>
            <div style='font-size:10px; color:#7A9BBF; margin-top:4px;'>~9 years at ₹4–5L per annum</div>
        </div>
        """, unsafe_allow_html=True)

    # ── New monthly SIP allocation ────────────────────────────────────────────
    st.markdown('<div style="font-size:11px; color:#A0B8D0; font-weight:600; margin-bottom:12px; letter-spacing:1.5px; text-transform:uppercase;">New Monthly SIP Allocation</div>', unsafe_allow_html=True)
    sip_data = [s for s in SIP_BREAKDOWN if not s["name"].startswith("Deployment")]
    total_active = sum(s["amount"] for s in sip_data)

    fig2 = go.Figure(go.Bar(
        x=[s["amount"] / 1e5 for s in sip_data],
        y=[s["name"] for s in sip_data],
        orientation='h',
        marker_color=[s["color"] for s in sip_data],
        text=[f"₹{s['amount']//1000}K" for s in sip_data],
        textposition="outside",
        textfont=dict(color="#EAE3D6", size=11, family="DM Mono"),
        hovertemplate="<b>%{y}</b><br>₹%{x:.1f}L/month<extra></extra>",
    ))
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=10, r=60), height=220,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(tickfont=dict(color="#7A8A9E", size=11, family="Inter")),
        bargap=0.35,
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown(f"""
    <div style='background:#0C1A2E; border:1px solid #3DAFB830; border-radius:10px; padding:14px 18px;
        font-size:12px; color:#7A8A9E; line-height:1.6; margin-top:4px;'>
        <strong style='color:#C8A84B;'>Tax strategy:</strong>
        Arbitrage Funds (6.5–7.5% · LTCG taxed at 12.5%) preferred over FDs for the Wedding goal
        — saves ~18% tax leakage vs slab rate. GILT Funds (7–8.5%) held 10+ years for the
        retirement bucket at absolute safety.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — GOALS
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "◎  Goals":
    st.markdown('<div style="font-size:32px; color:#EAE3D6; margin-bottom:4px;">Where you want to be</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'DM Mono\',monospace; font-size:11px; color:#7A9BBF; margin-bottom:20px;">Long-term milestones · 5-Year Sprint · All values at projected growth rates</div>', unsafe_allow_html=True)

    # ── Two Primary Targets ───────────────────────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        gap_to_empire = EMPIRE_TARGET - TOTAL_CORPUS
        pct_done = TOTAL_CORPUS / EMPIRE_TARGET * 100
        st.markdown(f"""
        <div style='background:linear-gradient(140deg,#0A1A0A,#0D200D); border-left:4px solid #4EAF7A;
            border-radius:0 16px 16px 0; padding:24px; margin-bottom:16px;'>
            <div style='font-size:10px; color:#4EAF7A; letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;'>
                🚀 Primary Target — The ₹10 Cr Empire</div>
            <div style='font-size:12px; color:#A0B8D0; margin-bottom:4px;'>5-Year Sprint · ₹7L/month SIP</div>
            <div style='font-size:11px; color:#7A9BBF; margin-bottom:14px;'>
                Moderate scenario: ₹9.73 Cr · Aggressive: ₹10.77 Cr by 2031</div>
            <div style='font-size:10px; color:#7A9BBF; margin-bottom:4px;'>Target by 2031 · Age 60</div>
            <div style='font-family:"DM Mono",monospace; font-size:40px; color:#4EAF7A; line-height:1;'>
                {fmt_cr(EMPIRE_TARGET)}</div>
            <div style='margin-top:14px; height:4px; background:#152440; border-radius:2px;'>
                <div style='height:100%; width:{pct_done:.1f}%; background:#4EAF7A; border-radius:2px;'></div>
            </div>
            <div style='font-size:10px; color:#7A9BBF; margin-top:6px;'>
                {pct_done:.0f}% built · Gap: {fmt_cr(gap_to_empire)} to close in 5 years</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        RETIRE_CORPUS_NEEDED = SWP_MONTHLY * 12 / 0.05
        st.markdown(f"""
        <div style='background:linear-gradient(140deg,#1A0C0C,#200E0E); border-left:4px solid #D45858;
            border-radius:0 16px 16px 0; padding:24px; margin-bottom:16px;'>
            <div style='font-size:10px; color:#D45858; letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;'>
                🌅 Retirement — ₹4L/month SWP</div>
            <div style='font-size:12px; color:#A0B8D0; margin-bottom:4px;'>
                ₹4L/month income starting age 64 · 5% safe withdrawal</div>
            <div style='font-size:11px; color:#7A9BBF; margin-bottom:14px;'>
                Safe Bucket (₹4.4 Cr debt) funds 10+ years without touching equity</div>
            <div style='font-size:10px; color:#7A9BBF; margin-bottom:4px;'>Corpus needed at age 64 · 2035</div>
            <div style='font-family:"DM Mono",monospace; font-size:40px; color:#D45858; line-height:1;'>
                {fmt_cr(RETIRE_CORPUS_NEEDED)}</div>
            <div style='font-size:10px; color:#7A9BBF; margin-top:8px;'>
                9 years to build · Projected range ₹9.97–11.61 Cr ✓</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Projection scenarios ──────────────────────────────────────────────────
    scenarios = [
        ("Conservative",  9,  9.97e7, "#7A9BBF", 5.54, 4.43),
        ("Moderate",     11, 10.73e7, "#C8A84B", 6.30, 4.43),
        ("Aggressive",   13, 11.61e7, "#4EAF7A", 7.18, 4.43),
    ]
    scenario_rows = ""
    for s_label, s_rate, s_val, s_color, s_eq, s_debt in scenarios:
        scenario_rows += f"<div style='margin-bottom:12px;'><div style='display:flex; justify-content:space-between; margin-bottom:4px;'><span style='font-size:11px; color:#7A8A9E;'>{s_label} ({s_rate}% equity)</span><span style='font-family:\"DM Mono\",monospace; font-size:13px; color:{s_color};'>{fmt_cr(s_val)}</span></div><div style='display:flex; height:8px; border-radius:4px; overflow:hidden; gap:2px;'><div style='flex:{s_eq}; background:#4EAF7A; border-radius:4px 0 0 4px;'></div><div style='flex:{s_debt}; background:#4E87D4; border-radius:0 4px 4px 0;'></div></div><div style='display:flex; justify-content:space-between; font-size:10px; color:#3E5068; margin-top:2px;'><span>Equity: {fmt_cr(s_eq * 1e7)}</span><span>Debt: ₹4.43 Cr</span></div></div>"
    st.markdown(f"<div style='background:#0C1A2E; border:1px solid #2A3F58; border-radius:12px; padding:16px 24px; margin-bottom:24px;'><div style='font-size:10px; color:#7A9BBF; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:14px;'>Projected Corpus at Age 64 — Three Scenarios</div>{scenario_rows}</div>", unsafe_allow_html=True)

    # ── Other Goals ───────────────────────────────────────────────────────────
    st.markdown('<div style="font-size:11px; color:#A0B8D0; font-weight:600; margin-bottom:12px; letter-spacing:1.5px; text-transform:uppercase;">Other Goals</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    # Wedding goal — special treatment
    with col1:
        st.markdown(f"""
        <div style='background:#0C1A2E; border:1px solid #C8A84B25; border-radius:14px; padding:22px 18px; margin-bottom:16px;'>
            <div style='font-size:26px; margin-bottom:10px;'>💍</div>
            <div style='font-size:18px; font-weight:500; color:#EAE3D6; margin-bottom:3px;'>Son's Wedding</div>
            <div style='font-size:11px; color:#7A9BBF; margin-bottom:18px;'>Funding the milestone · 5 years · 2031</div>
            <div style='font-size:9px; color:#7A9BBF; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:3px;'>Target corpus</div>
            <div style='font-family:"DM Mono",monospace; font-size:24px; color:#C8A84B; margin-bottom:12px;'>₹1.00 Cr</div>
            <div style='background:#C8A84B10; border:1px solid #C8A84B30; border-radius:8px; padding:10px 12px; font-size:11px; color:#7A9BBF; line-height:1.7;'>
                <strong style='color:#C8A84B;'>Bridge plan:</strong><br>
                ₹70L FD → Arbitrage Fund<br>
                + ₹50K/month SIP → Arbitrage<br>
                Tax saving: ₹1.6L/year vs FD<br>
                <strong style='color:#4EAF7A;'>Projected: ~₹95L–1.1 Cr by 2031 ✓</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        inflated = fv(GOALS[1]["today"], GOALS[1]["years"])
        g = GOALS[1]
        st.markdown(f"""
        <div style='background:#0C1A2E; border:1px solid {g["color"]}25; border-radius:14px; padding:22px 18px; margin-bottom:16px;'>
            <div style='font-size:26px; margin-bottom:10px;'>{g["icon"]}</div>
            <div style='font-size:18px; font-weight:500; color:#EAE3D6; margin-bottom:3px;'>{g["name"]}</div>
            <div style='font-size:11px; color:#7A9BBF; margin-bottom:18px;'>{g["sub"]}</div>
            <div style='font-size:9px; color:#7A9BBF; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:3px;'>In today's money</div>
            <div style='font-family:"DM Mono",monospace; font-size:14px; color:#A0B8D0; margin-bottom:12px;'>{fmt_smart(g["today"])}</div>
            <div style='font-size:9px; color:#7A9BBF; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:3px;'>Needed by {g["year"]} · 6% inflation</div>
            <div style='font-family:"DM Mono",monospace; font-size:24px; color:{g["color"]}; margin-bottom:16px;'>{fmt_smart(inflated)}</div>
            <div style='display:inline-flex; align-items:center; gap:6px; background:{g["color"]}12; border-radius:20px; padding:4px 12px;'>
                <div style='width:5px; height:5px; border-radius:50%; background:{g["color"]};'></div>
                <span style='font-size:10px; color:{g["color"]};'>{g["years"]} years · {g["year"]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PROTECTION
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "◇  Protection":
    st.markdown('<div style="font-size:32px; color:#EAE3D6; margin-bottom:4px;">Your protection shield</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'DM Mono\',monospace; font-size:11px; color:#7A9BBF; margin-bottom:20px;">Health and life cover · CM Narang & Ritu Narang</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    for col, icon, lbl, val, sub, color in [
        (col1, "🏥", "Total Health Cover",   "₹20 L",  "Niva Bupa + Star Health (active)", "#3DAFB8"),
        (col2, "🛡️", "Proposed Cover",       "₹50–60 L","Post HDFC ERGO top-up",           "#9B72D0"),
        (col3, "📅", "Nearest Renewal",      "Nov 2026", "Niva Bupa · 8 months away",       "#D45858"),
    ]:
        with col:
            st.markdown(f"""
            <div style='background:#0C1A2E; border:1px solid {color}25; border-radius:14px; padding:20px; margin-bottom:20px;'>
                <div style='font-size:24px; margin-bottom:10px;'>{icon}</div>
                <div style='font-size:10px; color:#7A9BBF; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:4px;'>{lbl}</div>
                <div style='font-family:"DM Mono",monospace; font-size:26px; color:{color}; margin-bottom:4px;'>{val}</div>
                <div style='font-size:11px; color:#7A9BBF;'>{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Health cover gap ──────────────────────────────────────────────────────
    st.markdown('<div style="font-size:11px; color:#A0B8D0; font-weight:600; margin-bottom:12px; letter-spacing:1.5px; text-transform:uppercase;">Health Cover — Gap Analysis</div>', unsafe_allow_html=True)

    current_health = 2000000   # ₹20L current
    target_health  = 6000000   # ₹60L target with top-up
    gap_health     = target_health - current_health
    pct_health     = current_health / target_health * 100

    st.markdown(f"""
    <div style='background:#0C1A2E; border:1px solid #3DAFB830; border-radius:14px; padding:20px; margin-bottom:16px;'>
        <div style='display:flex; align-items:center; gap:8px; margin-bottom:14px;'>
            <div style='width:8px; height:8px; border-radius:50%; background:#3DAFB8;'></div>
            <span style='font-size:11px; color:#A0B8D0; letter-spacing:2px; text-transform:uppercase;'>CM Narang + Ritu Narang</span>
        </div>
        <div style='display:flex; justify-content:space-between; padding:7px 0; border-bottom:1px solid #152440;'>
            <span style='font-size:11px; color:#7A9BBF;'>Niva Bupa ReAssure 2.0</span>
            <span style='font-family:"DM Mono",monospace; font-size:11px; color:#4EAF7A;'>₹10 L</span>
            <span style='font-family:"DM Mono",monospace; font-size:11px; color:#3E5068;'>till Nov 2026</span>
        </div>
        <div style='display:flex; justify-content:space-between; padding:7px 0; border-bottom:1px solid #152440;'>
            <span style='font-size:11px; color:#7A9BBF;'>Star Health Comprehensive</span>
            <span style='font-family:"DM Mono",monospace; font-size:11px; color:#4EAF7A;'>₹10 L</span>
            <span style='font-family:"DM Mono",monospace; font-size:11px; color:#3E5068;'>till Mar 2027</span>
        </div>
        <div style='margin-top:14px; padding-top:12px; border-top:1px solid #1C3050;'>
            <div style='display:flex; justify-content:space-between; margin-bottom:6px;'>
                <span style='font-size:11px; color:#7A9BBF;'>Current total cover</span>
                <span style='font-family:"DM Mono",monospace; font-size:13px; color:#EAE3D6;'>₹20 L</span>
            </div>
            <div style='display:flex; justify-content:space-between; margin-bottom:10px;'>
                <span style='font-size:11px; color:#7A9BBF;'>Target cover (post top-up)</span>
                <span style='font-family:"DM Mono",monospace; font-size:13px; color:#EAE3D6;'>₹60 L</span>
            </div>
            <div style='height:4px; background:#152440; border-radius:2px; margin-bottom:10px;'>
                <div style='height:100%; width:{pct_health:.0f}%; background:#3DAFB8; border-radius:2px;'></div>
            </div>
            <div style='background:#C8A84B15; border:1px solid #C8A84B40; border-radius:8px; padding:10px 14px;
                display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <div style='font-size:10px; color:#C8A84B; text-transform:uppercase; letter-spacing:1px; margin-bottom:2px;'>
                        → Recommended: HDFC ERGO Optima Secure Top-Up</div>
                    <div style='font-size:11px; color:#7A9BBF;'>₹50L top-up cover · Bumps effective cover to ₹60 L+</div>
                </div>
                <div style='font-family:"DM Mono",monospace; font-size:20px; color:#C8A84B;'>₹40 L</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background:#0C1A2E; border:1px solid #1C3050; border-radius:12px;
        padding:16px 20px; margin-bottom:20px; font-size:12px; color:#7A8A9E; line-height:1.7;'>
        <strong style='color:#C8A84B;'>Rationale:</strong> At age 55 (self-employed, no employer cover),
        ₹20L health cover is inadequate for a metro family. Upgrading to HDFC ERGO Optima Secure at ₹50L top-up
        effectively provides ₹60 L+ cover. At 30% tax slab, health insurance premium also yields tax deduction
        under 80D. <strong style='color:#EAE3D6;'>Action pending: Ritu Narang's DOB + medical history needed
        for final quote comparison (₹25L vs ₹50L).</strong>
    </div>
    """, unsafe_allow_html=True)

    # ── Life insurance ────────────────────────────────────────────────────────
    st.markdown('<div style="font-size:11px; color:#A0B8D0; font-weight:600; margin-bottom:12px; letter-spacing:1.5px; text-transform:uppercase;">Life Insurance — Status</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background:#0C1A2E; border:1px solid #D4585830; border-radius:14px; padding:20px; margin-bottom:20px;'>
        <div style='background:#D4585815; border:1px solid #D4585840; border-radius:8px; padding:14px;
            display:flex; justify-content:space-between; align-items:center;'>
            <div>
                <div style='font-size:10px; color:#D45858; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;'>
                    ⚠ Life Policy Details Pending</div>
                <div style='font-size:11px; color:#7A9BBF; line-height:1.6;'>
                    Client to share all life insurance policy PDFs for review.<br>
                    Assessment: cover sufficiency, maturity values, surrender vs hold decision.
                </div>
            </div>
            <div style='font-family:"DM Mono",monospace; font-size:18px; color:#D45858; flex-shrink:0; margin-left:16px;'>TBD</div>
        </div>
        <div style='margin-top:14px; font-size:11px; color:#7A9BBF; line-height:1.7;'>
            <strong style='color:#C8A84B;'>Note:</strong> At age 55 with ₹3.14 Cr corpus and ₹7L/month surplus,
            traditional life cover need may be limited. Term insurance premium at this age is high.
            Full assessment will follow once policy documents are received.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Insurance table ───────────────────────────────────────────────────────
    for section_title, cat, color in [("🏥 Health Insurance", "health", "#3DAFB8"), ("🛡️ Life & Investment Policies", "life", "#9B72D0")]:
        filtered = [i for i in INSURANCE if i["cat"] == cat]
        st.markdown(f"""
        <div style='background:#0C1A2E; border:1px solid #1C3050; border-radius:16px; padding:22px; margin-bottom:16px;'>
            <div style='font-size:20px; color:#EAE3D6; margin-bottom:18px;'>{section_title}</div>
            <div style='overflow-x:auto;'>
            <table style='width:100%; border-collapse:collapse; min-width:460px;'>
                <thead><tr>
                    {''.join(f"<th style='text-align:left; padding:8px 10px; font-size:9px; color:#7A9BBF; text-transform:uppercase; letter-spacing:1.2px; border-bottom:1px solid #1C3050;'>{h}</th>"
                             for h in ["Policy", "Coverage", "Type", "Covers", "Until"])}
                </tr></thead>
                <tbody>
                    {''.join(f"""<tr style='border-bottom:1px solid #152440;'>
                        <td style='padding:11px 10px; font-size:12px; color:#7A8A9E;'>{i["name"]}</td>
                        <td style='padding:11px 10px; font-size:12px; color:#4EAF7A; font-family:"DM Mono",monospace; white-space:nowrap;'>{i["cover"]}</td>
                        <td style='padding:11px 10px;'><span style='background:{color}15; color:{color}; border-radius:4px; padding:2px 8px; font-size:10px;'>{i["type"]}</span></td>
                        <td style='padding:11px 10px; font-size:11px; color:#C8A84B;'>{i["who"]}</td>
                        <td style='padding:11px 10px; font-size:11px; color:#7A9BBF; font-family:"DM Mono",monospace;'>{i["until"]}</td>
                    </tr>""" for i in filtered)}
                </tbody>
            </table>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — ALERTS
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "🔔  Alerts":
    st.markdown('<div style="font-size:32px; color:#EAE3D6; margin-bottom:4px;">Alerts & Action Items</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:\'DM Mono\',monospace; font-size:11px; color:#7A9BBF; margin-bottom:20px;">As of {datetime.now().strftime("%d %B %Y")} · MOM: 9 March 2026 · Vikram Batra · {len(ALERTS)} active items</div>', unsafe_allow_html=True)

    # Pending from client
    st.markdown('<div style="font-size:11px; color:#D45858; font-weight:600; margin-bottom:10px; letter-spacing:1.5px; text-transform:uppercase;">⏳ Pending from Client</div>', unsafe_allow_html=True)
    pending = [
        "FD list with amounts and maturity dates — to avoid premature exit penalties",
        "Life insurance policy PDFs — for cover assessment and surrender analysis",
        "Spouse (Ritu Narang) DOB and medical history — for HDFC ERGO Optima Secure final quote",
    ]
    for p in pending:
        st.markdown(f"""
        <div style='background:#0C1A2E; border:1px solid #D4585840; border-left:3px solid #D45858;
            border-radius:0 10px 10px 0; padding:12px 18px; margin-bottom:8px;
            display:flex; align-items:flex-start; gap:12px;'>
            <span style='font-size:16px; flex-shrink:0;'>📋</span>
            <span style='font-size:13px; color:#7A8A9E; line-height:1.6;'>{p}</span>
        </div>
        """, unsafe_allow_html=True)

    # Pending from Vikram
    st.markdown('<div style="font-size:11px; color:#4EAF7A; font-weight:600; margin-top:18px; margin-bottom:10px; letter-spacing:1.5px; text-transform:uppercase;">✅ Pending from Vikram Batra</div>', unsafe_allow_html=True)
    vikram = [
        "5-Year Projection: New roadmap showing ₹10 Cr+ target with ₹7L/month SIP",
        "Deployment Plan: Specific allocation for remaining ₹2L of ₹7L monthly surplus",
        "Insurance Comparison: Side-by-side ₹25L vs ₹50L HDFC ERGO Optima Secure plans",
    ]
    for v in vikram:
        st.markdown(f"""
        <div style='background:#0C1A2E; border:1px solid #4EAF7A40; border-left:3px solid #4EAF7A;
            border-radius:0 10px 10px 0; padding:12px 18px; margin-bottom:8px;
            display:flex; align-items:flex-start; gap:12px;'>
            <span style='font-size:16px; flex-shrink:0;'>📊</span>
            <span style='font-size:13px; color:#7A8A9E; line-height:1.6;'>{v}</span>
        </div>
        """, unsafe_allow_html=True)

    # All alerts
    st.markdown('<div style="font-size:11px; color:#A0B8D0; font-weight:600; margin-top:18px; margin-bottom:10px; letter-spacing:1.5px; text-transform:uppercase;">🔔 All Alerts & Reminders</div>', unsafe_allow_html=True)
    for a in ALERTS:
        st.markdown(f"""
        <div style='background:#0C1A2E; border:1px solid #1C3050; border-left:3px solid {a["color"]};
            border-radius:0 10px 10px 0; padding:14px 18px; margin-bottom:10px;
            display:flex; align-items:flex-start; gap:12px;'>
            <span style='font-size:18px; flex-shrink:0;'>{a["icon"]}</span>
            <span style='font-size:13px; color:#7A8A9E; line-height:1.6;'>{a["msg"]}</span>
        </div>
        """, unsafe_allow_html=True)

    # MOM summary
    st.markdown(f"""
    <div style='background:#0C1A2E; border:1px solid #2A3F58; border-radius:12px;
        padding:18px 22px; margin-top:16px;'>
        <div style='font-size:11px; color:#7A9BBF; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:12px;'>
            MOM Summary — 9 March 2026 · Vikram Batra</div>
        <div style='font-size:12px; color:#7A8A9E; line-height:1.9;'>
            <strong style='color:#C8A84B;'>Strategy:</strong> "The 5-Year Sprint" — ₹10 Cr+ empire by Age 60<br>
            <strong style='color:#C8A84B;'>Surplus:</strong> ₹7,00,000/month investible (updated)<br>
            <strong style='color:#C8A84B;'>Wedding:</strong> ₹70L FD → Arbitrage · target ~₹95L in 5 years · no further SIP needed beyond ₹50K/mo<br>
            <strong style='color:#C8A84B;'>Buffer:</strong> ₹60L savings held as 8-month cushion for business volatility<br>
            <strong style='color:#C8A84B;'>Gold:</strong> ₹70L physical gold officially integrated into the wealth plan<br>
            <strong style='color:#C8A84B;'>Insurance:</strong> HDFC ERGO Mediclaim Optima Secure · ₹25L vs ₹50L cover — quote comparison pending
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding:32px 0 0; font-size:10px; color:#7A9BBF; line-height:1.8;'>
    For illustrative purposes only · Values as of March 2026 · MOM dated 9 March 2026<br>
    Equity projections at 9–13% CAGR · Debt at 6% CAGR · Inflation assumed 6% p.a. · Not financial advice<br>
    Vikram Batra · Wealth Strategist
</div>
""", unsafe_allow_html=True)
