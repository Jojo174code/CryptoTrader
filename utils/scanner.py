import requests

def get_top_gainers(limit=5):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "percent_change_1h_desc",
        "per_page": limit,
        "page": 1,
        "price_change_percentage": "1h,24h"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("Failed to fetch data")
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        return []

    data = response.json()
    gainers = []
    for coin in data:
        gainers.append({
            "name": coin["name"],
            "symbol": coin["symbol"],
            "price": coin["current_price"],
            "1h_change": coin["price_change_percentage_1h_in_currency"],
            "24h_change": coin["price_change_percentage_24h_in_currency"],
            "volume": coin["total_volume"]
        })
    return gainers
