import requests
from tradier_config import TRADIER_ACCESS_TOKEN, TRADIER_BASE_URL
from tradier_config import get_api_key, get_base_url

HEADERS = {
    "Authorization": f"Bearer " + TRADIER_ACCESS_TOKEN,
    "Accept": "application/json"
}


def get_quote(ticker):
    url = f"{TRADIER_BASE_URL}markets/quotes"
    try:
        response = requests.get(url, headers=HEADERS, params={"symbols": ticker})
        if response.status_code != 200:
            print(f"[{ticker}] Quote API error {response.status_code}")
            return {}
        data = response.json()
        quote = data.get("quotes", {}).get("quote", {})
        if not quote:
            print(f"[{ticker}] ⚠️ No quote data returned.")
        return {
            "price": quote.get("last"),
            "beta": quote.get("beta"),
            "type": quote.get("type"),
            "earnings": quote.get("earnings"),
            "week_52_low": quote.get("week_52_low"),
            "week_52_high": quote.get("week_52_high"),
            "pe": quote.get("pe")
        }
    except Exception as e:
        print(f"[{ticker}] ⚠️ Quote exception: {e}")
        return {}


def get_expirations(ticker):
    url = f"{TRADIER_BASE_URL}markets/options/expirations"
    try:
        response = requests.get(url, headers=HEADERS, params={"symbol": ticker})
        if response.status_code != 200:
            print(f"[{ticker}] Expiration API error {response.status_code}")
            return []
        data = response.json()
        expirations = data.get("expirations", {}).get("date", [])
        if not expirations:
            print(f"[{ticker}] ⚠️ No expirations returned.")
        return expirations
    except Exception as e:
        print(f"[{ticker}] ⚠️ Expiration exception: {e}")
        return []


def get_option_chain(symbol, expiration, option_type="put"):
    """
    Fetches the option chain for a given symbol and expiration date.
    Filters for 'put' or 'call' options only if specified.
    """
    url = f"{get_base_url()}markets/options/chains"
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Accept": "application/json"
    }
    params = {
        "symbol": symbol,
        "expiration": expiration,
        "greeks": "true"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"[{symbol}] Option API error: {response.status_code}")
        return None

    try:
        data = response.json()
        options = data.get("options", {}).get("option", [])
        if options is None:
            return []
        # Filter by option_type
        return [opt for opt in options if opt["option_type"].lower() == option_type.lower()]
    except Exception as e:
        print(f"[{symbol}] Error parsing options: {e}")
        return None
