import streamlit as st
import pandas as pd
import numpy as np
import requests
import math
import plotly.graph_objects as go
from scipy.stats import norm
from datetime import datetime

# --- 1. КОНФИГУРАЦИЯ СТИЛЯ REYA ---
st.set_page_config(page_title="Reya Alpha Terminal", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    .stMetric { background-color: #0b0b0b; border: 1px solid #222; padding: 15px; border-radius: 10px; }
    div[data-testid="stMetricValue"] { color: #00FF00 !important; font-family: 'Space Mono', monospace; }
    .stButton>button { border: 1px solid #00FF00; background-color: #000; color: #00FF00; width: 100%; }
    .stButton>button:hover { background-color: #00FF00; color: #000; }
    .stHeader { color: #00FF00; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. МАТЕМАТИЧЕСКИЙ ДВИЖОК ---
def calc_realized_vol(prices):
    """Расчет реализованной волатильности (RV) на основе 5-минутных свечей за 24ч"""
    log_returns = np.log(prices / prices.shift(1)).dropna()
    # 5-минутных интервалов в году: (60/5) * 24 * 365 = 105120
    annualization_factor = np.sqrt(105120)
    return log_returns.std() * annualization_factor * 100

def lognormal_prob_above(S, K, iv, T):
    """Вероятность того, что цена будет выше K (BSM d2)"""
    if S <= 0 or K <= 0 or iv <= 0 or T <= 0: return 0.5
    # iv передается как 0.7 (для 70%)
    d2 = (math.log(S / K) - 0.5 * iv**2 * T) / (iv * math.sqrt(T))
    return float(norm.cdf(d2))

# --- 3. ПОЛУЧЕНИЕ ДАННЫХ ---
@st.cache_data(ttl=300)
def get_market_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        # 1. Свечи 5м и спот цена (Bybit V5)
        bybit_url = "https://api.bybit.com/v5/market/kline?category=linear&symbol=BTCUSDT&interval=5&limit=288"
        resp_bybit = requests.get(bybit_url, headers=headers, timeout=10)
        
        # Проверка статуса
        if resp_bybit.status_code != 200:
            st.error(f"Bybit API Error: {resp_bybit.status_code}")
            st.stop()
            
        data_bybit = resp_bybit.json()
        
        # Извлекаем список свечей
        kline_list = data_bybit.get('result', {}).get('list', [])
        if not kline_list:
            st.error("Bybit вернул пустой список данных")
            st.stop()
            
        df = pd.DataFrame(kline_list, columns=['t','o','h','l','c','v','turnover']).astype(float)
        df = df.iloc[::-1] # От старых к новым
        
        current_price = df['c'].iloc[-1]
        rv = calc_realized_vol(df['c'])
        
        # 2. DVOL (Deribit Volatility Index)
        dvol_url = "https://www.deribit.com/api/v2/public/get_volatility_index_data?currency=BTC&resolution=1&limit=1"
        resp_dvol = requests.get(dvol_url, headers=headers, timeout=10)
        
        if resp_dvol.status_code != 200:
            # Если Deribit недоступен, используем заглушку (среднее значение), чтобы приложение не падало
            st.warning("Не удалось получить DVOL с Deribit. Использую среднее значение 50.0")
            current_dvol = 50.0
        else:
            data_dvol = resp_dvol.json()
            # DVOL: [timestamp, open, high, low, close]
            current_dvol = data_dvol['result']['data'][0][4]
            
        return current_price, current_dvol, rv

    except Exception as e:
        st.error(f"Критическая ошибка: {str(e)}")
        # Возвращаем стандартные значения в случае полного сбоя
        return 65000.0, 50.0, 45.0

# --- 4. ОСНОВНОЙ ИНТЕРФЕЙС ---
try:
    spot_price, dvol, rv = get_market_data()
except Exception as e:
    st.error(f"Ошибка подключения: {e}")
    st.stop()

st.title("⚡ Reya Alpha & Volatility Terminal")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")

# Метрики сверху
m1, m2, m3, m4 = st.columns(4)
m1.metric("BTC Price", f"${spot_price:,.2f}")
m2.metric("Implied Vol (DVOL)", f"{dvol:.1f}%")
m3.metric("Realized Vol (RV 24h)", f"{rv:.1f}%")
vol_gap = dvol - rv
m4.metric("Volatility Risk Premium", f"{vol_gap:.1f}%", delta=f"{vol_gap:.1f}%", delta_color="normal")

st.divider()

# --- СТРАТЕГИЯ ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📊 Volatility Arbitrage Radar")
    
    if vol_gap > 15:
        st.success("🎯 **SIGNAL: SHORT VOLATILITY (High VRP)**")
        st.write("Наблюдается высокая премия за риск. **LP на Reya** сейчас максимально выгоден: вы получаете комиссии за торговлю волатильностью, которая в реальности ниже ожидаемой.")
    elif vol_gap < 5:
        st.warning("⚠️ **SIGNAL: LONG VOLATILITY / PROTECT**")
        st.write("Рынок недооценивает возможные движения. Рекомендуется хеджировать позиции или использовать стратегии пробоя.")
    else:
        st.info("⚖️ **SIGNAL: NEUTRAL**")
        st.write("Волатильность сбалансирована. Оптимальное время для дельта-нейтрального маркет-мейкинга.")

    # График вероятностей
    strikes = np.linspace(spot_price * 0.7, spot_price * 1.3, 100)
    # Рассчитываем вероятность на 7 дней
    probs = [lognormal_prob_above(spot_price, k, dvol/100, 7/365) for k in strikes]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=strikes, y=probs, name="P(S > K)", line=dict(color='#00FF00', width=2)))
    fig.add_vline(x=spot_price, line_dash="dash", line_color="white", annotation_text="Spot")
    
    fig.update_layout(
        title="Probability of Price staying Above Strike (7-Day Outlook)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title="Strike Price ($)", gridcolor='#222'),
        yaxis=dict(title="Probability (0-1)", gridcolor='#222'),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("🛡️ Liquidation Risk Profile")
    target_price = st.number_input("Liquidation Price (Downside)", value=int(spot_price*0.85), step=500)
    
    # Расчет вероятности падения ниже уровня за 24 часа
    # 1 - (вероятность что цена ВЫШЕ target) = вероятность что цена НИЖЕ target
    prob_down = 1 - lognormal_prob_above(spot_price, target_price, dvol/100, 1/365)
    
    st.write(f"Вероятность падения ниже **${target_price:,.0f}** в течение 24ч:")
    
    # Визуальный индикатор риска
    risk_color = "#00FF00" if prob_down < 0.05 else "#FFFF00" if prob_down < 0.15 else "#FF0000"
    st.markdown(f"<h1 style='color: {risk_color}'>{prob_down*100:.2f}%</h1>", unsafe_allow_html=True)
    
    if prob_down > 0.15:
        st.error("DANGER: Overleveraged Zone")
    else:
        st.success("SAFE: High Margin Cushion")

    st.divider()
    st.markdown("### 💎 Reya Capital Efficiency")
    efficiency = 1 + (vol_gap / 100)
    st.write(f"Based on current vol metrics, LP efficiency is:")
    st.code(f"{efficiency:.2f}x Multiplier")
    st.caption("Lower RV relative to IV increases the probability of profitable LP cycles.")

# Сидебар
st.sidebar.markdown("# ⚡ REYA ALPHA")
st.sidebar.info("Этот терминал анализирует разрыв между IV (ожиданиями) и RV (реальностью) для оптимизации позиций в Reya Network.")
if st.sidebar.button("Refresh Data"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write("Developed for Reya LPs")
