import requests
import json
from pathlib import Path
import json_utils

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


# Persist the computed tradeable symbol lists to JSON files (both exchanges/ and coinGecko/)
json_utils.save_list_to_both("TRADE_ABLE_BINANCE", TRADE_ABLE_BINANCE)
json_utils.save_list_to_both("TRADE_ABLE_BYBIT", TRADE_ABLE_BYBIT)
json_utils.save_list_to_both("TRADE_ABLE_HYPERLIQUID", TRADE_ABLE_HYPERLIQUID)