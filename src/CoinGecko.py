import requests
import json_utils
from typing import Optional, List


def gecko_trending() -> set[str]:
    """Return a set of uppercase symbols from CoinGecko's trending API."""
    r = requests.get("https://api.coingecko.com/api/v3/search/trending").json()
    return {coin["item"]["symbol"].upper() for coin in r["coins"]}


def gecko_top100(timeout: float = 10.0) -> set[str]:
    """Return set of uppercase symbols for CoinGecko top-100 by market cap."""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 100, "page": 1}
    headers = {"User-Agent": "TrendEdge/1.0 (+https://your.repo.or.site)"}

    try:
        resp = requests.get(url, params=params, timeout=timeout, headers=headers)
        resp.raise_for_status()
        data = resp.json()  # expected: list of coin dicts
        return {(coin.get("symbol") or "").upper().strip() for coin in data if coin.get("symbol")}
    except requests.RequestException:
        # log or handle network/HTTP errors as appropriate; return empty set here
        return set()


def save_gecko_lists(var_name: Optional[str] = None) -> List[str]:
    """Save one or all CoinGecko symbol-lists into the `coinGecko/` folder.

    - If var_name is None, saves all available lists and returns list of written paths.
    - If var_name matches 'GECKO_TRENDING' or 'TRENDING' it saves only the trending list.
    - If var_name matches 'GECKO_TOP100' or 'TOP100' it saves only the top-100 list.

    Returns a list of Path-like strings written.
    """
    written = []

    def _save(name: str, data: set[str]):
        p = json_utils.save_list_to("coinGecko", name, data)
        written.append(str(p))

    if var_name is None:
        _save("GECKO_TRENDING", gecko_trending())
        _save("GECKO_TOP100", gecko_top100())
        return written

    key = var_name.upper()
    if key in ("GECKO_TRENDING", "TRENDING"):
        _save("GECKO_TRENDING", gecko_trending())
        return written
    if key in ("GECKO_TOP100", "TOP100"):
        _save("GECKO_TOP100", gecko_top100())
        return written

    raise ValueError(f"Unknown gecko list name: {var_name}")


if __name__ == "__main__":
    paths = save_gecko_lists()
    for p in paths:
        print(f"Wrote gecko list to: {p}")

