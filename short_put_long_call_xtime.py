import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Risk Reversal Dashboard", layout="wide")

# --- COMMAND CENTER (SIDEBAR) ---
st.sidebar.title("⚙️ Position Controls")

st.sidebar.markdown("### Market Environment")
current_price = st.sidebar.number_input("Current Underlying Price", value=3356)

st.sidebar.markdown("### Long Leg (Upside)")
call_strike = st.sidebar.number_input("Long Call Strike", value=3500)
call_prem = st.sidebar.number_input("Call Premium Paid", value=200.0)
call_qty = st.sidebar.number_input("Call Quantity", value=1, min_value=1)

st.sidebar.markdown("### Short Leg (Downside Funding)")
put_strike = st.sidebar.number_input("Short Put Strike", value=3200)
put_prem = st.sidebar.number_input("Put Premium Collected", value=100.0)
put_qty = st.sidebar.number_input("Put Quantity", value=2, min_value=1)

# Contract Multiplier (Defaulted to 10 MT for standard physical sizing)
multiplier = 10 

# --- CORE MATHEMATICS ---
net_premium = (put_prem * put_qty) - (call_prem * call_qty)
net_cash_flow = net_premium * multiplier

# 1. Max Profit Calculation
max_profit = "Infinite"

# 2. Max Loss Calculation (If asset goes to 0)
max_loss_per_unit = (put_strike * put_qty) - net_premium
total_max_loss = max_loss_per_unit * multiplier

# 3. Breakeven Calculation
if net_premium > 0: # Net Credit
    breakeven = put_strike - (net_premium / put_qty)
elif net_premium < 0: # Net Debit
    breakeven = call_strike + (abs(net_premium) / call_qty)
else: # Zero Cost
    breakeven = "Flat Zone between Strikes"

# --- MAIN DASHBOARD UI ---
st.title("📈 Synthetic Risk Reversal Tracker")
st.markdown("Absolute expiration risk metrics for leveraged synthetic longs.")

# Top Metric Cards
m1, m2, m3, m4 = st.columns(4)
m1.metric("Max Profit", max_profit)
m2.metric("Max Loss (To Zero)", f"-${total_max_loss:,.2f}", delta_color="inverse")
m3.metric("Breakeven Price", f"{breakeven:,.2f}" if isinstance(breakeven, float) else breakeven)

if net_cash_flow >= 0:
    m4.metric("Net Entry Cash Flow", f"+${net_cash_flow:,.2f} (Credit)", delta_color="normal")
else:
    m4.metric("Net Entry Cash Flow", f"-${abs(net_cash_flow):,.2f} (Debit)", delta_color="inverse")

# --- VISUALIZATION ENGINE ---
# Generate price array based on strikes
x_min = min(put_strike, call_strike) * 0.5
x_max = max(put_strike, call_strike) * 1.5
x = np.linspace(x_min, x_max, 300)

# Calculate Expiration PnL
exp_pnl = ((np.maximum(0, x - call_strike) * call_qty) - (np.maximum(0, put_strike - x) * put_qty) + net_premium) * multiplier

# Plotly Chart
fig = go.Figure()

# Rigid Expiration Line
fig.add_trace(go.Scatter(x=x, y=exp_pnl, name="Expiration PnL", 
                         line=dict(color="#00FFAA", width=4)))

# Zero Line & Current Price Marker
fig.add_hline(y=0, line_color="white", line_width=1)
fig.add_vline(x=current_price, line_dash="dot", line_color="orange", 
              annotation_text="Current Market", annotation_position="top left")

fig.update_layout(
    xaxis_title="Underlying Asset Price",
    yaxis_title="Total Profit / Loss ($)",
    template="plotly_dark",
    height=600,
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)
