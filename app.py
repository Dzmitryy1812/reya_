import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- 1. SYSTEM CONFIG ---
st.set_page_config(page_title="Reya | ecosystem_hub", page_icon="⚡", layout="wide")

# --- 2. THE "REYA PURE" CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600&family=JetBrains+Mono:wght@400;500&display=swap');

    .stApp {
        background-color: #050505 !important;
        color: #FFFFFF !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    header {visibility: hidden;}
    footer {visibility: hidden;}

    .reya-card {
        background: #0D0D0E;
        border: 1px solid #1A1A1B;
        border-radius: 4px;
        padding: 24px;
        margin-bottom: 20px;
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.03em !important;
    }
    
    .label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #555557;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .mono-data {
        font-family: 'JetBrains Mono', monospace;
        color: #FFFFFF;
        font-weight: 500;
    }
    .neon-text { color: #4BFF99 !important; }

    .stButton > button {
        background-color: transparent !important;
        color: #4BFF99 !important;
        border: 1px solid #4BFF99 !important;
        border-radius: 2px !important;
        font-family: 'JetBrains Mono' !important;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #4BFF99 !important;
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HEADER NAVIGATION ---
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0px 40px 0px; border-bottom: 1px solid #1A1A1B; margin-bottom: 40px;">
    <div style="display: flex; align-items: center; gap: 15px;">
        <div style="width: 32px; height: 32px; background: #4BFF99; border-radius: 4px;"></div>
        <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 1.2rem;">REYA <span style="color: #555;">ECOSYSTEM</span></div>
    </div>
    <div style="display: flex; gap: 30px; font-size: 0.8rem; font-family: 'JetBrains Mono'; color: #555;">
        <div>NETWORK / <span style="color: #FFF;">MAINNET-L2</span></div>
        <div>STATUS / <span style="color: #4BFF99;">STABLE</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<p class='label'>User Contribution</p>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: #0D0D0E; padding: 20px; border: 1px solid #1A1A1B; border-radius: 4px;">
        <p style="font-size: 0.7rem; color: #555; margin:0;">IMPACT POINTS</p>
        <p class="mono-data neon-text" style="font-size: 1.8rem; margin:0;">1,420.50</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.radio("SELECT MODULE", ["Risk Analyzer", "Margin Efficiency", "Rewards Tracker"])

# --- 5. MAIN CONTENT ---
col_left, col_right = st.columns([1.8, 1])

with col_left:
    st.markdown("<h3>Protocol Analysis</h3>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown("<div class='reya-card'><p class='label'>Total TVL</p><p class='mono-data' style='font-size:1.4rem;'>$241.8M</p></div>", unsafe_allow_html=True)
    with m2:
        st.markdown("<div class='reya-card'><p class='label'>Current APY</p><p class='mono-data neon-text' style='font-size:1.4rem;'>14.22%</p></div>", unsafe_allow_html=True)
    with m3:
        st.markdown("<div class='reya-card'><p class='label'>Active Traders</p><p class='mono-data' style='font-size:1.4rem;'>12.1K</p></div>", unsafe_allow_html=True)

    # Исправленная строка здесь!
    st.markdown("<div class='reya-card'>", unsafe_allow_html=True)
    st.markdown("<p class='label'>Liquidity Depth Simulator</p>", unsafe_allow_html=True)
    
    # График
    x = np.linspace(0, 10, 100)
    y = np.sin(x) * 5 + 20
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, fill='tozeroy', line=dict(color='#4BFF99', width=2), fillcolor='rgba(75, 255, 153, 0.05)'))
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<h3>Margin Utility</h3>", unsafe_allow_html=True)
    st.markdown("<div class='reya-card'>", unsafe_allow_html=True)
    st.markdown("<p class='label'>Select Market</p>", unsafe_allow_html=True)
    st.selectbox("Asset", ["BTC/srUSD", "ETH/srUSD"], label_visibility="collapsed")
    st.markdown("<p class='label' style='margin-top:20px;'>Position Leverage</p>", unsafe_allow_html=True)
    st.slider("Lev", 1, 50, 10, label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("CALCULATE RISK"):
        st.info("Simulation complete.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- 6. FOOTER ---
st.markdown("""
<div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #1A1A1B; text-align: center; opacity: 0.3;">
    <p style="font-family: 'JetBrains Mono'; font-size: 0.7rem;">BUILD_ID: REYA_ALPHA_2024</p>
</div>
""", unsafe_allow_html=True)
