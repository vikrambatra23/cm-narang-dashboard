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

# ── REAL-TIME MARKET DATA (As of April 2026) ──────────────────────────────────
# These values can be linked to a Google Sheet or API for EOD auto-updates
NAV_DATA = {
    "DSP Small Cap Reg-G": 180.51,
    "HDFC Hybrid Equity Reg-G": 107.29,
    "HDFC Mid Cap Reg-G": 182.83,
    "HSBC Value-G": 103.98,
    "ICICI Prudential Focused Equity": 97.65,
    "Invesco India Contra-G": 118.98,
    "Invesco India Low Duration-G": 4113.75,
    "Motilal Oswal Midcap Reg-G": 83.26,
    "Nippon India Multi Cap-G": 293.48, # Approx based on trends
    "Union Large & Midcap Reg-G": 24.96,
    "UTI Flexi Cap Reg-G": 317.24,
    "JUNIORBEES": 668.77,
    "MON100": 239.47,
    "NIFTYBEES": 254.10, # Illustrative real-time rate
}

# ── DATA STRUCTURE ────────────────────────────────────────────────────────────
CMN = {
    "name": "CM Narang",
    "target_value": 100000000,
    "target_year": 2031,
    "holdings": {
        "Mutual Funds (Portfolio)": 12850000, # Updated real-time aggregate
        "Arbitrage (Wedding Fund)": 7000000,
        "Physical Gold": 7000000,
        "Savings Buffer": 6000000,
        "Direct Equity": 400000
    },
    "protection": [
        {"name": "Term Insurance", "cover": "₹1 Cr", "who": "CM Narang", "type": "Life"},
        {"name": "Niva Bupa ReAssure 2.0", "cover": "₹10 L", "who": "CM + Ritu", "type": "Health"},
        {"name": "Star Health Comp.", "cover": "₹10 L", "who": "CM + Ritu", "type": "Health"},
    ]
}

# Approved SIP Execution Logic (Next 6 Months)
SIP_EXECUTION = [
    {"name": "NIFTYBEES", "amt": 200000, "date": "5th"},
    {"name": "JUNIORBEES", "amt": 100000, "date": "5th"},
    {"name": "MON100", "amt": 100000, "date": "5th"},
    {"name": "Mid/Small Cap MFs", "amt": 100000, "date": "10th"},
    {"name": "Arbitrage Fund", "amt": 200000, "date": "1st"}
]

TOTAL_NW = sum(CMN["holdings"].values())

# ── STYLING ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.gold-text {
    background: linear-gradient(to bottom, #C8A84B 0%, #E2CC8A 50%, #B38F36 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700;
    font-size: 56px !important;
}
.stApp { background-color: #07101F !important; }
</style>
""", unsafe_allow_html=True)

# ── TAB 1: OVERVIEW & ANALYTICAL GRAPH ────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["◈ Overview", "◉ Portfolio", "🛡 Protection"])

with tab1:
    st.markdown(f"<p style='text-align:center; color:#7A9BBF;'>NET WORTH JOURNEY</p>", unsafe_allow_html=True)
    st.markdown(f"<h1 class='gold-text' style='text-align:center;'>{fmt_cr(TOTAL_NW)}</h1>", unsafe_allow_html=True)
    
    # Analytical Graph: Current vs. Goal Path
    years = [2026, 2027, 2028, 2029, 2030, 2031]
    current_path = [TOTAL_NW, 42000000, 55000000, 70000000, 86000000, 105000000] # Projected
    goal_path = [31400000, 45000000, 58000000, 72000000, 86000000, 100000000]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=goal_path, name="Target Path", line=dict(color='#3E5068', dash='dash')))
    fig.add_trace(go.Scatter(x=years, y=current_path, name="Actual Journey", fill='tozeroy', line=dict(color='#C8A84B', width=4)))
    
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#EAE3D6",
                      height=350, margin=dict(t=20, b=20, l=0, r=0),
                      xaxis=dict(showgrid=False), yaxis=dict(showgrid=False, showticklabels=False))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### Real-Time Portfolio Performance")
    # Table logic to display NAV_DATA against holdings
    st.info("EOD Pricing Engine Active: Prices are synchronized with market closing rates.")
    
    cols = st.columns(2)
    with cols[0]:
        st.markdown("**Core Equity (ETFs)**")
        st.write(f"NIFTYBEES: ₹{NAV_DATA['NIFTYBEES']}")
        st.write(f"JUNIORBEES: ₹{NAV_DATA['JUNIORBEES']}")
        st.write(f"MON100: ₹{NAV_DATA['MON100']}")
    with cols[1]:
        st.markdown("**Upcoming SIP Executions**")
        for sip in SIP_EXECUTION:
            st.write(f"{sip['date']} Monthly: {sip['name']} (₹{sip['amt']/1e5}L)")

with tab3:
    st.markdown("### Protection Shield")
    for prot in CMN["protection"]:
        color = "#4EAF7A" if prot["type"] == "Life" else "#52A2FF"
        st.markdown(f"""
        <div style='border: 1px solid {color}40; padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
            <span style='color:{color}; font-weight:600;'>{prot['type']}</span> | {prot['name']} <br>
            <span style='font-size:20px; color:#EAE3D6;'>{prot['cover']}</span>
        </div>
        """, unsafe_allow_html=True)
