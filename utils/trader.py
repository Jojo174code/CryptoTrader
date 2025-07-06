# === utils/trader.py ===
import csv
import os
import joblib
from datetime import datetime
from utils.wallet import load_wallet, save_wallet

model = joblib.load("model.pkl")  # 🔮 Load ML model once

TRADE_AMOUNT = 50  # USD per trade


def simulate_trades(top_coins):
    wallet = load_wallet()
    trades = []

    for coin in top_coins:
        symbol = coin["symbol"]
        name = coin["name"]
        price = coin["price"]
        volume = coin["volume"]
        one_hour_change = coin["1h_change"]
        twentyfour_hour_change = coin["24h_change"]

        features = [[price, one_hour_change, twentyfour_hour_change, volume]]
        prediction = model.predict(features)[0]

        timestamp = datetime.utcnow().isoformat()
        action = prediction

        if action == "BUY" and wallet["usd"] >= TRADE_AMOUNT:
            wallet["usd"] -= TRADE_AMOUNT
            wallet["holdings"].setdefault(symbol, 0)
            wallet["holdings"][symbol] += TRADE_AMOUNT / price
            wallet["avg_cost"].setdefault(symbol, price)
            wallet["avg_cost"][symbol] = price
            wallet["hold_times"][symbol] = timestamp

        elif action == "SELL" and symbol in wallet["holdings"]:
            qty = wallet["holdings"][symbol]
            cost_basis = wallet["avg_cost"].get(symbol, price)
            proceeds = qty * price
            profit = proceeds - (qty * cost_basis)
            wallet["usd"] += proceeds
            wallet["pnl"] += profit
            del wallet["holdings"][symbol]
            del wallet["avg_cost"][symbol]
            wallet["hold_times"].pop(symbol, None)

        else:
            continue

        portfolio_value = wallet["usd"] + sum(
            wallet["holdings"].get(s, 0) * coin["price"] for s in wallet["holdings"]
        )

        trade = {
            "timestamp": timestamp,
            "coin": name,
            "symbol": symbol,
            "price": price,
            "action": action,
            "usd_amount": TRADE_AMOUNT,
            "volume": volume,
            "portfolio_value": round(portfolio_value, 2),
            "pnl": round(wallet["pnl"], 2)
        }

        wallet["trade_log"].append(trade)
        trades.append(trade)

    save_wallet(wallet)
    return trades


def log_trades_to_csv(trades, path="data/trades.csv"):
    if not trades:
        return
    file_exists = os.path.isfile(path)
    with open(path, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=trades[0].keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(trades)
