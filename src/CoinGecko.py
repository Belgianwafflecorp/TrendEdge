import requests
import json
from pathlib import Path


def gecko_trending():
    """Return a set of uppercase symbols from CoinGecko's trending API."""
    r = requests.get("https://api.coingecko.com/api/v3/search/trending").json()
    return {coin["item"]["symbol"].upper() for coin in r["coins"]}


def save_gecko_trending(var_name: str = "GECKO_TRENDING"):
    """Fetch gecko_trending() and save the result as JSON into coinGecko/<var_name>.json.

    The JSON is a sorted list for stable output.
    Returns the path written.
    """
    data = gecko_trending()
    serializable = sorted(list(data))

    out_dir = Path(__file__).resolve().parents[1] / "coinGecko"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{var_name}.json"
    with out_path.open("w", encoding="utf8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)
    return out_path



path = save_gecko_trending()
print(f"Wrote gecko trending JSON to: {path}")

