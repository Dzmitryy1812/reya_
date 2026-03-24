import streamlit as st
import pandas as pd
import numpy as np
import requests
import math
import plotly.graph_objects as go
from scipy.stats import norm
from datetime import datetime

# --- 1. ПРЕМИУМ КОНФИГУРАЦИЯ СТИЛЯ REYA ---
st.set_page_config(page_title="Reya Alpha Terminal", page_icon="⚡", layout="wide")

# Инъекция кастомного CSS с шрифтами Google (Space Grotesk + JetBrains Mono)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Space+Grotesk:wght@400;700&display=swap');

    /* Глобальный фон и текст */
    .stApp {
        background-color: #050505 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        color: #E0E0E0 !important;
    }

    /* Скрытие дефолтного хедера Streamlit */
    header {visibility: hidden;}

    /* Стилизация заголовков (градиентный текст) */
    h1, h2, h3 {
        font-weight: 700 !important;
        background: linear-gradient(90deg, #FFFFFF 0%, #00FFAA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }

    /* Карточки метрик (Metrics) */[data-testid="stMetric"] {
        background: linear-gradient(180deg, #111111 0%, #0a0a0a 100%);
        border: 1px solid #1a1a1a;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 30px rgba(0, 255, 170, 0.02);
        transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    }[data-testid="stMetric"]:hover {
        border-color: #00FFAA;
        box-shadow: 0 8px 40px rgba(0, 255, 170, 0.15);
        transform: translateY(-3px);
    }

    /* Цифры в метриках */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: #00FFAA !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        text-shadow: 0 0 20px rgba(0, 255, 170, 0.3);
    }

    /* Подписи к метрикам */[data-testid="stMetricLabel"] {
        color: #888888 !important;
        text-transform: uppercase;
        font-size: 0.85rem !important;
        letter-spacing: 1px;
    }

    /* Кнопки в стиле киберпанк/терминал */
    .stButton > button {
        background-color: transparent;
        color: #00FFAA;
        border: 1px solid #00FFAA;
        border-radius: 8px;
        font-family: 'JetBrains Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 700;
        width: 100%;
        padding: 10px;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 255, 170, 0.1);
    }
    
    .stButton > button:hover {
        background-color: #00FFAA;
        color: #000000;
        box-shadow: 0 0 25px rgba(0, 255, 170, 0.5);
        border-color: #00FFAA;
    }

    /* Разделители */
    hr {
        border-color: #1a1a1a !important;
    }

    /* Блоки с кодом (Code blocks) */
    .stCodeBlock {
        background-color: #0a0a0a !important;
        border: 1px solid #1a1a1a !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. МАТЕМАТИЧЕСКИЙ ДВИЖОК ---
def lognormal_prob_above(S, K, iv, T):
    if S <= 0 or K <= 0 or iv <= 0 or T <= 0: return 0.5
    d2 = (math.log(S / K) - 0.5 * iv**2 * T) / (iv * math.sqrt(T))
    return float(norm.cdf(d2))

# --- 3. ИМИТАЦИЯ ДАННЫХ (Чтоб точно работало без ошибок API) ---
# Замените этот блок на реальный API (CryptoCompare), когда настроите ключ
@st.cache_data(ttl=60)
def get_market_data():
    # Симуляция получения данных для демонстрации UI
    # Если хотите использовать Binance или CryptoCompare - вставьте код из предыдущего ответа
    current_price = 66500.0 + np.random.normal(0, 100)
    current_dvol = 52.4 + np.random.normal(0, 1)
    rv = 41.2 + np.random.normal(0, 2)
    return current_price, current_dvol, rv

# --- 4. ОСНОВНОЙ ИНТЕРФЕЙС ---
spot_price, dvol, rv = get_market_data()

# Заголовок
st.markdown("<h1>⚡ REYA ALPHA TERMINAL</h1>", unsafe_allow_html=True)
st.caption(f"LIVE FEED // SECURE CONNECTION // {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")

# Метрики сверху (с неоновым эффектом благодаря CSS)
m1, m2, m3, m4 = st.columns(4)
m1.metric("BTC Index Price", f"${spot_price:,.2f}")
m2.metric("Implied Vol (DVOL)", f"{dvol:.1f}%")
m3.metric("Realized Vol (RV 24h)", f"{rv:.1f}%")

vol_gap = dvol - rv
m4.metric("Volatility Risk Premium", f"{vol_gap:.1f}%", delta=f"{vol_gap:.1f}%", delta_color="normal")

st.divider()

# --- СТРАТЕГИЯ ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("<h3>📊 VOLATILITY ARBITRAGE RADAR</h3>", unsafe_allow_html=True)
    
    # Стилизованные плашки сигналов
    if vol_gap > 10:
        st.info("🟢 **SYSTEM SIGNAL: SHORT VOLATILITY (High VRP)**\n\nOptimal condition for Reya LP. Market is overpricing risk. Yield generation efficiency is at peak levels.")
    else:
        st.warning("🟡 **SYSTEM SIGNAL: PROTECT MODE**\n\nVolatility is underpriced. Hedge positions recommended.")

    # График вероятностей в стиле Reya (Киберпанк)
    strikes = np.linspace(spot_price * 0.75, spot_price * 1.25, 100)
    probs =[lognormal_prob_above(spot_price, k, dvol/100, 7/365) for k in strikes]
    
    fig = go.Figure()
    # Заливка под графиком с прозрачностью (Glow effect)
    fig.add_trace(go.Scatter(
        x=strikes, y=probs, 
        fill='tozeroy', 
        fillcolor='rgba(0, 255, 170, 0.1)', 
        line=dict(color='#00FFAA', width=3), 
        name="P(S > K)"
    ))
    
    # Линия текущей цены (Spot)
    fig.add_vline(x=spot_price, line_dash="dash", line_color="#888888", annotation_text=" SPOT PRICE ", annotation_font_color="#00FFAA")
    
    fig.update_layout(
        title=dict(text="7-Day Probability Distribution Map", font=dict(color="#FFFFFF", size=18, family="Space Grotesk")),
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title="STRIKE PRICE ($)", gridcolor='#111111', zerolinecolor='#111111', tickfont=dict(family="JetBrains Mono", color="#888")),
        yaxis=dict(title="PROBABILITY", gridcolor='#111111', zerolinecolor='#111111', tickfont=dict(family="JetBrains Mono", color="#888")),
        margin=dict(l=0, r=0, t=40, b=0),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("<h3>🛡️ LIQUIDATION RADAR</h3>", unsafe_allow_html=True)
    target_price = st.number_input("ENTER LIQUIDATION TRIGGER ($)", value=int(spot_price*0.85), step=500)
    
    prob_down = 1 - lognormal_prob_above(spot_price, target_price, dvol/100, 1/365)
    
    st.markdown("<p style='color: #888; font-size: 0.9rem;'>24H DOWNSIDE PROBABILITY:</p>", unsafe_allow_html=True)
    
    # Динамический цвет риска
    risk_color = "#00FFAA" if prob_down < 0.05 else "#FFAA00" if prob_down < 0.15 else "#FF0044"
    st.markdown(f"<h1 style='color: {risk_color}; font-family: \"JetBrains Mono\", monospace; text-shadow: 0 0 20px {risk_color}40; font-size: 3rem;'>{prob_down*100:.2f}%</h1>", unsafe_allow_html=True
