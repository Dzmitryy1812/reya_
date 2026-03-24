import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# --- 1. КОНФИГУРАЦИЯ СТРАНИЦЫ ---
st.set_page_config(page_title="Reya Staking Interface", page_icon="⚡", layout="wide")

# --- 2. CSS-СТИЛИЗАЦИЯ В ДУХЕ REYA NETWORK ---
st.markdown("""
    <style>
    /* Импорт шрифтов: Inter для UI, JetBrains Mono для цифр */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600;700&display=swap');

    /* Глобальный фон, убираем стандартный отступ Streamlit */
    .stApp {
        background-color: #0B0B0C !important;
        font-family: 'Inter', sans-serif !important;
        color: #F2F2F2 !important;
    }
    
    header {visibility: hidden;}
    .block-container {padding-top: 2rem !important; padding-bottom: 2rem !important;}

    /* Типографика и заголовки */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.02em;
    }

    /* Карточки метрик (Metrics) - Матовое стекло в стиле Mine Shaft */
    [data-testid="stMetric"] {
        background-color: rgba(32, 32, 32, 0.4) !important;
        backdrop-filter: blur(12px);
        border: 1px solid #2A2A2A !important;
        padding: 24px !important;
        border-radius: 16px !important;
        transition: border-color 0.3s ease;
    }[data-testid="stMetric"]:hover {
        border-color: rgba(75, 255, 153, 0.3) !important;
    }

    /* Значения в метриках */[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: #FFFFFF !important;
        font-size: 2.2rem !important;
        font-weight: 600 !important;
    }

    /* Лейблы метрик */[data-testid="stMetricLabel"] {
        color: #9CA3AF !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }

    /* Дельты (Delta) внутри метрик - Фирменный зеленый Reya */[data-testid="stMetricDelta"] svg { fill: #4BFF99 !important; }
    [data-testid="stMetricDelta"] div { 
        color: #4BFF99 !important; 
        font-family: 'JetBrains Mono', monospace !important; 
        font-weight: 600 !important;
    }

    /* Главные стили кнопок (Call to action) */
    .stButton > button {
        background-color: #4BFF99 !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        padding: 1rem !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: #83FFB9 !important;
        box-shadow: 0 0 24px rgba(75, 255, 153, 0.25) !important;
        transform: translateY(-1px);
    }
    .stButton > button:active {
        transform: translateY(1px);
    }

    /* Вкладки (Tabs) для переключения Stake / Unstake */
    .stTabs [data-baseweb="tab-list"] {
        gap: 32px;
        background-color: transparent !important;
    }
    .stTabs[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #9CA3AF !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        border-radius: 0 !important;
        padding-bottom: 12px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 1.1rem !important;
    }
    .stTabs [aria-selected="true"] {
        color: #FFFFFF !important;
        border-bottom: 2px solid #4BFF99 !important;
    }

    /* Поля ввода (Inputs) */
    .stNumberInput input {
        background-color: #151515 !important;
        border: 1px solid #2A2A2A !important;
        border-radius: 12px !important;
        color: #FFFFFF !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.5rem !important;
        padding: 12px 16px !important;
    }
    .stNumberInput input:focus {
        border-color: #4BFF99 !important;
        box-shadow: none !important;
    }

    /* Разделители */
    hr { border-color: #2A2A2A !important; margin-top: 2rem !important; margin-bottom: 2rem !important; }

    /* Кастомная плашка APY */
    .apy-badge {
        background: rgba(75, 255, 153, 0.1);
        color: #4BFF99;
        padding: 4px 10px;
        border-radius: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        font-weight: 600;
        vertical-align: middle;
        margin-left: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ИМИТАЦИОННЫЕ ДАННЫЕ И СОСТОЯНИЯ ---
if 'wallet_balance' not in st.session_state:
    st.session_state.wallet_balance = 25400.50
if 'staked_balance' not in st.session_state:
    st.session_state.staked_balance = 10000.00

active_apy = 14.2
tvl = 145200000.00

# --- 4. ВЕРСТКА ИНТЕРФЕЙСА ---

# Шапка с логотипом/названием
st.markdown("""
<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;'>
    <div style='display: flex; align-items: center; gap: 12px;'>
        <div style='background: #4BFF99; width: 24px; height: 24px; border-radius: 4px;'></div>
        <h2 style='margin:0; padding:0;'>Reya Network <span style='color: #888; font-weight: 400; font-size: 1.2rem;'>| Stake</span></h2>
    </div>
    <div style='font-family: "JetBrains Mono"; color: #9CA3AF; font-size: 0.9rem;'>
        Network: <span style='color: #FFF;'>Arbitrum</span> • Status: <span style='color: #4BFF99;'>Operational</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Метрики протокола (3 колонки)
col1, col2, col3 = st.columns(3)
col1.metric("Total Value Locked", f"${tvl:,.0f}")
col2.metric("Current APY", f"{active_apy}%", delta="+0.4% (24h)")
col3.metric("Your Staked Return", "$1,420.50", delta="+$12.40 (Today)")

st.divider()

# Основной рабочий блок (График слева, Управление стейкингом справа)
left_panel, right_panel = st.columns([1.6, 1])

with left_panel:
    st.markdown("### Yield Performance (7D)")
    
    # Генерация данных для графика (исторический APY)
    dates =[datetime.now() - timedelta(days=i) for i in range(7, -1, -1)]
    base_apy = active_apy
    y_data =[base_apy + np.random.normal(0, 0.2) for _ in range(8)]
    y_data[-1] = active_apy # Текущий APY

    fig = go.Figure()
    
    # График с заливкой (прозрачный градиент под линией)
    fig.add_trace(go.Scatter(
        x=dates, y=y_data,
        mode='lines',
        line=dict(color='#4BFF99', width=3),
        fill='tozeroy',
        fillcolor='rgba(75, 255, 153, 0.05)'
    ))

    # Стилизация графика под Reya-Dark
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='#1A1A1A', zerolinecolor='#1A1A1A', tickfont=dict(family="JetBrains Mono", color="#888")),
        yaxis=dict(gridcolor='#1A1A1A', zerolinecolor='#1A1A1A', tickfont=dict(family="JetBrains Mono", color="#888"),
                   ticksuffix="%"),
        margin=dict(l=0, r=0, t=10, b=0),
        height=380,
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

with right_panel:
    # Контейнер карточки стейкинга
    st.markdown("""
    <div style="background: rgba(32, 32, 32, 0.5); border: 1px solid #2A2A2A; border-radius: 16px; padding: 24px;">
        <h3 style="margin-top: 0; font-size: 1.2rem; display: inline-block;">Manage Stake</h3>
        <span class="apy-badge">14.2% APY</span>
    """, unsafe_allow_html=True)
    
    # Вкладки
    tab_stake, tab_unstake = st.tabs(["Stake", "Unstake / Withdraw"])
    
    with tab_stake:
        st.markdown(f"<p style='color: #9CA3AF; margin-bottom: 4px; font-size: 0.85rem;'>Wallet Balance</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-family: JetBrains Mono; color: #FFF; font-size: 1.5rem; margin-top: 0;'>{st.session_state.wallet_balance:,.2f} <span style='color: #4BFF99; font-size: 1rem;'>srUSD</span></p>", unsafe_allow_html=True)
        
        amount = st.number_input("Amount to stake", min_value=0.0, max_value=st.session_state.wallet_balance, value=0.0, step=100.0, label_visibility="collapsed")
        
        if st.button("Confirm Stake 🔒", key="btn_stake"):
            if amount > 0:
                with st.spinner("Executing transaction..."):
                    time.sleep(1.5) # Имитация транзакции
                    st.session_state.wallet_balance -= amount
                    st.session_state.staked_balance += amount
                st.success("Stake successful!")
                st.rerun()
            else:
                st.error("Enter a valid amount")
                
    with tab_unstake:
        st.markdown(f"<p style='color: #9CA3AF; margin-bottom: 4px; font-size: 0.85rem;'>Staked Balance</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-family: JetBrains Mono; color: #FFF; font-size: 1.5rem; margin-top: 0;'>{st.session_state.staked_balance:,.2f} <span style='color: #4BFF99; font-size: 1rem;'>srUSD</span></p>", unsafe_allow_html=True)
        
        amount_unstake = st.number_input("Amount to unstake", min_value=0.0, max_value=st.session_state.staked_balance, value=0.0, step=100.0, label_visibility="collapsed")
        
        # Для кнопки Unstake используем небольшую хитрость, чтобы переопределить ее цвет через кастомный класс (так как она второстепенная)
        st.markdown("""
        <style>
        .btn-unstake button { 
            background-color: transparent !important; 
            border: 1px solid #4BFF99 !important; 
            color: #4BFF99 !important; 
        }
        .btn-unstake button:hover { 
            background-color: rgba(75, 255, 153, 0.1) !important; 
            box-shadow: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="btn-unstake">', unsafe_allow_html=True)
        if st.button("Unstake & Withdraw", key="btn_unstake"):
            if amount_unstake > 0:
                with st.spinner("Withdrawing..."):
                    time.sleep(1.5)
                    st.session_state.staked_balance -= amount_unstake
                    st.session_state.wallet_balance += amount_unstake
                st.success("Withdrawal complete!")
                st.rerun()
            else:
                st.error("Enter a valid amount")
        st.markdown('</div>', unsafe_allow_html=True)

    # Закрываем div карточки
    st.markdown("</div>", unsafe_allow_html=True)
