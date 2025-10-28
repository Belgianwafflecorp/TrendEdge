"""
screener.py
PerpPulse – step-0 tester:
  - load locally saved tradeable list
  - fetch CoinGecko trending
  - intersect & print
"""
import json
import requests
from pathlib import Path
import json_utils
from CoinGecko import gecko_trending


# Process all exchanges and write one screened file per exchange
EXCHANGES = ["BINANCE", "BYBIT", "HYPERLIQUID"]


def load_tradeable(exchange: str):
    """Return set of bare symbols (BTC, ETH, …) from exchanges/<exchange>.json"""
    return json_utils.load_list_from("exchanges", f"TRADE_ABLE_{exchange}")


def main():
    trending = gecko_trending()

    for exchange in EXCHANGES:
        tradeable = load_tradeable(exchange)
        matched = tradeable & trending          # the '&' test
        final   = sorted(matched)

        # Save the screened result into screened/<EXCHANGE>.json (named exactly as requested)
        out_name = f"{exchange}"
        json_utils.save_list_to("screened", out_name, final)

        # Print a short confirmation to CLI
        out_path = Path(__file__).resolve().parents[1] / "screened" / f"{out_name}.json"
        print(f"Wrote screened list for {exchange} ({len(final)} items) to: {out_path}")

if __name__ == "__main__":
    main()