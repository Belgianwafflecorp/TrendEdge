import requests
import json
import logging
from pathlib import Path
import json_utils

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

def binance_perps():
    logger.info("Fetching Binance perpetuals")
    r = requests.get("https://fapi.binance.com/fapi/v1/exchangeInfo", timeout=10).json()
    symbols = {s["symbol"].replace("USDT", "").replace("USDC", "")
               for s in r.get("symbols", [])
               if s.get("contractType") == "PERPETUAL" and s.get("status") == "TRADING"}
    logger.info("Binance perpetuals: %d symbols", len(symbols))
    return symbols

def bybit_perps():
        # Bybit v5 `instruments-info` returns the full list for the requested
        logger.info("Fetching Bybit linear instruments")
        base = "https://api.bybit.com/v5/market/instruments-info"
        try:
            r = requests.get(base, params={"category": "linear"}, timeout=10)
            r.raise_for_status()
            js = r.json()
        except Exception as e:
            logger.exception("Bybit request failed: %s", e)
            return set()

        lst = js.get("result", {}).get("list", [])
        symbols = set()
        for d in lst:
            sym = d.get("symbol")
            if not sym:
                continue
            symbols.add(sym.replace("USDT", "").replace("USDC", ""))

        logger.info("Bybit instruments collected: %d symbols", len(symbols))
        return symbols

def hyperliquid_perps():
    logger.info("Fetching Hyperliquid universes")
    r = requests.post("https://api.hyperliquid.xyz/info", json={"type": "meta"}, timeout=10).json()
    symbols = {u["name"] for u in r.get("universe", []) if not u.get("isDisabled", False)}
    logger.info("Hyperliquid universes: %d symbols", len(symbols))
    return symbols

# Do not perform network calls at import time. Provide an explicit refresh function
# which fetches the lists and writes them to disk.
TRADE_ABLE_BINANCE = set()
TRADE_ABLE_BYBIT = set()
TRADE_ABLE_HYPERLIQUID = set()


def refresh_tradeable_files() -> None:
    """Fetch tradeable symbols for each exchange and save them to disk.

    This function centralizes side effects so importing this module doesn't
    automatically perform network I/O. Call it explicitly when you want to
    refresh the saved JSON files.
    """
    b = binance_perps()
    y = bybit_perps()
    h = hyperliquid_perps()

    # expose as module-level variables
    global TRADE_ABLE_BINANCE, TRADE_ABLE_BYBIT, TRADE_ABLE_HYPERLIQUID
    TRADE_ABLE_BINANCE = b
    TRADE_ABLE_BYBIT = y
    TRADE_ABLE_HYPERLIQUID = h

    json_utils.save_list_to("exchanges", "TRADE_ABLE_BINANCE", TRADE_ABLE_BINANCE)
    json_utils.save_list_to("exchanges", "TRADE_ABLE_BYBIT", TRADE_ABLE_BYBIT)
    json_utils.save_list_to("exchanges", "TRADE_ABLE_HYPERLIQUID", TRADE_ABLE_HYPERLIQUID)
    logger.info("Saved all exchange lists to disk")


if __name__ == "__main__":
    refresh_tradeable_files()