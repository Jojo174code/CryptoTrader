# === main.py ===
import time
from utils.scanner import get_top_gainers
from utils.trader import simulate_trades, log_trades_to_csv
from utils.visualize import show_trade_chart
from utils.wallet import load_wallet, reset_wallet

CYCLE_INTERVAL = 30  # seconds

def run_bot():
    print("\n===== Running Bot Cycle =====")
    reset_wallet()
    wallet = load_wallet()
    print("👛 Wallet loaded:", wallet)

    top_coins = get_top_gainers()
    print("Top Gainers:")
    for coin in top_coins:
        print(coin)

    trades = simulate_trades(top_coins)
    print("\nSimulated Trades:")
    for t in trades:
        print(t)

    log_trades_to_csv(trades)
    print("📊 Showing chart of recent trades...")
    show_trade_chart()

if __name__ == "__main__":
    print("🟢 Bot starting...")
    while True:
        run_bot()
        print("⏳ Sleeping for 30 seconds...\n")
        time.sleep(CYCLE_INTERVAL)