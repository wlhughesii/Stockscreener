import time
import requests
import pandas as pd
from tradier_config import get_api_key, get_base_url

def get_put_options(ticker, min_days=25, max_days=60):
    url = f"{get_base_url()}markets/options/chains"
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Accept": "application/json"
    }
    params = {
        "symbol": ticker,
        "greeks": "true",
        "chain_type": "put"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"[{ticker}] Option API error: {response.status_code}")
            return None

        data = response.json()
        options = data.get("options", {}).get("option", [])
        if not options:
            return []

        puts = []
        for opt in options:
            expiry = opt.get("expiration_date")
            days = opt.get("days_to_expiration", 0)
            if not expiry or days < min_days or days > max_days:
                continue

            puts.append({
                "symbol": opt.get("symbol"),
                "strike": opt.get("strike"),
                "bid": opt.get("bid", 0),
                "ask": opt.get("ask", 0),
                "last": opt.get("last", 0),
                "delta": opt.get("greeks", {}).get("delta"),
                "oi": opt.get("open_interest", 0),
                "expiry": expiry,
                "days": days
            })

        return puts

    except Exception as e:
        print(f"[{ticker}] Option error: {e}")
        return None
