# === dashboard.py ===
import streamlit as st
import pandas as pd
import json
import os
from streamlit_autorefresh import st_autorefresh
import matplotlib.pyplot as plt

WALLET_FILE = "data/wallet.json"
TRADE_LOG = "data/trades.csv"
CHART_FILE = "trade_chart.png"

st.set_page_config(page_title="Crypto Bot Dashboard", layout="wide")
st_autorefresh(interval=10000, limit=None, key="refresh")

st.title("📊 Crypto Auto-Trader Dashboard")

def load_wallet():
    if os.path.exists(WALLET_FILE):
        with open(WALLET_FILE, "r") as f:
            return json.load(f)
    return {"usd": 0, "holdings": {}, "avg_cost": {}, "hold_times": {}, "cooldowns": {}, "trade_history": []}

def load_trades():
    if os.path.exists(TRADE_LOG):
        return pd.read_csv(TRADE_LOG)
    return pd.DataFrame()

def show_trade_chart():
    if os.path.exists(CHART_FILE):
        st.image(CHART_FILE, caption="Trade Chart", use_column_width=False, width=600)
    else:
        st.warning("No trade chart available yet.")

wallet = load_wallet()
trades = load_trades()

st.header("💰 Paper Wallet")
st.metric("USD Balance", f"${wallet['usd']:.2f}")

st.subheader("🪙 Holdings & Performance")
if wallet["holdings"]:
    perf_data = []
    for symbol, qty in wallet["holdings"].items():
        cost = wallet["avg_cost"].get(symbol, 0)
        if not trades.empty and symbol in trades.symbol.values:
            coin_trades = trades[trades.symbol == symbol]
            current_price = coin_trades["price"].iloc[-1] if not coin_trades.empty else cost
        else:
            current_price = cost
        value = qty * current_price
        gain_pct = ((current_price - cost) / cost * 100) if cost else 0
        perf_data.append({
            "Coin": symbol.upper(),
            "Qty": round(qty, 6),
            "Buy Price": round(cost, 2),
            "Current Price": round(current_price, 2),
            "Value (USD)": round(value, 2),
            "Gain %": round(gain_pct, 2)
        })
    df_perf = pd.DataFrame(perf_data)
    st.dataframe(df_perf.set_index("Coin"))
else:
    st.write("No holdings yet.")

# === Pie Chart ===
if wallet["holdings"]:
    labels = []
    sizes = []
    for symbol, qty in wallet["holdings"].items():
        current_price = trades[trades.symbol == symbol].price.iloc[-1] if not trades.empty and symbol in trades.symbol.values else 0
        labels.append(symbol.upper())
        sizes.append(qty * current_price)
    fig1, ax1 = plt.subplots(figsize=(5, 5))
    ax1.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    ax1.axis("equal")
    st.pyplot(fig1, use_container_width=False)

# === Trade History ===
st.header("📄 Trade History")
if not trades.empty:
    st.dataframe(trades.tail(20))
else:
    st.write("No trades logged yet.")

# === Trade Chart ===
st.header("📈 Trade Chart")
show_trade_chart()

# === P&L Trend ===
st.header("📉 P&L Over Time")
if not trades.empty and "pnl" in trades.columns:
    trades["timestamp"] = pd.to_datetime(trades["timestamp"])
    fig2, ax2 = plt.subplots(figsize=(7, 3))
    ax2.plot(trades["timestamp"], trades["pnl"], marker='o', linestyle='-', linewidth=1)
    ax2.set_title("P&L Over Time")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("P&L ($)")
    ax2.grid(True)
    st.pyplot(fig2, use_container_width=False)
    st.metric("📈 Net P&L", f"${trades['pnl'].iloc[-1]:.2f}")
else:
    st.write("No portfolio data yet.")

# === Trade Alerts ===
st.header("📣 Trade Alerts")
if not trades.empty:
    for row in trades.tail(5).itertuples():
        st.info(f"[{row.timestamp}] {row.action} {row.symbol.upper()} @ ${row.price}")

