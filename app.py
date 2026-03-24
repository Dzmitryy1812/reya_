import streamlit as st
import requests
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Цвета Reya
BG = "#050505"
TEXT = "#F5F5F5"
RED = "#FF3B69"
YELLOW = "#FFB800"
BLUE = "#00D9FF"

st.set_page_config(page_title="Reya Liquidation Radar", layout="wide")
st.markdown(f"<style>body {{ background: {BG}; color: {TEXT}; }}</style>", unsafe_allow_html=True)

# === API CONFIGURATION ===
REYA_INDEXER_URL = "https://indexer.reya.network/v1/liquidation-clusters"  # Публичный эндпоинт
HEADERS = {"User-Agent": "ReyaRadar/1.0"}

def fetch_liquidation_data(asset: str = "BTC/srUSD"):
    """Получает агрегированные данные по ликвидациям из Reya Indexer"""
    try:
        response = requests.get(
            REYA_INDEXER_URL,
            params={"market": asset, "window_hours": 24},
            headers=HEADERS,
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"⚠️ Failed to fetch data: {str(e)}")
        return None

# === MAX PAIN CALCULATION ===
def calculate_max_pain(prices, density, window=300):
    max_vol, pain_price = 0, prices[0]
    for p in prices:
        vol = density[(prices >= p - window) & (prices <= p + window)].sum()
        if vol > max_vol:
            max_vol, pain_price = vol, p
    return pain_price

# === UI ===
st.title("🌐 Reya Liquidation Radar")
asset = st.selectbox("Market", ["BTC/srUSD", "ETH/srUSD", "SOL/srUSD", "ARB/srUSD"])

# Получаем данные
data = fetch_liquidation_data(asset)
if not data:
    st.stop()

# Извлекаем данные
current_price = data["current_price"]
price_levels = np.array(data["price_levels"])
liquidation_density = np.array(data["liquidation_volume"])
last_updated = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))

# Расчёт Max Pain
max_pain = calculate_max_pain(price_levels, liquidation_density)

# Визуализация
fig = go.Figure()
fig.add_trace(go.Bar(
    x=price_levels,
    y=liquidation_density,
    marker_color=[RED if v > np.percentile(liquidation_density, 80) 
                  else YELLOW if v > np.percentile(liquidation_density, 50) 
                  else "#333" for v in liquidation_density],
    width=np.diff(price_levels)[0] * 0.8
))
fig.add_vline(x=current_price, line_color=BLUE, line_width=3, annotation_text="NOW")
fig.add_vline(x=max_pain, line_dash="dot", line_color=YELLOW, line_width=2,
              annotation_text=f"MAX PAIN\n${max_pain:,.0f}", annotation_position="bottom right")

fig.update_layout(
    height=300,
    margin=dict(l=0, r=0, t=30, b=20),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis_title="Price (srUSD)",
    yaxis_title="Liquidation Volume",
    font=dict(color=TEXT)
)
st.plotly_chart(fig, use_container_width=True)

# Алерты
dist_to_pain = abs(current_price - max_pain) / current_price * 100
nearest_cluster = price_levels[np.argmax(liquidation_density)]
dist_to_cluster = abs(current_price - nearest_cluster) / current_price * 100

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Current Price", f"${current_price:,.0f}")
with col2:
    st.metric("Max Pain", f"${max_pain:,.0f}", delta=f"{-dist_to_pain:.1f}%")
with col3:
    st.metric("Nearest Cluster", f"${nearest_cluster:,.0f}", delta=f"{-dist_to_cluster:.1f}%")

# Рекомендации для маркетмейкеров
if dist_to_cluster < 1.0:
    st.error("🚨 HIGH RISK: Price approaching liquidation cluster — WIDEN SPREADS")
elif dist_to_pain < 1.5:
    st.warning("⚠️ MEDIUM RISK: Price near Max Pain — MONITOR VOLATILITY")
else:
    st.success("✅ LOW RISK: Safe distance from liquidation zones")

st.caption(f"Data updated: {last_updated.strftime('%H:%M:%S UTC')} | Source: Reya Indexer API")
