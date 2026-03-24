import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# --- 1. CONFIG & THEME ---
st.set_page_config(page_title="Reya Alpha | Staking", page_icon="⚡", layout="wide")

# Кастомный CSS для полной стилизации под Reya Network
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono:wght@400;700&display=swap');

    /* База */
    .stApp { background-color: #0B0B0C !important; color: #F2F2F2 !important; font-family: 'Inter', sans-serif !important; }
    header {visibility: hidden;}
    .block-container {padding-top: 2rem !important;}

    /* Карточки и блоки */
    .reya-card {
        background: rgba(22, 22, 23, 0.8);
        border: 1px solid #2A2A2B;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }

    /* Метрики */
    [data-testid="stMetric"] {
        background: #161617 !important;
        border: 1px solid #2A2A2B !important;
        padding: 20px !important;
        border-radius: 12px !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: #4BFF99 !important; /* Фирменный неон Reya */
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] { font-size: 0.8rem !important; color: #888 !important; text-transform: uppercase; }

    /* Кнопки */
    .stButton > button {
        background: #4BFF99 !important;
        color: #000 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        width: 100%;
        height: 50px;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.3s all;
    }
    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(75, 255, 153, 0.4);
        transform: translateY(-2px);
    }

    /* XP Badge */
    .xp-badge {
        background: linear-gradient(90deg, #4BFF99 0%, #34D399 100%);
        color: black;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 800;
        font-family: 'JetBrains Mono';
        font-size: 0.7rem;
    }

    /* Табы */
    .stTabs [data-baseweb="tab-list"] { background: transparent; border-bottom: 1px solid #2A2A2B; }
    .stTabs [data-baseweb="tab"] { color: #888; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #4BFF99 !important; border-bottom-color: #4BFF99 !important; }
    
    /* Скроллбар */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #0B0B0C; }
    ::-webkit-scrollbar-thumb { background: #2A2A2B; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIC & STATE ---
if 'balance' not in st.session_state:
    st.session_state.balance = 42000.00
if 'staked' not in st.session_state:
    st.session_state.staked = 5000.0
if 'xp' not in st.session_state:
    st.session_state.xp = 1450.0
if 'history' not in st.session_state:
    st.session_state.history = [
        {"type": "Stake", "amount": 5000, "status": "Confirmed", "time": "2h ago"},
        {"type": "Deposit", "amount": 12000, "status": "Confirmed", "time": "1d ago"}
    ]

def add_xp(amount):
    # Логика: чем больше стейк, тем быстрее капает XP
    st.session_state.xp += (st.session_state.staked / 1000) * amount

# --- 3. SIDEBAR (WALLET & XP) ---
with st.sidebar:
    st.markdown("<h2 style='color:#FFF;'>⚡ TERMINAL</h2>", unsafe_allow_html=True)
    
    # Wallet Info
    st.markdown(f"""
        <div class="reya-card">
            <p style="color:#888; font-size:0.7rem; margin-bottom:5px;">CONNECTED WALLET</p>
            <p style="font-family:'JetBrains Mono'; font-size:0.9rem;">0x71C...89B1</p>
            <hr style="border-color:#2A2A2B">
            <p style="color:#888; font-size:0.7rem; margin-bottom:5px;">REYA POINTS (XP)</p>
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <span style="font-size:1.4rem; font-weight:700; color:#4BFF99;">{st.session_state.xp:,.1f}</span>
                <span class="xp-badge">RANK #452</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📊 Yield Projection")
    # Калькулятор симуляции
    period = st.select_slider("Projection Period", options=["30D", "90D", "1Y"])
    days = 30 if period == "30D" else 90 if period == "90D" else 365
    projected = st.session_state.staked * (0.142 / 365 * days)
    st.caption(f"Estimated yield for {period}:")
    st.markdown(f"<h3 style='color:#FFF;'>+ ${projected:,.2f}</h3>", unsafe_allow_html=True)

# --- 4. MAIN CONTENT ---

# Header
col_h1, col_h2 = st.columns([2, 1])
with col_h1:
    st.markdown("<h1 style='margin-bottom:0;'>Active Staking</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888;'>Stake srUSD to power the Reya ecosystem and earn network fees.</p>", unsafe_allow_html=True)

# Top Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("TVL", "$241.8M", delta="1.2%")
m2.metric("Base APY", "14.22%", delta="0.4%")
m3.metric("Your Stake", f"${st.session_state.staked:,.0f}")
m4.metric("Efficiency", "1.4x", help="Capital efficiency multiplier based on Reya's margin engine")

st.markdown("---")

# Main Interface
left_col, right_col = st.columns([1.5, 1])

with left_col:
    # График доходности
    st.markdown("### Ecosystem Growth")
    time_points = pd.date_range(end=datetime.now(), periods=30)
    data = pd.DataFrame({
        'Date': time_points,
        'TVL': np.linspace(180, 241, 30) + np.random.normal(0, 2, 30)
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['Date'], y=data['TVL'],
        fill='tozeroy',
        fillcolor='rgba(75, 255, 153, 0.05)',
        line=dict(color='#4BFF99', width=3),
        name="TVL ($M)"
    ))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=20, b=0), height=300,
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#1A1A1B')
    )
    st.plotly_chart(fig, use_container_width=True)

    # Activity Feed
    st.markdown("### Recent Activity")
    for item in st.session_state.history:
        st.markdown(f"""
            <div style="display:flex; justify-content:space-between; padding:12px; border-bottom:1px solid #1A1A1B;">
                <span style="color:#FFF;">{item['type']} <span style="color:#4BFF99; font-family:'JetBrains Mono';">${item['amount']}</span></span>
                <span style="color:#888; font-size:0.8rem;">{item['time']} • <span style="color:#34D399;">{item['status']}</span></span>
            </div>
        """, unsafe_allow_html=True)

with right_col:
    # Staking Box
    st.markdown('<div class="reya-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>Manage Position</h3>", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["STAKE", "UNSTAKE"])
    
    with t1:
        st.markdown(f"<p style='color:#888; font-size:0.8rem;'>Available: <b>{st.session_state.balance:,.2f} srUSD</b></p>", unsafe_allow_html=True)
        amount = st.number_input("Amount", min_value=0.0, step=100.0, label_visibility="collapsed")
        
        if st.button("STAKE srUSD"):
            if amount > 0 and amount <= st.session_state.balance:
                with st.spinner("Broadcasting to Reya L2..."):
                    time.sleep(1.2)
                    st.session_state.balance -= amount
                    st.session_state.staked += amount
                    st.session_state.history.insert(0, {"type": "Stake", "amount": amount, "status": "Confirmed", "time": "Just now"})
                    add_xp(50) # Бонус XP за действие
                st.success(f"Success! {amount} srUSD added to stake.")
                st.rerun()
            else:
                st.error("Invalid amount")
        
        st.markdown("""
            <div style="margin-top:20px; font-size:0.75rem; color:#888;">
                <p>⚡ Boost: Staking for 30+ days increases XP multiplier to 1.5x</p>
            </div>
        """, unsafe_allow_html=True)

    with t2:
        st.markdown(f"<p style='color:#888; font-size:0.8rem;'>Staked: <b>{st.session_state.staked:,.2f} srUSD</b></p>", unsafe_allow_html=True)
        u_amount = st.number_input("Unstake Amount", min_value=0.0, step=100.0, label_visibility="collapsed", key="unstake_val")
        
        # Стилизация кнопки вывода (второстепенная)
        st.markdown("<style>.unstake-btn button {background:#1A1A1B !important; color:#FFF !important; border:1px solid #2A2A2B !important;}</style>", unsafe_allow_html=True)
        st.markdown('<div class="unstake-btn">', unsafe_allow_html=True)
        if st.button("WITHDRAW"):
            if u_amount > 0 and u_amount <= st.session_state.staked:
                st.session_state.staked -= u_amount
                st.session_state.balance += u_amount
                st.session_state.history.insert(0, {"type": "Withdraw", "amount": u_amount, "status": "Confirmed", "time": "Just now"})
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Risk Meter (Logic Add-on)
    st.markdown("""
        <div class="reya-card" style="background: rgba(255, 59, 105, 0.05); border-color: rgba(255, 59, 105, 0.2);">
            <p style="color:#FF3B69; font-size:0.7rem; font-weight:700; text-transform:uppercase; margin-bottom:5px;">Health Factor</p>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:1.5rem; font-weight:700; color:#FF3B69;">99.8</span>
                <span style="color:#888; font-size:0.8rem;">Low Risk</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Footnote
st.markdown("<p style='text-align:center; color:#444; font-size:0.7rem; margin-top:50px;'>Reya Alpha Terminal V2.4 • Powered by Reya L2 Network • Secure Connection</p>", unsafe_allow_html=True)
