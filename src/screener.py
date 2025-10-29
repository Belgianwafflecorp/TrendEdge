import json
import requests
from pathlib import Path
import json_utils
from CoinGecko import gecko_trending, gecko_top100, save_gecko_lists
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


# Process all exchanges and write one screened file per exchange
EXCHANGES = ["BINANCE", "BYBIT", "HYPERLIQUID"]

# When True, import (and reload) `TradeAblePairs` before screening so exchange
# JSON files are regenerated from the live APIs. Set to False to skip network calls.
REFRESH_EXCHANGES = True

def load_tradeable(exchange: str):
    """Return set of bare symbols (BTC, ETH, …) from exchanges/<exchange>.json"""
    return json_utils.load_list_from("exchanges", f"TRADE_ABLE_{exchange}")


def main():
    # Optionally regenerate exchange JSONs by importing/reloading TradeAblePairs
    if REFRESH_EXCHANGES:
        try:
            import TradeAblePairs
            # Call the explicit refresh function instead of relying on import-time side effects
            TradeAblePairs.refresh_tradeable_files()
            logger.info("Refreshed exchange lists from TradeAblePairs.")
        except Exception as e:
            logger.exception("Failed to refresh TradeAblePairs: %s", e)

    # Ensure CoinGecko lists are saved to disk so coinGecko/ has latest data.
    try:
        paths = save_gecko_lists()
        for p in paths:
            logger.info("Saved CoinGecko list: %s", p)
    except Exception:
        logger.exception("Failed to save CoinGecko lists")

    # Prefer loading the CoinGecko lists from disk (written by save_gecko_lists()).
    # This avoids calling the CoinGecko APIs twice.
    try:
        trending = json_utils.load_list_from("coinGecko", "GECKO_TRENDING")
    except Exception:
        logger.info("coinGecko/GECKO_TRENDING.json missing or unreadable; fetching live")
        trending = gecko_trending()

    try:
        top100 = json_utils.load_list_from("coinGecko", "GECKO_TOP100")
    except Exception:
        logger.info("coinGecko/GECKO_TOP100.json missing or unreadable; fetching live")
        top100 = gecko_top100()

    for exchange in EXCHANGES:
        tradeable = load_tradeable(exchange)
        matched = tradeable & trending & top100  # the '&' test
        final   = sorted(matched)

        # Save the screened result into screened/<EXCHANGE>.json (named exactly as requested)
        out_name = f"{exchange}"
        json_utils.save_list_to("screened", out_name, final)

    # Print a short confirmation to CLI
    out_path = Path(__file__).resolve().parents[1] / "screened" / f"{out_name}.json"
    logger.info("Wrote screened list for %s (%d items) to: %s", exchange, len(final), out_path)

if __name__ == "__main__":
    main()