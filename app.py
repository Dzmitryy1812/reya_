import streamlit as st
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timezone

# =============================================================================
# CONFIGURATION & STYLING
# =============================================================================
st.set_page_config(page_title="Reya Liquidation Radar", layout="wide", initial_sidebar_state="collapsed")

# Цветовая схема Reya (Dark Mode)
BG_COLOR = "#050505"
CARD_BG = "#111111"
TEXT_COLOR = "#F5F5F5"
LONG_RED = "#FF3B69"   # Ликвидация лонгов (цена падает)
SHORT_GREEN = "#00FF7F" # Ликвидация шортов (цена растет)
ACCENT_BLUE = "#00D9FF"
WARNING_GOLD = "#FFB800"

st.markdown(f"""
    <style>
    .main {{ background-color: {BG_COLOR}; }}
    .stMetric {{ background-color: {CARD_BG}; padding: 15px; border-radius: 10px; border: 1px solid #333; }}
    div[data-testid="stExpander"] {{ border: none; background: {CARD_BG}; }}
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# MOCK DATA ENGINE (Симуляция реального стакана ликвидаций)
# =============================================================================

def generate_market_data(asset):
    base_prices = {"BTC/srUSD": 64200, "ETH/srUSD": 3450, "SOL/srUSD": 145, "ARB/srUSD": 1.15}
    curr_price = base_prices.get(asset, 50000)
    
    # Создаем сетку цен +/- 10%
    price_range = np.linspace(curr_price * 0.9, curr_price * 1.1, 400)
    
    # Генерируем кластеры (имитация плечей 10х, 25х, 50х)
    def create_cluster(center, width, intensity):
        return np.exp(-((price_range - center)**2) / (2 * width**2)) * intensity

    # Кластеры Лонгов (ниже цены)
    longs = create_cluster(curr_price * 0.97, curr_price * 0.005, 1200) + \
            create_cluster(curr_price * 0.94, curr_price * 0.008, 800)
            
    # Кластеры Шортов (выше цены)
    shorts = create_cluster(curr_price * 1.03, curr_price * 0.004, 1500) + \
             create_cluster(curr_price * 1.06, curr_price * 0.01, 600)
    
    # Добавляем случайный шум
    noise = np.random.normal(0, 50, len(price_range))
    liq_density = np.maximum(0, longs + shorts + noise)
    
    return price_range, liq_density, curr_price

# =============================================================================
# LOGIC: MAX PAIN & RISK ANALYSIS
# =============================================================================

def get_risk_metrics(prices, density, current_price):
    max_idx = np.argmax(density)
    max_pain_price = prices[max_idx]
    
    # Расстояние до ближайшего крупного кластера (>80 процентиля)
    high_threshold = np.percentile(density, 90)
    high_nodes = prices[density > high_threshold]
    distances = np.abs(high_nodes - current_price)
    nearest_cluster = high_nodes[np.argmin(distances)] if len(high_nodes) > 0 else max_pain_price
    
    dist_pct = abs(current_price - nearest_cluster) / current_price * 100
    return max_pain_price, nearest_cluster, dist_pct

# =============================================================================
# UI LAYOUT
# =============================================================================

st.title("🌐 Reya Liquidation Radar")
st.caption("Active monitoring of liquidation cascades for Market Makers and Advanced Traders")

# Sidebar - Настройки
with st.sidebar:
    st.header("Radar Settings")
    asset = st.selectbox("Select Market", ["BTC/srUSD", "ETH/srUSD", "SOL/srUSD", "ARB/srUSD"])
    leverage_filter = st.slider("Filter by Leverage (Est.)", 1, 100, (10, 50))
    st.divider()
    st.info("Currently using Simulated Data. Integration with Reya Indexer V2 pending.")

# Получение данных
prices, density, curr_price = generate_market_data(asset)
max_pain, nearest_cluster, dist_to_cluster = get_risk_metrics(prices, density, curr_price)

# Метрики в верхней части
col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Price", f"${curr_price:,.2f}", )
col2.metric("Max Pain Zone", f"${max_pain:,.2f}", f"{((max_pain/curr_price)-1)*100:.2f}%")
col3.metric("Nearest Cluster", f"${nearest_cluster:,.2f}")

# Статус риска
with col4:
    if dist_to_cluster < 1.5:
        st.error("🚨 HIGH VOLATILITY RISK")
    elif dist_to_cluster < 3.0:
        st.warning("⚠️ MEDIUM RISK ZONE")
    else:
        st.success("✅ STABLE MARKET")

# =============================================================================
# CHARTING (PLOTLY)
# =============================================================================

fig = go.Figure()

# Цвета: Красный для лонгов (слева), Зеленый для шортов (справа)
bar_colors = [LONG_RED if p < curr_price else SHORT_GREEN for p in prices]

# Основной график плотности
fig.add_trace(go.Bar(
    x=prices,
    y=density,
    marker_color=bar_colors,
    marker_line_width=0,
    opacity=0.8,
    name="Liquidation Vol",
    hovertemplate="Price: $%{x:,.2f}<br>Liq Volume: %{y:.0f} srUSD<extra></extra>"
))

# Линия текущей цены
fig.add_vline(x=curr_price, line_width=2, line_dash="solid", line_color=ACCENT_BLUE)
fig.add_annotation(x=curr_price, y=max(density), text="MARK PRICE", showarrow=False, 
                   font=dict(color=ACCENT_BLUE), bgcolor=BG_COLOR)

# Линия Max Pain
fig.add_vline(x=max_pain, line_width=2, line_dash="dot", line_color=WARNING_GOLD)

# Оформление
fig.update_layout(
    height=450,
    margin=dict(l=10, r=10, t=20, b=10),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=False, title="Price (srUSD)", tickformat="$,.0f", color="#888"),
    yaxis=dict(showgrid=True, gridcolor="#222", title="Liquidation Intensity", color="#888"),
    showlegend=False,
    hovermode="x"
)

st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# TRADING INSIGHTS
# =============================================================================

c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 Market Maker Strategy")
    if dist_to_cluster < 2.0:
        st.write(f"**Action:** ⚠️ **Widen Spreads**. Price is very close to a liquidation cluster at ${nearest_cluster:,.0f}. Expect high slippage and toxic flow.")
    else:
        st.write("**Action:** ✅ **Tighten Spreads**. Market is balanced. Good conditions for delta-neutral market making.")

with c2:
    st.subheader("💡 Key Levels")
    long_liq_vol = sum(density[prices < curr_price])
    short_liq_vol = sum(density[prices > curr_price])
    
    total = long_liq_vol + short_liq_vol
    st.write(f"- **Est. Long Liquidations:** {(long_liq_vol/total)*100:.1f}% of total pool")
    st.write(f"- **Est. Short Liquidations:** {(short_liq_vol/total)*100:.1f}% of total pool")

# =============================================================================
# FOOTER / API PROPOSAL
# =============================================================================
st.divider()
st.markdown(f"""
    <div style="color: #666; font-size: 0.8rem;">
        <b>Proposal for Reya Network Indexer:</b><br>
        To move this to production, we propose the following endpoint: <code>GET /v1/analytics/liquidation-map?symbol={asset.split('/')[0]}</code><br>
        This will allow LPs to automate risk management directly via the Reya SDK.<br>
        <i>Last Updated: {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')} | Mock Mode Active</i>
    </div>
    """, unsafe_allow_html=True)
