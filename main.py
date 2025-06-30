# === main.py ===
import time
from utils.scanner import get_top_gainers
from utils.trader import simulate_trades, log_trades_to_csv
from utils.visualize import show_trade_chart

CYCLE_INTERVAL = 30  # seconds

def run_bot():
    print("\n===== Running Bot Cycle =====")
    top_coins = get_top_gainers()
    print("Top Gainers:")
    for coin in top_coins:
        print(coin)

    trades = simulate_trades(top_coins)
    print("\nSimulated Trades:")
    for t in trades:
        print(t)

    log_trades_to_csv(trades)
    print("\U0001F4CA Showing chart of recent trades...")
    show_trade_chart()

if __name__ == "__main__":
    while True:
        run_bot()
        print("\u23F3 Sleeping for 30 seconds...\n")
        time.sleep(CYCLE_INTERVAL)
