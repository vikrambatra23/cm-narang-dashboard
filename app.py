import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# ── NEW: CONNECT TO GOOGLE SHEETS ─────────────────────────────────────────────
# This replaces your old 'CMN' dictionary
conn = st.connection("gsheets", type=GSheetsConnection)

def get_live_data():
    # Fetch Portfolio and Market Rates
    df_portfolio = conn.read(worksheet="Portfolio", ttl=0) # ttl=0 means NO CACHE (Real-time)
    df_rates = conn.read(worksheet="Market_Rates", ttl=0)
    
    # Merge them to calculate current value
    df_merged = pd.merge(df_portfolio, df_rates, on="Asset Name")
    df_merged['Current Value'] = df_merged['Units Held'] * df_merged['Current NAV/Price']
    
    return df_merged

# ── UPDATE DASHBOARD ──────────────────────────────────────────────────────────
try:
    live_df = get_live_data()
    TOTAL_NW = live_df['Current Value'].sum() + 13000000 # Adding Gold/Buffer (Fixed assets)
except:
    st.error("Connection to Google Sheets failed. Check your Secret Keys.")
    TOTAL_NW = 32850000 # Fallback
