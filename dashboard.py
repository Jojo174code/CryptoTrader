import streamlit as st
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh


WALLET_FILE = "data/wallet.json"
TRADE_LOG = "data/trades.csv"
CHART_FILE = "trade_chart.png"

def load_wallet():
    if os.path.exists(WALLET_FILE):
        with open(WALLET_FILE, "r") as f:
            return json.load(f)
    return {"usd": 0, "holdings": {}, "trade_history": []}

def load_trades():
    if os.path.exists(TRADE_LOG):
        return pd.read_csv(TRADE_LOG)
    return pd.DataFrame()

def show_trade_chart():
    if os.path.exists(CHART_FILE):
        st.image(CHART_FILE, caption="Trade Chart", use_column_width=True)
    else:
        st.warning("No trade chart available yet.")

st.set_page_config(page_title="Crypto Bot Dashboard", layout="wide")
st.title("📊 Crypto Auto-Trader Dashboard")

st_autorefresh(interval=10000, limit=None, key="refresh")



wallet = load_wallet()
trades = load_trades()

st.header("💰 Paper Wallet")
st.metric("USD Balance", f"${wallet['usd']:.2f}")

st.subheader("🪙 Holdings")
if wallet["holdings"]:
    for symbol, qty in wallet["holdings"].items():
        st.write(f"{symbol.upper()}: {qty:.6f}")
else:
    st.write("No holdings yet.")

st.header("📄 Trade History")
if not trades.empty:
    st.dataframe(trades.tail(20))
else:
    st.write("No trades logged yet.")

st.header("📈 Trade Chart")
show_trade_chart()

st.header("📉 Portfolio Value Over Time")
if not trades.empty and "portfolio_value" in trades.columns:
    trades["timestamp"] = pd.to_datetime(trades["timestamp"])
    st.line_chart(data=trades, x="timestamp", y="portfolio_value")
    st.metric("📈 Net P&L", f"${trades['pnl'].iloc[-1]:.2f}")
else:
    st.write("No portfolio data yet.")
