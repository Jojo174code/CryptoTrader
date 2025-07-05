import json
import os

WALLET_FILE = "wallet.json"

DEFAULT_WALLET = {
    "usd": 1000.0,           # Starting USD balance
    "holdings": {},          # {symbol: quantity}
    "avg_cost": {},          # {symbol: average buy price}
    "hold_times": {},        # {symbol: timestamp of last buy}
    "pnl": 0.0,              # Total profit/loss
    "trade_log": []          # Optional: list of trades
}

def load_wallet():
    if os.path.exists(WALLET_FILE):
        with open(WALLET_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_WALLET.copy()

def save_wallet(wallet):
    with open(WALLET_FILE, "w") as f:
        json.dump(wallet, f, indent=4)

def reset_wallet():
    save_wallet(DEFAULT_WALLET.copy())
    print("🔁 Wallet reset to default ($1000 USD).")
