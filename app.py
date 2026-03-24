import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- 1. SYSTEM CONFIG ---
st.set_page_config(page_title="Reya | ecosystem_hub", page_icon="⚡", layout="wide")

# --- 2. THE "REYA PURE" CSS (Visual Identity) ---
st.markdown("""
<style>
    /* Импорт фирменных шрифтов */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Глобальный сброс стилей */
    .stApp {
        background-color: #050505 !important;
        color: #FFFFFF !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    /* Скрытие стандартных элементов Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0);}

    /* СТИЛЬ КАРТОЧЕК (REYA BORDER) */
    .reya-card {
        background: #0D0D0E;
        border: 1px solid #1A1A1B;
        border-radius: 4px; /* Острые профессиональные углы */
        padding: 24px;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .reya-card:hover {
        border-color: #4BFF99;
        box-shadow: 0 0 30px rgba(75, 255, 153, 0.03);
    }

    /* ЗАГОЛОВКИ */
    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.03em !important;
        margin-bottom: 1rem !important;
    }
    
    .label {
        font-family: 'Space Grotesk';
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #555557;
        font-weight: 600;
        margin-bottom: 8px;
    }

    /* ЧИСЛА И ДАННЫЕ */
    .mono-data {
        font-family: 'JetBrains Mono', monospace;
        color: #FFFFFF;
        font-size: 1.4rem;
        font-weight: 500;
    }
    .neon-text { color: #4BFF99 !important; }

    /* КАСТОМНЫЕ КНОПКИ (NEON STROKE) */
    .stButton > button {
        background-color: transparent !important;
        color: #4BFF99 !important;
        border: 1px solid #4BFF99 !important;
        padding: 10px 24px !important;
        border-radius: 2px !important;
        font-family: 'JetBrains Mono' !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        transition: 0.2s all !important;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #4BFF99 !important;
        color: #000000 !important;
        box-shadow: 0 0 20px rgba(75, 255, 153, 0.4) !important;
    }

    /* Ввод данных (Input Fields) */
    .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #000000 !important;
        border: 1px solid #1A1A1B !important;
        color: white !important;
        border-radius: 2px !important;
    }

    /* Кастомный Сайдбар */
    [data-testid="stSidebar"] {
        background-color: #080809 !important;
        border-right: 1px solid #1A1A1B !important;
        width: 300px !important;
    }

    /* Полоса прогресса */
    .stProgress > div > div > div > div { background-color: #4BFF99 !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. HEADER & NAVIGATION ---
# Создаем чистый Navbar в стиле Reya
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0px 40px 0px; border-bottom: 1px solid #1A1A1B; margin-bottom: 40px;">
    <div style="display: flex; align-items: center; gap: 15px;">
        <div style="width: 32px; height: 32px; background: #4BFF99; border-radius: 4px;"></div>
        <div style="font-family: 'Space Grotesk'; font-weight: 600; font-size: 1.2rem; letter-spacing: -0.5px;">REYA <span style="color: #555;">ECOSYSTEM</span></div>
    </div>
    <div style="display: flex; gap: 30px; font-size: 0.8rem; font-family: 'JetBrains Mono'; color: #555;">
        <div>NETWORK / <span style="color: #FFF;">MAINNET-L2</span></div>
        <div>STATUS / <span style="color: #4BFF99;">STABLE</span></div>
        <div>BLOCK / <span style="color: #FFF;">19,451,023</span></div>
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
        <p style="font-size: 0.6rem; color: #555; margin-top:10px;">GLOBAL RANK: <span style="color:#FFF;">#842</span></p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    menu = st.radio("SELECT MODULE", ["Risk Analyzer", "Margin Efficiency", "Rewards Tracker"])
    st.markdown("<p style='font-size: 0.6rem; color: #333; margin-top: 100px;'>v2.4.1 Build 829<br>Reya Labs (c) 2024</p>", unsafe_allow_html=True)

# --- 5. MAIN CONTENT ---
col_left, col_right = st.columns([1.8, 1])

with col_left:
    st.markdown("<h3>Protocol Analysis</h3>", unsafe_allow_html=True)
    
    # Сетка метрик в стиле Reya
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown('<div class="reya-card"><p class="label">Total TVL</p><p class="mono-data">$241.8M</p></div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="reya-card"><p class="label">Current APY</p><p class="mono-data neon-text">14.22%</p></div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="reya-card"><p class="label">Active Traders</p><p class="mono-data">12.1K</p></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Визуализация данных (Стиль: Тонкие линии, темный фон)
    st.markdown('<div class="reya-card">', unsafe_allow_html=True)
    st.markdown("<p class="label">Liquidity Depth Simulator</p>", unsafe_allow_html=True)
    
    x = np.linspace(0, 10, 100)
    y = np.sin(x) * 10 + 20
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, fill='tozeroy', line=dict(color='#4BFF99', width=2), fillcolor='rgba(75, 255, 153, 0.05)'))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0), height=300,
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(family="JetBrains Mono", size=10, color="#444")),
        yaxis=dict(showgrid=True, gridcolor="#1A1A1B", zeroline=False, tickfont=dict(family="JetBrains Mono", size=10, color="#444"))
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown("<h3>Margin Utility</h3>", unsafe_allow_html=True)
    
    # Блок калькулятора (Professional Input Form)
    st.markdown('<div class="reya-card">', unsafe_allow_html=True)
    st.markdown("<p class='label'>Select Asset</p>", unsafe_allow_html=True)
    st.selectbox("", ["BTC/srUSD", "ETH/srUSD", "SOL/srUSD"], label_visibility="collapsed")
    
    st.markdown("<p class='label' style='margin-top:20px;'>Position Leverage</p>", unsafe_allow_html=True)
    lev = st.slider("", 1, 50, 10, label_visibility="collapsed")
    
    st.markdown("<p class='label' style='margin-top:20px;'>Margin Amount</p>", unsafe_allow_html=True)
    st.number_input("", value=1000, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("CALCULATE RISK PARAMS"):
        with st.spinner("Processing on-chain logic..."):
            import time; time.sleep(1)
        st.markdown("<p style='color: #4BFF99; font-family: \"JetBrains Mono\"; font-size: 0.8rem;'>Analysis ready. Health Factor: 1.42 (Stable)</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Дополнительная информационная карточка
    st.markdown("""
    <div style="margin-top: 20px; border-left: 2px solid #4BFF99; padding-left: 20px;">
        <p class="label">Protocol Insight</p>
        <p style="font-size: 0.8rem; color: #888; line-height: 1.6;">Reya the first margin-optimized L2. By using this tool, you help the ecosystem visualize the capital efficiency of our cross-margin engine.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 6. FOOTER ---
st.markdown("""
<div style="margin-top: 100px; padding-top: 20px; border-top: 1px solid #1A1A1B; text-align: center;">
    <p style="font-family: 'JetBrains Mono'; color: #333; font-size: 0.7rem;">BUILD_ID: CONTRIBUTOR_829_ALPHA // AUTHENTICATED ACCESS ONLY</p>
</div>
""", unsafe_allow_html=True)
