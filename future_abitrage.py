import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Long/Short Futures Hedger", layout="wide")

# --- COMMAND CENTER (SIDEBAR) ---
st.sidebar.title("⚙️ Position Controls")

st.sidebar.markdown("### Market Environment")
current_price = st.sidebar.number_input("Live Market Price", value=3400.0)

st.sidebar.markdown("### Position Sizing")
qty = st.sidebar.number_input("Number of Contracts (Lots)", value=100, min_value=1)
multiplier = st.sidebar.number_input("Contract Multiplier (e.g., 10 MT)", value=10, min_value=1)
margin_per_lot = st.sidebar.number_input("Margin per Lot ($)", value=2500.0)

st.sidebar.markdown("### Execution Prices")
long_entry = st.sidebar.number_input("Long Entry Price (Buy)", value=3350.0)
short_entry = st.sidebar.number_input("Short Entry Price (Sell)", value=3450.0)


# --- CORE MATHEMATICS ---
total_margin = (margin_per_lot * qty) * 2 # Margin required for holding both legs

# Individual Leg Breakevens
breakeven_long = long_entry
breakeven_short = short_entry

# Individual Leg PnL
pnl_long = (current_price - long_entry) * qty * multiplier
pnl_short = (short_entry - current_price) * qty * multiplier

# Net Locked PnL (The Arbitrage / Spread value)
net_pnl = pnl_long + pnl_short

# --- MAIN DASHBOARD UI ---
st.title("⚖️ Futures Spread & Hedge Dashboard")
st.markdown("Compare Long and Short exposure simultaneously to visualize boxed positions.")

# Top Metric Cards (Leg 1)
st.markdown("### Long Position (Upside Exposure)")
l1, l2, l3 = st.columns(3)
l1.metric("Long Breakeven", f"{breakeven_long:,.2f}")
l2.metric("Long Floating PnL", f"${pnl_long:,.2f}", delta_color="normal" if pnl_long >= 0 else "inverse")
l3.metric("Long Margin", f"${margin_per_lot * qty:,.2f}")

# Top Metric Cards (Leg 2)
st.markdown("### Short Position (Downside Exposure)")
s1, s2, s3 = st.columns(3)
s1.metric("Short Breakeven", f"{breakeven_short:,.2f}")
s2.metric("Short Floating PnL", f"${pnl_short:,.2f}", delta_color="normal" if pnl_short >= 0 else "inverse")
s3.metric("Short Margin", f"${margin_per_lot * qty:,.2f}")

st.markdown("---")

# Master Net Metrics
m1, m2 = st.columns(2)
m1.metric("Total Margin Locked (Both Legs)", f"${total_margin:,.2f}")
if net_pnl >= 0:
    m2.metric("Net Locked Profit (Spread)", f"+${net_pnl:,.2f}", delta_color="normal")
else:
    m2.metric("Net Locked Loss (Spread)", f"-${abs(net_pnl):,.2f}", delta_color="inverse")

# --- VISUALIZATION ENGINE ---
# Generate price array focusing broadly around the entry prices
center_price = (long_entry + short_entry) / 2
x_min = center_price * 0.7
x_max = center_price * 1.3
x = np.linspace(x_min, x_max, 300)

# Calculate linear PnL arrays
y_long = (x - long_entry) * qty * multiplier
y_short = (short_entry - x) * qty * multiplier
y_net = y_long + y_short

# Plotly Chart
fig = go.Figure()

# Long PnL Line
fig.add_trace(go.Scatter(x=x, y=y_long, name="Long PnL", 
                         line=dict(color="#00FFAA", width=3, dash="dash")))

# Short PnL Line
fig.add_trace(go.Scatter(x=x, y=y_short, name="Short PnL", 
                         line=dict(color="#FF4444", width=3, dash="dash")))

# Master Net Line (The Box)
fig.add_trace(go.Scatter(x=x, y=y_net, name="Net Position (Locked)", 
                         line=dict(color="#FFFFFF", width=5)))

# Zero Line
fig.add_hline(y=0, line_color="gray", line_width=1)

# Markers for Breakevens
fig.add_vline(x=long_entry, line_dash="dot", line_color="#00FFAA", 
              annotation_text="Long Breakeven", annotation_position="bottom right")
fig.add_vline(x=short_entry, line_dash="dot", line_color="#FF4444", 
              annotation_text="Short Breakeven", annotation_position="top right")

# Current Live Price Marker
fig.add_vline(x=current_price, line_dash="solid", line_color="orange", 
              annotation_text="Live Market", annotation_position="top left")

fig.update_layout(
    xaxis_title="Underlying Asset Price",
    yaxis_title="Total Profit / Loss ($)",
    template="plotly_dark",
    height=600,
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)
