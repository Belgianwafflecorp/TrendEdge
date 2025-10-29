import json
import requests
from pathlib import Path
import json_utils
import logging
from CoinGecko import gecko_trending, gecko_top100, save_gecko_lists
from LunarCrush import galaxy50, alt_rank_top100, save_lunar_lists

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

    # Ensure LunarCrush lists are saved to disk so lunarCrush/ has latest data.
    try:
        lpaths = save_lunar_lists()
        for p in lpaths:
            logger.info("Saved LunarCrush list: %s", p)
    except Exception:
        logger.exception("Failed to save LunarCrush lists")

    # Prefer loading the CoinGecko lists from disk (written by save_gecko_lists()).
    # This avoids calling the CoinGecko APIs twice.
    # Load CoinGecko lists from disk (preferred) and fall back to live fetch on error
    try:
        trending_gecko = json_utils.load_list_from("coinGecko", "GECKO_TRENDING")
    except Exception:
        logger.info("coinGecko/GECKO_TRENDING.json missing or unreadable; fetching live")
        trending_gecko = gecko_trending()

    try:
        top100_gecko = json_utils.load_list_from("coinGecko", "GECKO_TOP100")
    except Exception:
        logger.info("coinGecko/GECKO_TOP100.json missing or unreadable; fetching live")
        top100_gecko = gecko_top100()

    # Load LunarCrush lists from disk (preferred) and fall back to live fetch on error
    try:
        galaxy_lunar = json_utils.load_list_from("lunarCrush", "GALAXY50")
    except Exception:
        logger.info("lunarCrush/GALAXY50.json missing or unreadable; fetching live")
        galaxy_lunar = galaxy50()

    try:
        top100_lunar = json_utils.load_list_from("lunarCrush", "ALT_RANK_TOP100")
    except Exception:
        logger.info("lunarCrush/ALT_RANK_TOP100.json missing or unreadable; fetching live")
        top100_lunar = alt_rank_top100()

    # Form the OR unions requested by the user
    combined_trending = trending_gecko | galaxy_lunar      # gecko trending OR lunar galaxy50
    combined_top100 = top100_gecko | top100_lunar         # gecko top100 OR lunar top100

    for exchange in EXCHANGES:
        tradeable = load_tradeable(exchange)
        # Keep only symbols that are in both combined sets (top100 OR) AND (trending OR galaxy)
        matched = tradeable & combined_trending & combined_top100
        final = sorted(matched)

        # Save the screened result into screened/<EXCHANGE>.json (named exactly as requested)
        out_name = f"{exchange}"
        p = json_utils.save_list_to("screened", out_name, final)
        logger.info("Wrote screened list for %s (%d items) to: %s", exchange, len(final), p)

if __name__ == "__main__":
    main()