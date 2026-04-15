import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Linear Futures Tracker", layout="wide")

# --- COMMAND CENTER (SIDEBAR) ---
st.sidebar.title("⚙️ Trade Execution")

direction = st.sidebar.radio("Position Direction", ["Long Future (Buy)", "Short Future (Sell)"])

st.sidebar.markdown("### Trade Parameters")
entry_price = st.sidebar.number_input("Entry Price", value=3350.0)
current_price = st.sidebar.number_input("Current Market Price", value=3400.0)

qty = st.sidebar.number_input("Number of Contracts (Lots)", value=100, min_value=1)
multiplier = st.sidebar.number_input("Contract Multiplier (e.g., 10 MT)", value=10, min_value=1)

# Margin input for return on capital calculations
initial_margin = st.sidebar.number_input("Margin Requirement per Lot ($)", value=2500.0)

# --- CORE MATHEMATICS ---
total_margin = initial_margin * qty
notional_value = entry_price * qty * multiplier

# Breakeven is mathematically just the entry price (excluding broker fees)
breakeven = entry_price

if direction == "Long Future (Buy)":
    current_pnl = (current_price - entry_price) * qty * multiplier
    max_profit = "Infinite"
    max_loss = f"-${notional_value:,.2f} (If asset goes to 0)"
else: # Short Future
    current_pnl = (entry_price - current_price) * qty * multiplier
    max_profit = f"${notional_value:,.2f} (If asset goes to 0)"
    max_loss = "Infinite Risk (Upside uncapped)"

# --- MAIN DASHBOARD UI ---
st.title("⚖️ Directional Futures Tracker")
st.markdown("Track absolute linear risk, margin utilization, and real-time PnL.")

# Top Metric Cards
m1, m2, m3, m4 = st.columns(4)

m1.metric("Breakeven Price", f"{breakeven:,.2f}")
m2.metric("Total Margin Locked", f"${total_margin:,.2f}")

if current_pnl >= 0:
    m3.metric("Live Floating PnL", f"+${current_pnl:,.2f}", delta_color="normal")
else:
    m3.metric("Live Floating PnL", f"-${abs(current_pnl):,.2f}", delta_color="inverse")

# Calculate Return on Margin (ROM)
if total_margin > 0:
    rom = (current_pnl / total_margin) * 100
    m4.metric("Return on Margin (ROM)", f"{rom:,.2f}%", delta=f"{rom:,.2f}%")
else:
    m4.metric("Return on Margin (ROM)", "N/A")

st.markdown("---")
st.markdown(f"**Risk Profile:** Max Profit: {max_profit} | Max Loss: {max_loss}")

# --- VISUALIZATION ENGINE ---
# Generate price array focusing tightly around the entry price
x_min = entry_price * 0.7
x_max = entry_price * 1.3
x = np.linspace(x_min, x_max, 300)

# Calculate linear PnL array
if direction == "Long Future (Buy)":
    y_pnl = (x - entry_price) * qty * multiplier
    line_color = "#00FFAA" # Greenish for long
else:
    y_pnl = (entry_price - x) * qty * multiplier
    line_color = "#FF4444" # Reddish for short

# Plotly Chart
fig = go.Figure()

# Linear PnL Line
fig.add_trace(go.Scatter(x=x, y=y_pnl, name="Futures PnL", 
                         line=dict(color=line_color, width=4)))

# Zero Line (Breakeven Horizon)
fig.add_hline(y=0, line_color="white", line_width=1)

# Entry Price / Breakeven Marker
fig.add_vline(x=entry_price, line_dash="solid", line_color="yellow", 
              annotation_text="Entry / Breakeven", annotation_position="bottom right")

# Current Live Price Marker
fig.add_vline(x=current_price, line_dash="dot", line_color="cyan", 
              annotation_text="Live Market", annotation_position="top right")

fig.update_layout(
    xaxis_title="Underlying Asset Price",
    yaxis_title="Total Profit / Loss ($)",
    template="plotly_dark",
    height=500,
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)
