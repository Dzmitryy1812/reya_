import streamlit as st
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timezone

# =============================================================================
# CONFIGURATION
# =============================================================================

BG = "#050505"
TEXT = "#F5F5F5"
RED = "#FF3B69"
YELLOW = "#FFB800"
BLUE = "#00D9FF"

st.set_page_config(page_title="Reya Liquidation Radar", layout="wide")
st.markdown(f"<style>body {{ background: {BG}; color: {TEXT}; }}</style>", unsafe_allow_html=True)

# =============================================================================
# MOCK DATA GENERATOR (REALISTIC LIQUIDATION CLUSTERS)
# =============================================================================

def get_mock_liquidation_data(asset: str):
    """Generates realistic liquidation heatmap based on typical perpetuals behavior"""
    # Base price from asset
    base_prices = {
        "BTC/srUSD": 65200,
        "ETH/srUSD": 3450,
        "SOL/srUSD": 175,
        "ARB/srUSD": 1.85
    }
    current_price = base_prices.get(asset, 65200)
    
    # Generate price grid ±15%
    range_pct = 0.15
    step = max(1, int(current_price * 0.001))  # Adaptive step size
    min_price = int(current_price * (1 - range_pct))
    max_price = int(current_price * (1 + range_pct))
    price_levels = np.arange(min_price, max_price + step, step)
    
    # Simulate 2-3 liquidation clusters (realistic for perps)
    np.random.seed(42)  # Reproducible
    cluster1_center = current_price * (0.97 + np.random.rand() * 0.03)  # Below price
    cluster2_center = current_price * (1.03 + np.random.rand() * 0.03)  # Above price
    
    liquidation_volume = (
        np.exp(-((price_levels - cluster1_center)**2) / (2 * (current_price * 0.005)**2)) * 1200 +
        np.exp(-((price_levels - cluster2_center)**2) / (2 * (current_price * 0.007)**2)) * 900
    )
    
    return {
        "current_price": current_price,
        "price_levels": price_levels.tolist(),
        "liquidation_volume": liquidation_volume.tolist(),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }

# =============================================================================
# MAX PAIN CALCULATION
# =============================================================================

def calculate_max_pain(prices, density, window_ratio=0.005):
    """Max Pain = price level with highest liquidation concentration in adaptive window"""
    prices = np.array(prices)
    density = np.array(density)
    window = int(window_ratio * prices[len(prices)//2])  # ~0.5% of mid price
    
    max_vol, pain_price = 0, prices[0]
    for p in prices:
        mask = (prices >= p - window) & (prices <= p + window)
        vol = density[mask].sum()
        if vol > max_vol:
            max_vol, pain_price = vol, p
    return pain_price

# =============================================================================
# UI LAYOUT
# =============================================================================

st.title("🌐 Reya Liquidation Radar")
st.caption("Early-warning system for market makers | Max Pain + Liquidation Clusters")

# Market selector
asset = st.selectbox("Market", ["BTC/srUSD", "ETH/srUSD", "SOL/srUSD", "ARB/srUSD"])

# Always use mock data (API not live yet)
data = get_mock_liquidation_data(asset)

# Extract data
current_price = data["current_price"]
price_levels = np.array(data["price_levels"])
liquidation_density = np.array(data["liquidation_volume"])
last_updated = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))

# Calculate Max Pain
max_pain = calculate_max_pain(price_levels, liquidation_density)

# =============================================================================
# VISUALIZATION
# =============================================================================

fig = go.Figure()
fig.add_trace(go.Bar(
    x=price_levels,
    y=liquidation_density,
    marker_color=[
        RED if v > np.percentile(liquidation_density, 85)
        else YELLOW if v > np.percentile(liquidation_density, 60)
        else "#333" for v in liquidation_density
    ],
    width=np.diff(price_levels)[0] * 0.8
))

# Current price and Max Pain lines
fig.add_vline(x=current_price, line_color=BLUE, line_width=3, annotation_text="NOW")
fig.add_vline(x=max_pain, line_dash="dot", line_color=YELLOW, line_width=2,
              annotation_text=f"MAX PAIN\n${max_pain:,.0f}", annotation_position="bottom right")

# Layout
fig.update_layout(
    height=320,
    margin=dict(l=0, r=0, t=30, b=20),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis_title="Price (srUSD)",
    yaxis_title="Liquidation Volume",
    font=dict(color=TEXT),
    showlegend=False
)
st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# RISK METRICS & ALERTS
# =============================================================================

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

# Risk-level alert
if dist_to_cluster < 1.0:
    st.error("🚨 HIGH RISK: Price approaching liquidation cluster — WIDEN SPREADS")
elif dist_to_pain < 1.5:
    st.warning("⚠️ MEDIUM RISK: Price near Max Pain — MONITOR VOLATILITY")
else:
    st.success("✅ LOW RISK: Safe distance from liquidation zones")

# =============================================================================
# FOOTER: PROPOSAL TO REYA TEAM
# =============================================================================

st.markdown("---")
st.caption(
    "💡 This dashboard requires a new Reya Indexer endpoint: "
    "`GET /v2/public/liquidation-heatmap?market=BTC/srUSD`. "
    "Proposed to enhance market maker risk infrastructure. "
    f"Mock data shown • Updated: {last_updated.strftime('%H:%M:%S UTC')}"
)
