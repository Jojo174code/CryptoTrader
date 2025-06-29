import pandas as pd
import matplotlib.pyplot as plt
import os

def show_trade_chart(filename="data/trades.csv", output="trade_chart.png"):
    if not os.path.exists(filename):
        print("⚠️ No trade log file found.")
        return

    df = pd.read_csv(filename)

    if df.empty or "timestamp" not in df.columns:
        print("⚠️ No data to plot yet.")
        print(f"Columns found: {list(df.columns)}")
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.sort_values("timestamp", inplace=True)

    plt.figure(figsize=(10, 5))
    for action in ["BUY", "SELL"]:
        sub = df[df["action"] == action]
        plt.scatter(sub["timestamp"], sub["price"],
                    label=f"{action} (${sub['usd_amount'].sum():.2f})", alpha=0.7)

    plt.title("Simulated Crypto Trades Over Time")
    plt.xlabel("Time")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output)
    plt.close()
    print(f"✅ Chart saved to {output}")
