import streamlit as st
import plotly.graph_objects as go
import numpy as np
import scipy.stats as si
import math

st.set_page_config(page_title="Institutional Risk Desk", layout="wide")

# --- BLACK-SCHOLES ENGINE ---
def d1(S, K, T, r, sigma):
    return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

def d2(S, K, T, r, sigma):
    return (np.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

def bs_call(S, K, T, r, sigma):
    if T <= 0: return np.maximum(0, S - K)
    return (S * si.norm.cdf(d1(S, K, T, r, sigma)) - K * np.exp(-r * T) * si.norm.cdf(d2(S, K, T, r, sigma)))

def bs_put(S, K, T, r, sigma):
    if T <= 0: return np.maximum(0, K - S)
    return (K * np.exp(-r * T) * si.norm.cdf(-d2(S, K, T, r, sigma)) - S * si.norm.cdf(-d1(S, K, T, r, sigma)))

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Trading Desk Modules")
module = st.sidebar.radio("Select Tool:", [
    "1. Expected Move (Volatility)", 
    "2. Order Execution & Slippage", 
    "3. Vertical Spread Architect", 
    "4. Ratio Risk Reversal (T+0)"
])

# ==========================================
# MODULE 1: EXPECTED MOVE
# ==========================================
if module == "1. Expected Move (Volatility)":
    st.title("📊 Implied Volatility & Expected Move")
    col1, col2, col3 = st.columns(3)
    price = col1.number_input("Current Price", value=3356)
    iv = col2.slider("Implied Volatility (%)", 10, 200, 30)
    dte = col3.slider("Days to Expiration", 1, 365, 30)

    move = price * (iv / 100) * math.sqrt(dte / 365)
    upper, lower = price + move, price - move

    st.metric("1 Standard Deviation Expected Move (+/-)", f"{move:,.2f} Points")
    
    x = np.linspace(price * 0.5, price * 1.5, 500)
    y = si.norm.pdf(x, price, move)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, fill='tozeroy', name="Probability Curve"))
    fig.add_vline(x=price, line_dash="solid", annotation_text="Current Price")
    fig.add_vline(x=upper, line_dash="dash", line_color="red", annotation_text=f"Upper: {upper:,.0f}")
    fig.add_vline(x=lower, line_dash="dash", line_color="green", annotation_text=f"Lower: {lower:,.0f}")
    fig.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# MODULE 2: ORDER EXECUTION & SLIPPAGE
# ==========================================
elif module == "2. Order Execution & Slippage":
    st.title("⚖️ Bid-Ask Spread & Slippage Calculator")
    col1, col2, col3 = st.columns(3)
    lots = col1.number_input("Order Size (Lots)", value=200)
    bid = col2.number_input("Best Bid", value=3300)
    ask = col3.number_input("Best Ask", value=3356)
    
    multiplier = 10 # Standard MT multiplier
    mid_price = (bid + ask) / 2
    spread = ask - bid
    
    st.markdown("### Execution Strategy Comparison")
    m_col1, m_col2 = st.columns(2)
    
    with m_col1:
        st.error("🚨 Market Order (Pay the Ask)")
        cost_market = ask * lots * multiplier
        slippage = (ask - mid_price) * lots * multiplier
        st.metric("Total Capital Required", f"${cost_market:,.2f}")
        st.metric("Slippage (Money Surrendered)", f"-${slippage:,.2f}")
        
    with m_col2:
        st.success("🛡️ Limit Order (Target Mid-Price)")
        cost_limit = mid_price * lots * multiplier
        st.metric("Total Capital Required", f"${cost_limit:,.2f}")
        st.metric("Capital Saved", f"${slippage:,.2f}")

# ==========================================
# MODULE 3: VERTICAL SPREAD ARCHITECT
# ==========================================
elif module == "3. Vertical Spread Architect":
    st.title("🏗️ Vertical Spread Architect")
    cap_base = st.sidebar.number_input("Allocated Capital", value=5000000)
    
    col1, col2 = st.columns(2)
    with col1:
        short_strike = st.number_input("Short Strike", value=3400)
        short_prem = st.number_input("Short Premium", value=200)
    with col2:
        long_strike = st.number_input("Long Strike", value=3600)
        long_prem = st.number_input("Long Premium", value=80)
        
    net_prem = short_prem - long_prem
    width = abs(long_strike - short_strike) * 10
    max_risk = max(0, width - (net_prem * 10))
    max_contracts = int(cap_base / max_risk) if max_risk > 0 else 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Net Premium Collected", f"${net_prem:,.2f}/unit")
    m2.metric("Max Contracts (for 5M Margin)", f"{max_contracts:,}")
    m3.metric("Total Cash Generated TODAY", f"${max_contracts * net_prem * 10:,.2f}")
    
    x = np.linspace(short_strike*0.8, long_strike*1.2, 100)
    y = (np.minimum(0, short_strike - x) + np.maximum(0, x - long_strike)) * 10 + (net_prem * 10)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, name="Expiration PnL", line=dict(width=3)))
    fig.add_hline(y=0, line_dash="dash", line_color="white")
    fig.add_vline(x=short_strike+net_prem, line_dash="dot", annotation_text="Breakeven")
    fig.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# MODULE 4: RATIO RISK REVERSAL (T+0)
# ==========================================
elif module == "4. Ratio Risk Reversal (T+0)":
    st.title("📈 Ratio Risk Reversal & Time Decay (T+0)")
    
    st.sidebar.markdown("### Live Market Conditions")
    dte = st.sidebar.slider("Days to Expiration (DTE)", 0.001, 60.0, 60.0)
    iv = st.sidebar.slider("Implied Volatility (%)", 10, 100, 30) / 100.0
    r = 0.05 # Risk free rate
    
    col1, col2, col3, col4 = st.columns(4)
    put_strike = col1.number_input("Short Put Strike", value=3200)
    put_qty = col2.number_input("Short Put Qty", value=2)
    call_strike = col3.number_input("Long Call Strike", value=3500)
    call_qty = col4.number_input("Long Call Qty", value=1)
    
    # Calculate initial entry cost based on 60 DTE to set the baseline
    entry_put_prem = bs_put(3356, put_strike, 60/365, r, iv)
    entry_call_prem = bs_call(3356, call_strike, 60/365, r, iv)
    net_credit = (entry_put_prem * put_qty) - (entry_call_prem * call_qty)
    
    x = np.linspace(2000, 4500, 200)
    
    # Expiration Line
    exp_pnl = (np.maximum(0, x - call_strike) * call_qty) - (np.maximum(0, put_strike - x) * put_qty) + net_credit
    
    # T+0 Line (Current Day)
    t_days = dte / 365.0
    t0_pnl = []
    for spot in x:
        current_put = bs_put(spot, put_strike, t_days, r, iv)
        current_call = bs_call(spot, call_strike, t_days, r, iv)
        current_value = (current_call * call_qty) - (current_put * put_qty)
        t0_pnl.append(current_value + net_credit)
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=exp_pnl, name="Expiration PnL", line=dict(color="gray", width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=x, y=t0_pnl, name=f"T+0 PnL ({int(dte)} Days Left)", line=dict(color="cyan", width=3)))
    fig.add_hline(y=0, line_color="white")
    
    fig.update_layout(template="plotly_dark", height=600, yaxis_title="Net Profit / Loss")
    st.plotly_chart(fig, use_container_width=True)
