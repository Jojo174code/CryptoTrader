import csv
import os
import json
from datetime import datetime

WALLET_FILE = "data/wallet.json"
TRADE_LOG = "data/trades.csv"
TRADE_AMOUNT = 50.0  # $50 per buy trade

def load_wallet():
    if not os.path.exists(WALLET_FILE):
        return {"usd": 10000.0, "holdings": {}, "trade_history": []}
    with open(WALLET_FILE, "r") as f:
        return json.load(f)

def save_wallet(wallet):
    with open(WALLET_FILE, "w") as f:
        json.dump(wallet, f, indent=2)

def simulate_trades(coins):
    trades = []
    wallet = load_wallet()

    for coin in coins:
        action = None
        price = coin["price"]
        symbol = coin["symbol"]

        if coin["1h_change"] > 0:
            action = "BUY"
        elif coin["1h_change"] < 0:
            action = "SELL"

        usd_amount = 0.0

        if action == "BUY" and wallet["usd"] >= TRADE_AMOUNT:
            qty = TRADE_AMOUNT / price
            wallet["usd"] -= TRADE_AMOUNT
            wallet["holdings"][symbol] = wallet["holdings"].get(symbol, 0) + qty
            usd_amount = TRADE_AMOUNT

        elif action == "SELL" and wallet["holdings"].get(symbol, 0) > 0:
            qty = wallet["holdings"][symbol]
            usd_amount = qty * price
            wallet["usd"] += usd_amount
            wallet["holdings"][symbol] = 0

        else:
            continue

        total_value = wallet["usd"]
        for sym, qty in wallet["holdings"].items():
            match = next((c for c in coins if c["symbol"] == sym), None)
            if match:
                total_value += qty * match["price"]

        pnl = total_value - 10000

        trade = {
            "timestamp": datetime.utcnow().isoformat(),
            "coin": coin["name"],
            "symbol": symbol,
            "price": price,
            "action": action,
            "usd_amount": round(usd_amount, 2),
            "volume": coin["volume"],
            "portfolio_value": round(total_value, 2),
            "pnl": round(pnl, 2)
        }

        trades.append(trade)
        wallet["trade_history"].append(trade)

    save_wallet(wallet)
    return trades

def log_trades_to_csv(trades, filename=TRADE_LOG):
    if not trades:
        print("No trades to log.")
        return

    file_exists = os.path.exists(filename)
    with open(filename, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=trades[0].keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(trades)

    print(f"Logged {len(trades)} simulated trade(s) to {filename}")
