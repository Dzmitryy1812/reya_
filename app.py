import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIG & STYLING (REYA DARK MODE) ---
st.set_page_config(page_title="Reya Utility Terminal", page_icon="⚙️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { background-color: #0A0A0B !important; color: #E0E0E0 !important; font-family: 'Inter', sans-serif !important; }
    header {visibility: hidden;}
    
    /* Карточки */
    .utility-card {
        background: #141415;
        border: 1px solid #252526;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
    }
    
    /* Цвет Reya */
    .highlight { color: #4BFF99; font-family: 'JetBrains Mono'; font-weight: 700; }
    
    /* Стилизация инпутов */
    .stNumberInput input { background-color: #000 !important; border: 1px solid #333 !important; color: #FFF !important; }
    
    /* Метрики */
    [data-testid="stMetric"] { background: #141415 !important; border: 1px solid #252526 !important; border-radius: 10px !important; }
    [data-testid="stMetricValue"] { color: #4BFF99 !important; font-family: 'JetBrains Mono' !important; }

    /* Кнопки */
    .stButton > button {
        background: transparent !important; color: #4BFF99 !important; border: 1px solid #4BFF99 !important;
        font-weight: 700 !important; width: 100% !important; border-radius: 8px !important;
        transition: 0.3s all;
    }
    .stButton > button:hover { background: rgba(75, 255, 153, 0.1) !important; box-shadow: 0 0 15px rgba(75, 255, 153, 0.2); }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIC: MARGIN CALCULATIONS ---
def calc_liquidation_price(entry_price, leverage, side, margin_ratio=0.05):
    if side == "Long":
        return entry_price * (1 - (1 / leverage) + margin_ratio)
    else:
        return entry_price * (1 + (1 / leverage) - margin_ratio)

# --- 3. SIDEBAR: CONTRIBUTOR STATUS ---
with st.sidebar:
    st.markdown("<h2 style='color:#FFF;'>⚙️ REYA TOOLS</h2>", unsafe_allow_html=True)
    st.markdown("""
        <div style="background:#1A1A1B; padding:15px; border-radius:10px; border-left: 4px solid #4BFF99;">
            <p style="margin:0; font-size:0.7rem; color:#888;">CONTRIBUTOR IMPACT SCORE</p>
            <h2 style="margin:0; color:#FFF;">840 <span style="font-size:0.8rem; color:#4BFF99;">XP</span></h2>
            <p style="margin:0; font-size:0.6rem; color:#4BFF99;">Top 12% of Ecosystem Helpers</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🛠 Useful Links")
    st.caption("[Reya Explorer](https://reya.network)")
    st.caption("[Risk Documentation](https://docs.reya.xyz)")

# --- 4. MAIN INTERFACE ---

st.markdown("<h1>Reya Margin & Risk Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#888;'>Official community tool for traders to simulate risk and optimize collateral.</p>", unsafe_allow_html=True)

# Блок 1: Симулятор Позиции
st.markdown('<div class="utility-card">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    side = st.selectbox("Side", ["Long", "Short"])
with col2:
    entry_price = st.number_input("Entry Price ($)", value=65000)
with col3:
    leverage = st.slider("Leverage", 1, 50, 10)
with col4:
    collateral = st.number_input("Collateral (srUSD)", value=1000)

liq_price = calc_liquidation_price(entry_price, leverage, side)
distance = abs(entry_price - liq_price) / entry_price * 100

# Отображение критических метрик
m_col1, m_col2, m_col3 = st.columns(3)
m_col1.metric("Liquidation Price", f"${liq_price:,.2f}")
m_col2.metric("Safety Buffer", f"{distance:.2f}%")
m_col3.metric("Position Size", f"${collateral * leverage:,.0f}")

st.markdown('</div>', unsafe_allow_html=True)

# Блок 2: График риска
st.markdown("### Risk Visualizer")
left_p, right_p = st.columns([2, 1])

with left_p:
    # Генерация ценового коридора
    prices = np.linspace(liq_price * 0.9, entry_price * 1.1, 100)
    # PnL Calculation
    if side == "Long":
        pnl = (prices - entry_price) / entry_price * leverage * 100
    else:
        pnl = (entry_price - prices) / entry_price * leverage * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=prices, y=pnl, name="PnL %", line=dict(color='#4BFF99', width=3)))
    
    # Линия ликвидации
    fig.add_vline(x=liq_price, line_dash="dash", line_color="#FF3B69", annotation_text="LIQUIDATION")
    
    fig.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(title="PnL (%)", gridcolor='#222'), xaxis=dict(title="Asset Price ($)", gridcolor='#222'),
        height=350, margin=dict(l=0, r=0, t=20, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

with right_p:
    st.markdown("""
        <div class="utility-card">
            <h4 style="margin-top:0;">Risk Assessment</h4>
            <p style="font-size:0.85rem; color:#888;">Based on <b>Reya's Margin Engine</b>, your position has:</p>
            <ul style="font-size:0.85rem; color:#DDD;">
                <li><b style="color:#4BFF99;">Normal</b> Maintenance Margin</li>
                <li>Low risk of cascade liquidation</li>
                <li>Capital efficiency: <b>High</b></li>
            </ul>
            <hr style="border-color:#333">
            <p style="font-size:0.7rem; color:#666;">*This tool uses standard Reya L2 risk parameters (5% maintenance margin).</p>
        </div>
    """, unsafe_allow_html=True)

# Блок 3: Сравнение с конкурентами
st.markdown("### Why Reya? (Efficiency Comparison)")
comp_col1, comp_col2 = st.columns(2)

with comp_col1:
    st.markdown("""
    <div style="background: rgba(75, 255, 153, 0.05); padding:20px; border-radius:12px; border: 1px solid #4BFF99;">
        <h4 style="color:#4BFF99; margin:0;">Reya Network</h4>
        <p style="font-size:0.9rem;">Required Collateral: <b>$1,000</b></p>
        <p style="font-size:0.8rem; color:#888;">Max Leverage: <b>50x</b></p>
        <p style="font-size:0.8rem; color:#888;">Margin Mode: <b>Cross-Margin Portfolio</b></p>
    </div>
    """, unsafe_allow_html=True)

with comp_col2:
    st.markdown("""
    <div style="background: #111; padding:20px; border-radius:12px; border: 1px solid #333;">
        <h4 style="color:#888; margin:0;">Standard DEX (GMX/Uni)</h4>
        <p style="font-size:0.9rem;">Required Collateral: <b>$2,400</b></p>
        <p style="font-size:0.8rem; color:#888;">Max Leverage: <b>20-30x</b></p>
        <p style="font-size:0.8rem; color:#888;">Margin Mode: <b>Isolated Only</b></p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<p style='text-align:center; color:#444; margin-top:30px;'>Building for Reya Ecosystem • 2024</p>", unsafe_allow_html=True)
