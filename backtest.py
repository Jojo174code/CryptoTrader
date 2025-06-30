# === backtest.py ===
import pandas as pd
import os
import json
from datetime import datetime
from utils.trader import simulate_trades, log_trades_to_csv, save_wallet

HISTORICAL_FOLDER = "data/historical"
BACKTEST_LOG = "data/backtest_trades.csv"

def reset_wallet():
    wallet = {
        "usd": 10000.0,
        "holdings": {},
        "avg_cost": {},
        "hold_times": {},
        "cooldowns": {},
        "trade_history": []
    }
    save_wallet(wallet)

def load_historical_data():
    combined = []
    for file in os.listdir(HISTORICAL_FOLDER):
        if file.endswith(".csv"):
            symbol = file.replace(".csv", "").lower()
            df = pd.read_csv(os.path.join(HISTORICAL_FOLDER, file))
            df["symbol"] = symbol
            df["name"] = symbol.capitalize()
            combined.append(df)
    return pd.concat(combined).sort_values("timestamp")

def run_backtest():
    print("Running backtest simulation...")
    reset_wallet()
    all_data = load_historical_data()
    all_data["timestamp"] = pd.to_datetime(all_data["timestamp"])
    timestamps = sorted(all_data["timestamp"].unique())

    all_trades = []
    for ts in timestamps:
        frame = all_data[all_data["timestamp"] == ts]
        coins = []
        for row in frame.itertuples():
            coins.append({
                "name": row.name,
                "symbol": row.symbol,
                "price": row.price,
                "volume": row.volume,
                "1h_change": 0.6,     # Force BUY trigger (default +0.6%)
                "24h_change": 0.8
            })
        trades = simulate_trades(coins)
        if trades:
            print(f"[{ts}] Executed {len(trades)} trade(s)")
        all_trades.extend(trades)

    log_trades_to_csv(all_trades, filename=BACKTEST_LOG)

    if not all_trades:
        print("⚠️ No trades were executed. Strategy may be too strict or data too flat.")
    else:
        print(f"✅ Backtest complete. Logged {len(all_trades)} trades to {BACKTEST_LOG}")

if __name__ == "__main__":
    run_backtest()
