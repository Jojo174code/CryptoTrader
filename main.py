import time
from utils.scanner import get_top_gainers
from utils.trader import simulate_trades, log_trades_to_csv
from utils.visualize import show_trade_chart

def run_bot():
    top_coins = get_top_gainers()
    print("Top Gainers:")
    for coin in top_coins:
        print(coin)

    trades = simulate_trades(top_coins)
    print("\nSimulated Trades:")
    for trade in trades:
        print(trade)

    log_trades_to_csv(trades)

# 🔁 Fast loop for testing
loop_count = 0
while True:
    print("\n===== Running Bot Cycle =====")
    run_bot()
    
    loop_count += 1
    if loop_count % 1 == 0:
        print("📊 Showing chart of recent trades...")
        show_trade_chart()
    
    print("⏳ Sleeping for 30 seconds...\n")
    time.sleep(30)
