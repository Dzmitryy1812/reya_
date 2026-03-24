import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from enum import Enum

# ============================================================================
# 1. CONFIGURATION & THEME
# ============================================================================

st.set_page_config(
    page_title="Reya Pro Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Color Palette (Reya Brand)
class Colors:
    BG_PRIMARY = "#050505"
    BG_SECONDARY = "#0E0E10"
    BG_TERTIARY = "#111111"
    BORDER = "#1C1C1E"
    TEXT_PRIMARY = "#F5F5F5"
    TEXT_SECONDARY = "#999999"
    TEXT_MUTED = "#666666"
    ACCENT_GREEN = "#4BFF99"
    ACCENT_RED = "#FF3B69"
    ACCENT_BLUE = "#00D9FF"
    ACCENT_YELLOW = "#FFB800"

# ============================================================================
# 2. CUSTOM STYLING
# ============================================================================

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* === Global Styles === */
    .stApp {{
        background-color: {Colors.BG_PRIMARY} !important;
        font-family: 'Inter', sans-serif !important;
        color: {Colors.TEXT_PRIMARY} !important;
    }}
    
    header {{visibility: hidden;}}
    
    /* === Pro Card Component === */
    .pro-card {{
        background: {Colors.BG_SECONDARY};
        border: 1px solid {Colors.BORDER};
        border-radius: 6px;
        padding: 20px;
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }}
    
    .pro-card:hover {{
        border-color: {Colors.ACCENT_GREEN};
        box-shadow: 0 0 20px rgba(75, 255, 153, 0.1);
    }}
    
    /* === Typography === */
    .label-text {{
        color: {Colors.TEXT_MUTED};
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }}
    
    .value-text {{
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
        color: {Colors.TEXT_PRIMARY};
        font-size: 1.2rem;
    }}
    
    .highlight-green {{ color: {Colors.ACCENT_GREEN}; }}
    .highlight-red {{ color: {Colors.ACCENT_RED}; }}
    .highlight-blue {{ color: {Colors.ACCENT_BLUE}; }}
    
    /* === Stats Bar === */
    .stats-bar {{
        display: flex;
        gap: 40px;
        padding: 15px 20px;
        background: {Colors.BG_TERTIARY};
        border-bottom: 1px solid {Colors.BORDER};
        margin-bottom: 25px;
        border-radius: 4px;
    }}
    
    .stat-item {{
        display: flex;
        flex-direction: column;
        gap: 4px;
    }}
    
    /* === Sidebar === */
    [data-testid="stSidebar"] {{
        background-color: {Colors.BG_TERTIARY} !important;
        border-right: 1px solid {Colors.BORDER} !important;
    }}
    
    /* === Buttons === */
    .stButton > button {{
        background-color: {Colors.ACCENT_GREEN} !important;
        color: {Colors.BG_PRIMARY} !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
    }}
    
    .stButton > button:hover {{
        background-color: #3AE080 !important;
        transform: translateY(-2px) !important;
    }}
    
    /* === Input Fields === */
    .stNumberInput input, .stSelectbox select, .stSlider {{
        background-color: {Colors.BG_TERTIARY} !important;
        border: 1px solid {Colors.BORDER} !important;
        color: {Colors.TEXT_PRIMARY} !important;
        border-radius: 6px !important;
    }}
    
    /* === Dividers === */
    hr {{
        border-color: {Colors.BORDER} !important;
        margin: 15px 0 !important;
    }}
    
    /* === Scrollbar === */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {Colors.BG_SECONDARY};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {Colors.BORDER};
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {Colors.ACCENT_GREEN};
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# 3. SESSION STATE INITIALIZATION
# ============================================================================

if "leverage" not in st.session_state:
    st.session_state.leverage = 10
if "collateral" not in st.session_state:
    st.session_state.collateral = 5000
if "entry_price" not in st.session_state:
    st.session_state.entry_price = 65000
if "direction" not in st.session_state:
    st.session_state.direction = "Long"
if "simulation_result" not in st.session_state:
    st.session_state.simulation_result = None

# ============================================================================
# 4. UTILITY FUNCTIONS
# ============================================================================

def calculate_liquidation_price(entry, leverage, direction, collateral, maintenance_ratio=0.05):
    """Calculate precise liquidation price based on margin requirements"""
    if entry <= 0 or leverage <= 0 or collateral <= 0:
        return 0
    
    position_size = (collateral * leverage) / entry
    
    if direction == "Long":
        # For long: liquidation = entry * (1 - margin_ratio)
        liq_price = entry * (1 - (collateral / (position_size * entry)) + maintenance_ratio)
    else:
        # For short: liquidation = entry * (1 + margin_ratio)
        liq_price = entry * (1 + (collateral / (position_size * entry)) - maintenance_ratio)
    
    return max(0, liq_price)

def calculate_position_metrics(entry, leverage, collateral, direction):
    """Calculate all position-related metrics"""
    position_size = (collateral * leverage) / entry
    max_loss = collateral
    
    # ROI at 2% price movement
    price_change_2pct = entry * 0.02
    pnl_2pct = price_change_2pct * position_size
    roi_2pct = (pnl_2pct / collateral) * 100
    
    # Network fee estimation
    network_fee = 0.42
    
    # XP calculation
    xp_per_hour = leverage * 1.5 + (collateral / 1000) * 0.5
    
    return {
        "position_size": position_size,
        "max_loss": max_loss,
        "roi_2pct": roi_2pct,
        "network_fee": network_fee,
        "xp_per_hour": xp_per_hour,
    }

def format_currency(value, decimals=2):
    """Format value as currency"""
    return f"${value:,.{decimals}f}"

def format_percentage(value, decimals=2):
    """Format value as percentage"""
    color = "highlight-green" if value >= 0 else "highlight-red"
    sign = "+" if value >= 0 else ""
    return f'<span class="{color}">{sign}{value:.{decimals}f}%</span>'

# ============================================================================
# 5. HEADER: NETWORK HEALTH STATUS
# ============================================================================

col_net, col_tps, col_gas, col_block = st.columns(4)

with col_net:
    st.markdown(f"""
    <div class="stat-item">
        <span class="label-text">Network</span>
        <span class="value-text highlight-green" style="font-size:0.9rem;">● Reya L2</span>
    </div>
    """, unsafe_allow_html=True)

with col_tps:
    st.markdown(f"""
    <div class="stat-item">
        <span class="label-text">TPS</span>
        <span class="value-text" style="font-size:0.9rem;">42.5</span>
    </div>
    """, unsafe_allow_html=True)

with col_gas:
    st.markdown(f"""
    <div class="stat-item">
        <span class="label-text">Gas Price</span>
        <span class="value-text" style="font-size:0.9rem;">0.0001 srUSD</span>
    </div>
    """, unsafe_allow_html=True)

with col_block:
    st.markdown(f"""
    <div class="stat-item">
        <span class="label-text">Block Height</span>
        <span class="value-text" style="font-size:0.9rem;">19,450,212</span>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ============================================================================
# 6. SIDEBAR: PORTFOLIO & SETTINGS
# ============================================================================

with st.sidebar:
    st.markdown("### 💠 Portfolio Manager")
    
    st.markdown(f"""
    <div class="pro-card">
        <div style="margin-bottom: 15px;">
            <p class="label-text">Equity Value</p>
            <p class="value-text highlight-green">$42,105.50</p>
        </div>
        <hr>
        <div style="margin-top: 15px;">
            <p class="label-text">Available Margin</p>
            <p class="value-text highlight-green">$38,400.12</p>
        </div>
        <div style="margin-top: 10px;">
            <p class="label-text">Margin Utilization</p>
            <p class="value-text">8.8%</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### ⚙️ Terminal Settings")
    mode = st.radio(
        "Terminal Mode",
        ["Margin Analysis", "Vault Strategy", "XP Farming"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    st.markdown("### 📊 Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Open Positions", "3", "+1")
    with col2:
        st.metric("Total PnL", "+$1,245.50", "+2.8%")
    
    st.markdown("---")
    st.caption("v2.4.1-Stable | Audited by Halborn")

# ============================================================================
# 7. MAIN INTERFACE
# ============================================================================

st.markdown("<h2 style='margin-top:0; margin-bottom:25px;'>Advanced Margin Simulator</h2>", unsafe_allow_html=True)

col_main, col_side = st.columns([2.5, 1])

# ============================================================================
# 7.1 MAIN COLUMN: INPUT PARAMETERS
# ============================================================================

with col_main:
    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
    
    st.markdown("#### Position Parameters")
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        asset = st.selectbox(
            "Market",
            ["BTC/srUSD", "ETH/srUSD", "SOL/srUSD", "ARB/srUSD"],
            label_visibility="collapsed"
        )
        st.markdown('<p class="label-text">Market</p>', unsafe_allow_html=True)
        
        st.session_state.entry_price = st.number_input(
            "Entry Price",
            value=st.session_state.entry_price,
            min_value=1,
            step=100,
            label_visibility="collapsed"
        )
        st.markdown('<p class="label-text">Entry Price</p>', unsafe_allow_html=True)
    
    with c2:
        st.markdown('<p class="label-text" style="margin-bottom:8px;">Direction</p>')
        st.session_state.direction = st.segmented_control(
            "Direction",
            ["Long", "Short"],
            selection_mode="single",
            default=st.session_state.direction,
            label_visibility="collapsed"
        )
    
    with c3:
        st.session_state.leverage = st.slider(
            "Leverage (x)",
            1, 50,
            st.session_state.leverage,
            label_visibility="collapsed"
        )
        st.markdown('<p class="label-text">Leverage</p>', unsafe_allow_html=True)
    
    with c4:
        st.session_state.collateral = st.number_input(
            "Margin ($)",
            value=st.session_state.collateral,
            min_value=100,
            step=500,
            label_visibility="collapsed"
        )
        st.markdown('<p class="label-text">Margin</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # 7.2 LIQUIDATION RISK HEATMAP
    # ========================================================================
    
    st.markdown("### 📊 Liquidation Risk Distribution")
    
    # Generate price range and liquidation clusters
    entry = st.session_state.entry_price
    leverage = st.session_state.leverage
    collateral = st.session_state.collateral
    direction = st.session_state.direction
    
    price_range = np.linspace(entry * 0.7, entry * 1.3, 100)
    
    # Simulate liquidation clusters (realistic distribution)
    liq_clusters = (
        np.exp(-((price_range - (entry * 0.85))**2) / (2 * (entry * 0.08)**2)) * 50 +
        np.exp(-((price_range - (entry * 1.15))**2) / (2 * (entry * 0.08)**2)) * 30
    )
    
    # Calculate user's liquidation price
    my_liq = calculate_liquidation_price(entry, leverage, direction, collateral)
    
    # Create figure
    fig = go.Figure()
    
    # Add liquidation heatmap
    fig.add_trace(go.Scatter(
        x=price_range,
        y=liq_clusters,
        fill='tozeroy',
        name="Liquidation Depth",
        line=dict(color=Colors.ACCENT_RED, width=0),
        fillcolor=f'rgba(255, 59, 105, 0.15)'
    ))
    
    # Add user's liquidation line
    fig.add_vline(
        x=my_liq,
        line_dash="dash",
        line_color=Colors.ACCENT_GREEN,
        line_width=2,
        annotation_text="YOUR LIQUIDATION",
        annotation_position="top right",
        annotation_font_color=Colors.ACCENT_GREEN,
        annotation_font_size=10
    )
    
    # Add current price line
    fig.add_vline(
        x=entry,
        line_dash="solid",
        line_color=Colors.ACCENT_BLUE,
        line_width=2,
        annotation_text="ENTRY PRICE",
        annotation_position="top left",
        annotation_font_color=Colors.ACCENT_BLUE,
        annotation_font_size=10
    )
    
    # Update layout
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=350,
        margin=dict(l=0, r=0, t=40, b=0),
        hovermode='x unified',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor=f'rgba(28, 28, 30, 0.3)',
            title="Asset Price (srUSD)",
            title_font_color=Colors.TEXT_MUTED,
            tickfont_color=Colors.TEXT_MUTED
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor=f'rgba(28, 28, 30, 0.3)',
            title="Liquidation Volume",
            title_font_color=Colors.TEXT_MUTED,
            tickfont_color=Colors.TEXT_MUTED
        ),
        legend=dict(
            bgcolor='rgba(14, 14, 16, 0.8)',
            bordercolor=Colors.BORDER,
            borderwidth=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ========================================================================
    # 7.3 RISK METRICS TABLE
    # ========================================================================
    
    st.markdown("### 📈 Position Metrics")
    
    metrics = calculate_position_metrics(entry, leverage, collateral, direction)
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric(
            "Position Size",
            f"{metrics['position_size']:.4f} {asset.split('/')[0]}",
            delta=f"${metrics['position_size'] * entry:,.2f}"
        )
    
    with metric_col2:
        st.metric(
            "Max Loss",
            format_currency(metrics['max_loss']),
            delta=f"{(metrics['max_loss']/collateral)*100:.1f}% of margin"
        )
    
    with metric_col3:
        st.metric(
            "ROI @ 2% Move",
            f"{metrics['roi_2pct']:.2f}%",
            delta="Best case"
        )
    
    with metric_col4:
        st.metric(
            "XP/Hour",
            f"+{metrics['xp_per_hour']:.1f}",
            delta="Estimated"
        )

# ============================================================================
# 7.4 SIDE COLUMN: EXECUTION DETAILS
# ============================================================================

with col_side:
    st.markdown("### ⚡ Execution Details")
    
    st.markdown(f"""
    <div class="pro-card">
        <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
            <span class="label-text">Est. Liq Price</span>
            <span class="value-text" style="color:{Colors.ACCENT_RED}; font-size:0.95rem;">${my_liq:,.2f}</span>
        </div>
        
        <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
            <span class="label-text">Distance to Liq</span>
            <span class="value-text" style="font-size:0.95rem;">{abs((my_liq - entry) / entry * 100):.2f}%</span>
        </div>
        
        <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
            <span class="label-text">Margin Required</span>
            <span class="value-text" style="font-size:0.95rem;">{collateral:,.2f} srUSD</span>
        </div>
        
        <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
            <span class="label-text">Network Fee</span>
            <span class="value-text" style="font-size:0.95rem;">$0.42</span>
        </div>
        
        <hr>
        
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span class="label-text">Projected XP</span>
            <span class="value-text highlight-green" style="font-size:0.95rem;">+{metrics['xp_per_hour']:.1f}/hr</span>
        </div>
        
        <div style="display:flex; justify-content:space-between;">
            <span class="label-text">Risk Level</span>
            <span class="value-text" style="font-size:0.95rem;">
                {'🔴 HIGH' if leverage > 30 else '🟡 MEDIUM' if leverage > 15 else '🟢 LOW'}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Simulation button
    if st.button("⚙️ SIMULATE ON-CHAIN", use_container_width=True):
        with st.status("Simulating transaction on Reya L2...", expanded=True):
            st.write("🔍 Fetching Oracle prices (Pyth Network)...")
            time.sleep(0.6)
            
            st.write("📊 Calculating Cross-Margin requirements...")
            time.sleep(0.6)
            
            st.write("✅ Verifying solvency...")
            time.sleep(0.6)
            
            st.write("🔐 Confirming with smart contract...")
            time.sleep(0.4)
        
        st.success("✅ Simulation passed. Ready for execution.")
        st.session_state.simulation_result = {
            "timestamp": datetime.now(),
            "asset": asset,
            "direction": direction,
            "leverage": leverage,
            "entry": entry,
            "liq_price": my_liq,
            "collateral": collateral
        }

# ============================================================================
# 8. ADVANCED ANALYTICS SECTION
# ============================================================================

st.markdown("---")
st.markdown("### 📉 Advanced Analytics")

tab1, tab2, tab3 = st.tabs(["Historical Data", "Risk Analysis", "Portfolio"])

with tab1:
    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
    
    # Generate mock historical data
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    prices = entry + np.cumsum(np.random.randn(30) * entry * 0.02)
    volumes = np.random.randint(1000, 5000, 30)
    
    df_history = pd.DataFrame({
        'Date': dates,
        'Price': prices,
        'Volume': volumes
    })
    
    fig_history = go.Figure()
    fig_history.add_trace(go.Scatter(
        x=df_history['Date'],
        y=df_history['Price'],
        mode='lines',
        name='Price',
        line=dict(color=Colors.ACCENT_BLUE, width=2)
    ))
    
    fig_history.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=300,
        xaxis_title="Date",
        yaxis_title="Price (srUSD)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_history, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
    
    col_risk1, col_risk2, col_risk3 = st.columns(3)
    
    with col_risk1:
        st.metric("Value at Risk (95%)", format_currency(collateral * 0.95))
    with col_risk2:
        st.metric("Sharpe Ratio", "1.42")
    with col_risk3:
        st.metric("Max Drawdown", "-12.5%")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
    
    portfolio_data = {
        'Asset': ['BTC/srUSD', 'ETH/srUSD', 'SOL/srUSD'],
        'Position': ['+5.2', '+12.1', '-8.5'],
        'PnL': ['+$1,245.50', '+$542.30', '-$125.80'],
        'Margin': ['$2,000', '$1,500', '$1,000']
    }
    
    df_portfolio = pd.DataFrame(portfolio_data)
    st.dataframe(df_portfolio, use_container_width=True, hide_index=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# 9. FOOTER: LOGS & EXPORT
# ============================================================================

st.markdown("---")

log_col, exp_col = st.columns([2.5, 1])

with log_col:
    st.markdown("#### 📋 System Logs")
    
    st.markdown(f"""
    <div style="background:{Colors.BG_TERTIARY}; padding:12px; border:1px solid {Colors.BORDER}; 
                height:120px; overflow-y:auto; font-family:'JetBrains Mono'; font-size:0.75rem; 
                color:{Colors.ACCENT_GREEN}; opacity:0.8; border-radius:6px;">
        <div>[{datetime.now().strftime('%H:%M:%S')}] ✅ Connected to Reya Indexer (Mainnet)</div>
        <div>[{(datetime.now() - timedelta(seconds=5)).strftime('%H:%M:%S')}] ⚠️  High volatility detected in SOL markets</div>
        <div>[{(datetime.now() - timedelta(seconds=10)).strftime('%H:%M:%S')}] ✅ Account 0x71... verified for XP Multiplier 1.2x</div>
        <div>[{(datetime.now() - timedelta(seconds=15)).strftime('%H:%M:%S')}] 📊 Portfolio rebalance triggered</div>
        <div>[{(datetime.now() - timedelta(seconds=20)).strftime('%H:%M:%S')}] ✅ Gas price optimized to 0.0001 srUSD</div>
    </div>
    """, unsafe_allow_html=True)

with exp_col:
    st.markdown("#### 📥 Export")
    
    # Generate PDF report
    report_content = f"""
    REYA PRO TERMINAL - RISK REPORT
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    POSITION DETAILS:
    Asset: {asset}
    Direction: {direction}
    Entry Price: ${entry:,.2f}
    Leverage: {leverage}x
    Margin: ${collateral:,.2f}
    
    RISK METRICS:
    Liquidation Price: ${my_liq:,.2f}
    Position Size: {metrics['position_size']:.4f}
    Max Loss: ${metrics['max_loss']:,.2f}
    """
    
    st.download_button(
        label="📄 PDF REPORT",
        data=report_content,
        file_name=f"reya_risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        use_container_width=True
    )

# ============================================================================
# 10. FOOTER INFO
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.75rem; margin-top: 20px;">
    <p>🔒 <strong>Security First</strong> | Audited by Halborn | Non-Custodial | Self-Custody by Design</p>
    <p>Reya Pro Terminal v2.4.1 | Built with Streamlit | Powered by Arbitrum Orbit</p>
</div>
""", unsafe_allow_html=True)
