# === trader.py ===
import csv
import os
import json
from datetime import datetime, timedelta

WALLET_FILE = "data/wallet.json"
TRADE_LOG = "data/trades.csv"
TRADE_AMOUNT = 50.0
VOLUME_THRESHOLD = 10_000_000
PROFIT_TARGET = 0.05  # 5%
LOSS_CUTOFF = -0.03    # -3%
MAX_HOLDINGS = 5
HOLD_TIME_MIN = 5      # minutes
COOLDOWN_MIN = 3       # minutes

def load_wallet():
    if not os.path.exists(WALLET_FILE):
        return {
            "usd": 10000.0,
            "holdings": {},
            "avg_cost": {},
            "hold_times": {},
            "cooldowns": {},
            "trade_history": []
        }
    with open(WALLET_FILE, "r") as f:
        return json.load(f)

def save_wallet(wallet):
    with open(WALLET_FILE, "w") as f:
        json.dump(wallet, f, indent=2)

def simulate_trades(coins):
    trades = []
    wallet = load_wallet()
    now = datetime.utcnow()

    for coin in coins:
        symbol = coin["symbol"]
        price = coin["price"]
        volume = coin["volume"]
        change_1h = coin["1h_change"]
        change_24h = coin["24h_change"]

        qty_held = wallet["holdings"].get(symbol, 0)
        avg_cost = wallet["avg_cost"].get(symbol)
        last_buy_time = wallet["hold_times"].get(symbol)
        cooldown_expiry = wallet["cooldowns"].get(symbol)
        action = None
        usd_amount = 0.0

        # Parse times
        if last_buy_time:
            last_buy_time = datetime.fromisoformat(last_buy_time)
        if cooldown_expiry:
            cooldown_expiry = datetime.fromisoformat(cooldown_expiry)

        # === SELL ===
        if qty_held > 0 and avg_cost:
            hold_ok = last_buy_time and (now - last_buy_time).total_seconds() / 60 >= HOLD_TIME_MIN
            change = (price - avg_cost) / avg_cost
            if hold_ok and (change >= PROFIT_TARGET or change <= LOSS_CUTOFF):
                usd_amount = qty_held * price
                wallet["usd"] += usd_amount
                wallet["holdings"].pop(symbol)
                wallet["avg_cost"].pop(symbol)
                wallet["hold_times"].pop(symbol)
                action = "SELL"

        # === BUY ===
        elif change_1h > 1 and change_24h > 0 and volume > VOLUME_THRESHOLD:
            in_cooldown = cooldown_expiry and now < cooldown_expiry
            if not in_cooldown and len(wallet["holdings"]) < MAX_HOLDINGS and wallet["usd"] >= TRADE_AMOUNT:
                qty = TRADE_AMOUNT / price
                wallet["usd"] -= TRADE_AMOUNT
                wallet["holdings"][symbol] = wallet["holdings"].get(symbol, 0) + qty
                current_total = wallet["avg_cost"].get(symbol, 0) * wallet["holdings"].get(symbol, 0)
                new_avg = ((current_total + TRADE_AMOUNT) / (wallet["holdings"][symbol])) if current_total else price
                wallet["avg_cost"][symbol] = new_avg
                wallet["hold_times"][symbol] = now.isoformat()
                wallet["cooldowns"][symbol] = (now + timedelta(minutes=COOLDOWN_MIN)).isoformat()
                usd_amount = TRADE_AMOUNT
                action = "BUY"

        # Log trade if action happened
        if action:
            total_value = wallet["usd"]
            for sym, qty in wallet["holdings"].items():
                match = next((c for c in coins if c["symbol"] == sym), None)
                if match:
                    total_value += qty * match["price"]

            pnl = total_value - 10000

            trades.append({
                "timestamp": now.isoformat(),
                "coin": coin["name"],
                "symbol": symbol,
                "price": price,
                "action": action,
                "usd_amount": round(usd_amount, 2),
                "volume": volume,
                "portfolio_value": round(total_value, 2),
                "pnl": round(pnl, 2)
            })
            wallet["trade_history"].append(trades[-1])

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
