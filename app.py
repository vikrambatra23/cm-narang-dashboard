# ── HEADER & NAVIGATION ───────────────────────────────────────────────────────
# Using a column layout to prevent title and subtitle overlap
col_h1, col_h2 = st.columns([2, 1])

with col_h1:
    st.markdown("""
        <h1 style='
            background: linear-gradient(90deg, #C8A84B, #E2CC8A);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            font-size: 38px;
            margin-bottom: 0px;
            padding-bottom: 0px;
        '>Chandra Mohan Narang</h1>
        <p style='
            color: #7A9BBF;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-top: -5px;
        '>Family Office Dashboard</p>
    """, unsafe_allow_html=True)

with col_h2:
    st.markdown(f"""
        <div style='text-align: right; padding-top: 20px;'>
            <p style='color: #5C7089; font-size: 11px; margin-bottom: 0;'>Valuation Date</p>
            <p style='color: #EAE3D6; font-size: 14px; font-weight: 500;'>{pd.Timestamp.now().strftime('%d %B, %Y')}</p>
        </div>
    """, unsafe_allow_html=True)

# Navigation bar remains untouched to maintain your original layout
tab = st.radio("nav", ["Overview", "Portfolio", "Protection", "Actions"], horizontal=True, label_visibility="collapsed")
st.markdown("<hr style='margin-top: 5px; border: 1px solid #1C3050;'>", unsafe_allow_html=True)
