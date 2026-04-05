import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Wealth Terminal · CM Narang", page_icon="◈", layout="wide")

# ── DARK ANALYTICAL STYLING ───────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #050A14; }
    .stApp { background-color: #050A14 !important; }
    #MainMenu, footer, header { visibility: hidden; }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] { font-family: 'JetBrains Mono'; color: #E2CC8A !important; font-size: 28px !important; }
    [data-testid="stMetricLabel"] { color: #7A9BBF !important; text-transform: uppercase; letter-spacing: 1px; font-size: 10px !important; }

    .gold-header {
        background: linear-gradient(90deg, #C8A84B, #E2CC8A);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 700; font-size: 48px; letter-spacing: -1px;
    }
</style>
""", unsafe_allow_html=True)

# ── DATA ENGINE ───────────────────────────────────────────────────────────────
URL = "https://docs.google.com/spreadsheets/d/1PZACfddE3VkcCWqYD-_0j_ERaBUT1SBQqPN63Vylvy0/export?format=csv"
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def get_data():
    # Load Portfolio
    df = conn.read(spreadsheet=URL)
    df['Val_Num'] = pd.to_numeric(df['Current Value'].astype(str).replace('[₹,L,Cr, ,]', '', regex=True), errors='coerce').fillna(0)
    assets = df[~df['Asset Name'].str.contains('Total|TOTAL|Sum', na=False)]
    assets = assets[assets['Val_Num'] > 0]
    
    # Load History (Assumes a tab named 'History' exists)
    try:
        hist = conn.read(spreadsheet=URL, worksheet="History")
        hist['Date'] = pd.to_datetime(hist['Date'])
        hist['Net Worth'] = pd.to_numeric(hist['Net Worth'])
    except:
        hist = pd.DataFrame(columns=['Date', 'Net Worth'])
        
    return assets, hist

assets, history = get_data()
total_nw = assets['Val_Num'].sum()
target = 100000000 # 10 Cr Goal

# ── HEADER & NAVIGATION ───────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([2, 1])
with col_h1:
    st.markdown("<h1 class='gold-header'>Wealth Terminal</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#5C7089; margin-top:-20px;'>CHANDRA MOHAN NARANG • {pd.Timestamp.now().strftime('%d %b %Y')}</p>", unsafe_allow_html=True)

tab = st.radio("nav", ["Strategic Overview", "Analytics", "Protection", "Actions"], horizontal=True, label_visibility="collapsed")
st.markdown("---")

# ── TAB 1: STRATEGIC OVERVIEW ─────────────────────────────────────────────────
if tab == "Strategic Overview":
    # Row 1: The 10Cr Goal Gauge
    st.markdown("<p style='color:#C8A84B; font-weight:600; letter-spacing:1px;'>GOAL PROGRESS: 10 CR JOURNEY</p>", unsafe_allow_html=True)
    
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = total_nw / 10000000, # Show in Cr
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Current (Cr)", 'font': {'size': 14, 'color': '#7A9BBF'}},
        gauge = {
            'axis': {'range': [None, 10], 'tickwidth': 1, 'tickcolor': "#1C3050"},
            'bar': {'color': "#C8A84B"},
            'bgcolor': "#0C1A2E",
            'borderwidth': 2,
            'bordercolor': "#1C3050",
            'steps': [{'range': [0, 10], 'color': '#0C1A2E'}],
            'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': 10}
        }
    ))
    fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=250, margin=dict(t=30, b=0, l=10, r=10))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Row 2: Analytical Pie & Progress Path
    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        st.markdown("<p style='font-size:11px; color:#7A9BBF;'>ASSET ALLOCATION</p>", unsafe_allow_html=True)
        # Improved Pie Chart
        fig_pie = px.pie(assets, values='Val_Num', names='Category', hole=0.7,
                         color_discrete_sequence=px.colors.sequential.Gold_r)
        fig_pie.update_layout(showlegend=True, paper_bgcolor='rgba(0,0,0,0)', 
                              legend=dict(font=dict(color="#7A9BBF", size=10), orientation="h", y=-0.2),
                              margin=dict(t=0, b=0, l=0, r=0))
        fig_pie.update_traces(textinfo='percent', textfont_size=10, marker=dict(line=dict(color='#050A14', width=2)))
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.markdown("<p style='font-size:11px; color:#7A9BBF;'>NET WORTH TRAJECTORY</p>", unsafe_allow_html=True)
        if not history.empty:
            fig_trend = px.line(history, x="Date", y="Net Worth", markers=True)
            fig_trend.update_traces(line_color='#C8A84B', fill='tozeroy', fillcolor='rgba(200,168,75,0.05)')
            fig_trend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                    height=300, margin=dict(t=10, b=0, l=0, r=0),
                                    xaxis=dict(showgrid=False, color="#5C7089"), yaxis=dict(showgrid=True, gridcolor="#1C3050", color="#5C7089"))
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("To see the trend, add a 'History' tab in your Google Sheet with 'Date' and 'Net Worth' columns.")

# Rest of the tabs (Portfolio, Protection, Actions) remain as per previous logic
