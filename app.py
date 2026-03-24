import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import time

# --- 1. CONFIG & SYSTEM THEME ---
st.set_page_config(page_title="Reya Pro Terminal", page_icon="📈", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global Styles */
    .stApp { background-color: #050505 !important; font-family: 'Inter', sans-serif !important; color: #F5F5F5 !important; }
    header {visibility: hidden;}
    
    /* Professional Card style */
    .pro-card {
        background: #0E0E10;
        border: 1px solid #1C1C1E;
        border-radius: 4px; /* Более острые углы выглядят строже */
        padding: 20px;
        margin-bottom: 15px;
    }
    
    /* Typography */
    .label-text { color: #666; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }
    .value-text { font-family: 'JetBrains Mono'; font-weight: 500; color: #FFF; font-size: 1.2rem; }
    .highlight-green { color: #4BFF99; }
    
    /* Stats Bar */
    .stats-bar {
        display: flex; gap: 30px; padding: 10px 20px; background: #000; border-bottom: 1px solid #1C1C1E; margin-bottom: 20px;
    }
    
    /* Custom Sidebar */
    [data-testid="stSidebar"] { background-color: #080808 !important; border-right: 1px solid #1C1C1E !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. PRE-LOAD (SIMULATED LIVE DATA) ---
l2_tps = 42.5
gas_price = 0.0001
block_height = 19450212

# --- 3. HEADER: L2 NETWORK HEALTH ---
st.markdown(f"""
<div class="stats-bar">
    <div><span class="label-text">Network:</span> <span class="highlight-green" style="font-size:0.8rem;">Reya L2 (Mainnet)</span></div>
    <div><span class="label-text">TPS:</span> <span class="value-text" style="font-size:0.8rem;">{l2_tps}</span></div>
    <div><span class="label-text">Gas:</span> <span class="value-text" style="font-size:0.8rem;">{gas_price} srUSD</span></div>
    <div><span class="label-text">Block:</span> <span class="value-text" style="font-size:0.8rem;">{block_height}</span></div>
</div>
""", unsafe_allow_html=True)

# --- 4. SIDEBAR CONTEXT ---
with st.sidebar:
    st.markdown("### 💠 Portfolio Manager")
    st.markdown("""<div style="background:#111; padding:15px; border-radius:4px;">
        <p class="label-text">Equity Value</p>
        <p class="value-text">$42,105.50</p>
        <p class="label-text" style="margin-top:10px;">Available Margin</p>
        <p class="value-text" style="color:#4BFF99;">$38,400.12</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    mode = st.radio("Terminal Mode", ["Margin Analysis", "Vault Strategy", "XP Farming"])
    st.divider()
    st.caption("v2.4.1-Stable | Security: Audited by Halborn")

# --- 5. MAIN INTERFACE GRID ---
col_main, col_side = st.columns([2.5, 1])

with col_main:
    st.markdown("<h2 style='margin-top:0;'>Advanced Margin Simulator</h2>", unsafe_allow_html=True)
    
    # Сетка параметров
    with st.container():
        st.markdown('<div class="pro-card">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            asset = st.selectbox("Market", ["BTC/srUSD", "ETH/srUSD", "SOL/srUSD"])
            entry = st.number_input("Entry Price", value=65000)
        with c2:
            st.markdown('<p class="label-text" style="margin-bottom:23px;">Direction</p>', unsafe_allow_html=True)
            direction = st.segmented_control("Dir", ["Long", "Short"], selection_mode="single", default="Long")
        with c3:
            leverage = st.slider("Leverage (x)", 1, 50, 10)
        with c4:
            collateral = st.number_input("Margin ($)", value=5000)
        st.markdown('</div>', unsafe_allow_html=True)

    # Визуализация: Liquidation Heatmap Concept
    st.markdown("### Liquidation Risk Distribution")
    
    # Генерация данных графика
    price_range = np.linspace(entry * 0.8, entry * 1.2, 50)
    # Симуляция "кластеров" ликвидаций на рынке
    liq_clusters = np.exp(-((price_range - (entry*0.9))**2) / (2 * (entry*0.02)**2)) * 100
    
    fig = go.Figure()
    # Добавляем тепловую карту (Area)
    fig.add_trace(go.Scatter(x=price_range, y=liq_clusters, fill='tozeroy', 
                             name="Liq Depth", line=dict(color='#FF3B69', width=0),
                             fillcolor='rgba(255, 59, 105, 0.1)'))
    
    # Ваша цена ликвидации
    my_liq = entry * (1 - 1/leverage + 0.05) if direction == "Long" else entry * (1 + 1/leverage - 0.05)
    fig.add_vline(x=my_liq, line_dash="dash", line_color="#4BFF99", 
                  annotation_text="YOUR LIQUIDATION", annotation_font_color="#4BFF99")
    
    fig.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=300, margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(showgrid=False, title="Asset Price"), yaxis=dict(showgrid=False, title="Liquidation Volume")
    )
    st.plotly_chart(fig, use_container_width=True)

with col_side:
    st.markdown("### Execution Details")
    
    # Блок симуляции транзакции
    st.markdown(f"""
    <div class="pro-card">
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
            <span class="label-text">Est. Liq Price</span>
            <span class="value-text" style="color:#FF3B69; font-size:1rem;">${my_liq:,.2f}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
            <span class="label-text">Margin Required</span>
            <span class="value-text" style="font-size:1rem;">{collateral:,.2f} srUSD</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
            <span class="label-text">Network Fee</span>
            <span class="value-text" style="font-size:1rem;">$0.42</span>
        </div>
        <hr style="border-color:#1C1C1E">
        <div style="display:flex; justify-content:space-between;">
            <span class="label-text">Projected XP</span>
            <span class="value-text highlight-green" style="font-size:1rem;">+14.2 / hr</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("SIMULATE ON-CHAIN ACTION"):
        with st.status("Simulating transaction on Reya L2..."):
            st.write("Fetching Oracle prices (Pyth Network)...")
            time.sleep(0.8)
            st.write("Calculating Cross-Margin requirements...")
            time.sleep(0.8)
            st.write("Verifying solvency...")
        st.success("Simulation passed. Ready for execution.")

# --- 6. FOOTER: EXPORT & LOGS ---
log_col, exp_col = st.columns([2, 1])
with log_col:
    st.markdown("""<p class="label-text">System Logs</p>
    <div style="background:#000; padding:10px; border:1px solid #1C1C1E; height:80px; overflow-y:auto; font-family:'JetBrains Mono'; font-size:0.7rem; color:#4BFF99; opacity:0.6;">
        [09:12:01] INFO: Connected to Reya Indexer (Mainnet)<br>
        [09:12:05] WARN: High volatility detected in SOL markets<br>
        [09:12:10] INFO: Account 0x71... verified for XP Multiplier 1.2x
    </div>""", unsafe_allow_html=True)

with exp_col:
    st.markdown('<p class="label-text">Report Export</p>', unsafe_allow_html=True)
    st.download_button("GENERATE PDF AUDIT", data="Risk Report Content", file_name="reya_risk_report.txt")
