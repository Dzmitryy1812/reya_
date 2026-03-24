
import streamlit as st
import pandas as pd
import numpy as np
import requests
import math
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
from scipy.stats import norm

# --- 1. КОНФИГУРАЦИЯ СТИЛЯ REYA ---
st.set_page_config(page_title="Reya Alpha Terminal", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    .stMetric { background-color: #0b0b0b; border: 1px solid #222; padding: 15px; border-radius: 10px; }
    div[data-testid="stMetricValue"] { color: #00FF00 !important; font-family: 'Space Mono', monospace; }
    .stButton>button { border: 1px solid #00FF00; background-color: #000; color: #00FF00; width: 100%; }
    .stButton>button:hover { background-color: #00FF00; color: #000; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. МАТЕМАТИЧЕСКИЙ ДВИЖОК ---
def calc_realized_vol(prices):
    """Расчет реализованной волатильности (RV) за 24ч (годовое исчисление)"""
    log_returns = np.log(prices / prices.shift(1)).dropna()
    # 24 часа * 365 дней (минутные свечи: 60*24*365)
    return log_returns.std() * np.sqrt(365 * 1440) * 100

def lognormal_prob_above(S, K, iv, T):
    """Вероятность того, что цена будет выше K (BSM d2)"""
    if S <= 0 or K <= 0 or iv <= 0 or T <= 0: return 0.5
    d2 = (math.log(S / K) - 0.5 * iv**2 * T) / (iv * math.sqrt(T))
    return float(norm.cdf(d2))

# --- 3. ПОЛУЧЕНИЕ ДАННЫХ ---
@st.cache_data(ttl=60)
def get_market_data():
    # 1. Спот цена (Bybit)
    r_price = requests.get("https://api.bybit.com").json()
    price = float(r_price["result"]["list"][0]["lastPrice"])
    
    # 2. DVOL (Deribit) - Ожидаемая волатильность
    r_dvol = requests.get("https://www.deribit.com").json()
    dvol = float(r_dvol["result"]["data"][-1][3])
    
    # 3. История цен для RV (последние 24 часа, 5-минутные свечи)
    r_hist = requests.get("https://api.bybit.com").json()
    df_hist = pd.DataFrame(r_hist["result"]["list"], columns=['t','o','h','l','c','v','turnover']).astype(float)
    rv = calc_realized_vol(df_hist['c'])
    
    return price, dvol, rv

# --- 4. ОСНОВНОЙ ИНТЕРФЕЙС ---
try:
    spot_price, dvol, rv = get_market_data()
except:
    st.error("Ошибка подключения к API. Проверь интернет.")
    st.stop()

st.title("⚡ Reya Alpha & Volatility Terminal")
st.caption("Quantitative insights for Reya Network LPs & Traders")

# Метрики сверху
m1, m2, m3, m4 = st.columns(4)
m1.metric("BTC Price", f"${spot_price:,.0f}")
m2.metric("Implied Vol (DVOL)", f"{dvol:.1f}%")
m3.metric("Realized Vol (RV)", f"{rv:.1f}%")
vol_gap = dvol - rv
m4.metric("Volatility Gap", f"{vol_gap:.1f}%", delta=f"{vol_gap:.1f}%", delta_color="inverse")

st.divider()

# --- СТРАТЕГИЯ MEAN REVERSION ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📊 Volatility Arbitrage Radar")
    
    if vol_gap > 10:
        st.success("🎯 **SIGNAL: SELL VOLATILITY (High Fear)**")
        st.write("Рынок переплачивает за риск. Это идеальное время для **предоставления ликвидности (LP) на Reya**, так как комиссии от трейдеров будут перекрывать реальные движения цены.")
    elif vol_gap < -5:
        st.warning("⚠️ **SIGNAL: BUY VOLATILITY (Underpriced)**")
        st.write("Рынок слишком спокоен. Ожидается сильный импульс. Будьте осторожны с короткими позициями и низким залогом.")
    else:
        st.info("⚖️ **SIGNAL: NEUTRAL**")
        st.write("Волатильность в равновесии. Торгуйте по тренду.")

    # График (Визуализация вероятностей)
    strikes = np.linspace(spot_price * 0.8, spot_price * 1.2, 50)
    probs = [lognormal_prob_above(spot_price, k, dvol/100, 7/365) for k in strikes] # на 7 дней
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=strikes, y=probs, line=dict(color='#00FF00', width=3), name="Prob Above Strike"))
    fig.update_layout(
        title="Вероятность удержания цены (через 7 дней)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title="BTC Strike Price", gridcolor='#222'),
        yaxis=dict(title="Probability", gridcolor='#222')
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("🛡️ Risk Metrics")
    target_price = st.number_input("Target Price (Downside)", value=int(spot_price*0.9), step=500)
    
    # Расчет вероятности падения ниже уровня за 24 часа
    prob_down = 1 - lognormal_prob_above(spot_price, target_price, dvol/100, 1/365)
    
    st.write(f"Вероятность падения ниже **${target_price:,.0f}** за 24 часа:")
    st.header(f"{prob_down*100:.1f}%")
    
    if prob_down > 0.15:
        st.error("HIGH LIQUIDATION RISK")
    else:
        st.success("SAFE ZONE")

    st.divider()
    st.markdown("### 💎 Reya Point Multiplier")
    st.write("Based on Volatility:")
    st.code(f"Current Efficiency: {1 + (vol_gap/100):.2f}x")
    st.caption("Higher Gap = Better conditions for Signal Points via LP-ing.")

# Футер
st.sidebar.image("https://docs.reya.network", width=150) # Проверь ссылку на лого
st.sidebar.markdown("---")
st.sidebar.write("Developed for **Reya Signal Program**")
st.sidebar.button("Generate Alpha Report (X)")
