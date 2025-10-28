import requests
import json
from pathlib import Path

def binance_perps():
    r = requests.get("https://fapi.binance.com/fapi/v1/exchangeInfo").json()
    return {s["symbol"].replace("USDT","").replace("USDC","")
            for s in r["symbols"]
            if s["contractType"]=="PERPETUAL" and s["status"]=="TRADING"}

def bybit_perps():
    r = requests.get("https://api.bybit.com/v5/market/instruments-info?category=linear").json()
    return {d["symbol"].replace("USDT","").replace("USDC","")
            for d in r["result"]["list"]}

def hyperliquid_perps():
    r = requests.post("https://api.hyperliquid.xyz/info", json={"type":"meta"}).json()
    return {u["name"] for u in r["universe"] if not u.get("isDisabled",False)}

TRADE_ABLE_BINANCE = binance_perps()
TRADE_ABLE_BYBIT = bybit_perps()
TRADE_ABLE_HYPERLIQUID = hyperliquid_perps()


def _save_tradeables(var_name: str, data):
    """Save a collection of symbols to exchanges/<VAR_NAME>.json as a sorted list."""
    # Resolve project root (one level up from src/) and the exchanges folder
    exchanges_dir = Path(__file__).resolve().parents[1] / "exchanges"
    exchanges_dir.mkdir(parents=True, exist_ok=True)
    out_path = exchanges_dir / f"{var_name}.json"
    # Convert sets to sorted lists for stable output
    serializable = sorted(list(data))
    with out_path.open("w", encoding="utf8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)


# Persist the computed tradeable symbol lists to JSON files
_save_tradeables("TRADE_ABLE_BINANCE", TRADE_ABLE_BINANCE)
_save_tradeables("TRADE_ABLE_BYBIT", TRADE_ABLE_BYBIT)
_save_tradeables("TRADE_ABLE_HYPERLIQUID", TRADE_ABLE_HYPERLIQUID)