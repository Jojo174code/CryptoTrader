# === trader.py ===
import json
import os
from datetime import datetime
import pickle
import numpy as np

WALLET_FILE = "data/wallet.json"
MODEL_FILE = "model.pkl"

# === Wallet Storage ===
def save_wallet(wallet):
    with open(WALLET_FILE, "w") as f:
        json.dump(wallet, f, indent=2)

def load_wallet():
    if os.path.exists(WALLET_FILE):
        with open(WALLET_FILE, "r") as f:
            return json.load(f)
    return {"usd": 10000.0, "holdings": {}, "avg_cost": {}, "hold_times": {}, "cooldowns": {}, "trade_history": []}

# === Load Trained Model ===
if os.path.exists(MODEL_FILE):
    with open(MODEL_FILE, "rb") as f:
        model = pickle.load(f)
else:
    model = None
    print("⚠️ AI model not found. Skipping prediction.")

# === Trade Simulation ===
def simulate_trades(coins):
    wallet = load_wallet()
    trades = []
    timestamp = datetime.utcnow().isoformat()

    for coin in coins:
        name = coin["name"]
        symbol = coin["symbol"]
        price = coin["price"]
        volume = coin["volume"]
        change_1h = coin.get("1h_change", 0) * 100
        change_24h = coin.get("24h_change", 0) * 100

        # === Use AI to predict action ===
        if model:
            features = np.array([[price, volume, change_1h, change_24h]])
            action = model.predict(features)[0]
        else:
            action = "HOLD"

        # === Execute trade based on prediction ===
        if action == "BUY" and wallet["usd"] >= 50:
            wallet["usd"] -= 50
            wallet["holdings"][symbol] = wallet["holdings"].get(symbol, 0) + 50 / price
            wallet["avg_cost"][symbol] = price
            wallet["hold_times"][symbol] = timestamp
            trades.append({
                "timestamp": timestamp,
                "coin": name,
                "symbol": symbol,
                "price": price,
                "action": "BUY",
                "usd_amount": 50.0,
                "volume": volume,
                "portfolio_value": wallet["usd"] + sum(wallet["holdings"][s] * coin["price"] for s in wallet["holdings"] if s == symbol),
                "pnl": round(sum((price - wallet["avg_cost"][s]) * wallet["holdings"][s] for s in wallet["holdings"]), 2)
            })

        if action == "SELL" and symbol in wallet["holdings"]:
            qty = wallet["holdings"][symbol]
            avg = wallet["avg_cost"].get(symbol, 0)
            sell_amount = qty * price
            wallet["usd"] += sell_amount
            del wallet["holdings"][symbol]
            del wallet["avg_cost"][symbol]
            trades.append({
                "timestamp": timestamp,
                "coin": name,
                "symbol": symbol,
                "price": price,
                "action": "SELL",
                "usd_amount": round(sell_amount, 2),
                "volume": volume,
                "portfolio_value": wallet["usd"],
                "pnl": round((price - avg) * qty, 2)
            })

    save_wallet(wallet)
    return trades

# === Logging ===
def log_trades_to_csv(trades, filename="data/trades.csv"):
    import csv
    if not trades:
        print("No trades to log.")
        return

    header = list(trades[0].keys())
    file_exists = os.path.exists(filename)

    with open(filename, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=header)
        if not file_exists or os.stat(filename).st_size == 0:
            writer.writeheader()
        writer.writerows(trades)

    print(f"Logged {len(trades)} simulated trade(s) to {filename}")

