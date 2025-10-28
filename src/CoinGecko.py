import requests
import json_utils


def gecko_trending():
    """Return a set of uppercase symbols from CoinGecko's trending API."""
    r = requests.get("https://api.coingecko.com/api/v3/search/trending").json()
    return {coin["item"]["symbol"].upper() for coin in r["coins"]}


def save_gecko_trending(var_name: str = "GECKO_TRENDING"):
    """Fetch gecko_trending() and save the result as JSON into coinGecko/<var_name>.json.

    Returns the Path written.
    """
    data = gecko_trending()
    return json_utils.save_list_to("coinGecko", var_name, data)


if __name__ == "__main__":
    path = save_gecko_trending()
    print(f"Wrote gecko trending JSON to: {path}")

