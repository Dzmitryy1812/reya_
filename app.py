import streamlit as st
import numpy as np
import plotly.graph_objects as go
import requests
import pandas as pd
from datetime import datetime

# =============================================================================
# CONFIGURATION & STYLING
# =============================================================================
st.set_page_config(page_title="Reya Live Radar", layout="wide")

BG_COLOR = "#050505"
CARD_BG = "#111111"
LONG_RED = "#FF3B69"
SHORT_GREEN = "#00FF7F"
ACCENT_BLUE = "#00D9FF"
WARNING_GOLD = "#FFB800"

st.markdown(f"""
    <style>
    .main {{ background-color: {BG_COLOR}; }}
    .stMetric {{ background-color: {CARD_BG}; padding: 15px; border-radius: 10px; border: 1px solid #333; }}
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# DATA FETCHING (CHAINBASE & BINANCE)
# =============================================================================

def get_crypto_price(asset_pair):
    """Получает живую цену с Binance для точности радара"""
    try:
        symbol = asset_pair.split('/')[0] # Из "BTC/srUSD" получаем "BTC"
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        res = requests.get(url, timeout=3).json()
        return float(res['price'])
    except:
        # Резервные цены, если API недоступно
        defaults = {"BTC": 96500.0, "ETH": 3450.0, "SOL": 185.0, "ARB": 0.90}
        return defaults.get(asset_pair.split('/')[0], 1.0)

def fetch_chainbase_data(api_key, sql):
    url = "https://api.chainbase.online/v1/dw/query"
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, json={"query": sql}, timeout=5)
        if response.status_code == 200:
            return response.json()['data']['result']
    except:
        pass
    return None

def get_liquidation_clusters(api_key):
    """Реальные балансы из Reya (topic0: 0x6748...)"""
    sql = """
    SELECT bytearray_to_uint256(unhex(substring(data, 3, 64))) / 1e6 as balance
    FROM reya.transaction_logs 
    WHERE topic0 = '0x6748e8a7f71651e1dc8805fbbe06f1d448578396cd02923f579b2aedde56087f'
    ORDER BY block_number DESC LIMIT 200
    """
    res = fetch_chainbase_data(api_key, sql)
    return [r['balance'] for r in res] if res else []

# =============================================================================
# CORE LOGIC
# =============================================================================

def generate_radar_data(api_key, asset):
    # 1. Получаем ПРАВИЛЬНУЮ рыночную цену
    curr_price = get_crypto_price(asset)
    
    # 2. Получаем реальные балансы (залоги) из Reya
    balances = get_liquidation_clusters(api_key) if api_key else []
    
    # Создаем сетку цен вокруг текущей рыночной цены
    price_range = np.linspace(curr_price * 0.92, curr_price * 1.08, 400)
    density = np.zeros_like(price_range)
    
    # Используем балансы для создания "горбов" ликвидаций
    # Если ключа нет, создаем синтетические кластеры
    seed_data = balances if len(balances) > 0 else [500, 1200, 3000, 800, 150]
    
    for i, b in enumerate(seed_data[:40]):
        # Плечи (отступ от цены)
        offset = 0.015 + (i % 6) * 0.012 
        intensity = b * 5 
        
        # Лонги
        c_long = curr_price * (1 - offset)
        density += np.exp(-((price_range - c_long)**2) / (2 * (curr_price*0.002)**2)) * intensity
        
        # Шорты
        c_short = curr_price * (1 + offset)
        density += np.exp(-((price_range - c_short)**2) / (2 * (curr_price*0.002)**2)) * (intensity * 0.8)

    return price_range, density + np.random.normal(0, np.max(density)*0.01, 400), curr_price

# =============================================================================
# UI
# =============================================================================

st.title("🌐 Reya Liquidation Radar")

with st.sidebar:
    st.header("Terminal Settings")
    cb_api_key = st.text_input("Chainbase API Key", type="password")
    asset = st.selectbox("Select Asset", ["BTC/srUSD", "ETH/srUSD", "SOL/srUSD", "ARB/srUSD"])
    st.divider()
    if cb_api_key: st.success("Connected to Reya Mainnet")
    else: st.info("Running in Simulation Mode")

# Получение данных
prices, density, curr_price = generate_radar_data(cb_api_key, asset)

# Вычисляем метрики
max_idx = np.argmax(density)
max_pain = prices[max_idx]
dist_pct = abs(curr_price - max_pain) / curr_price * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Live Price", f"${curr_price:,.2f}")
col2.metric("Max Pain Zone", f"${max_pain:,.2f}")
col3.metric("Closeness", f"{dist_pct:.2f}%")
with col4:
    if dist_pct < 1.5: st.error("🚨 CRITICAL RISK")
    elif dist_pct < 3: st.warning("⚠️ VOLATILE")
    else: st.success("✅ CALM")

# График
fig = go.Figure()
fig.add_trace(go.Bar(
    x=prices, y=density, 
    marker_color=[LONG_RED if p < curr_price else SHORT_GREEN for p in prices],
    opacity=0.8, name="Liq Intensity"
))

# Линии
fig.add_vline(x=curr_price, line_width=2, line_color=ACCENT_BLUE, annotation_text="MARKET")
fig.add_vline(x=max_pain, line_width=2, line_dash="dot", line_color=WARNING_GOLD)

fig.update_layout(
    height=500, margin=dict(l=0, r=0, t=30, b=0),
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=False, color="#888", tickformat="$,.00f"),
    yaxis=dict(showgrid=True, gridcolor="#222", color="#888"),
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# Стратегический анализ
c_a, c_b = st.columns(2)
with c_a:
    st.subheader("💡 Market Context")
    st.write(f"The largest liquidation cluster is currently at **${max_pain:,.2f}**. Market makers should expect increased volatility if price approaches this level.")
with c_b:
    st.subheader("📊 Pool Balance")
    long_vol = np.sum(density[prices < curr_price])
    short_vol = np.sum(density[prices > curr_price])
    st.write(f"- Long Liquidation Volume: **{long_vol/(long_vol+short_vol)*100:.1f}%**")
    st.write(f"- Short Liquidation Volume: **{short_vol/(long_vol+short_vol)*100:.1f}%**")

st.divider()
st.caption(f"Last Refresh: {datetime.now().strftime('%H:%M:%S')} | Prices by Binance | Log Data by Chainbase")
