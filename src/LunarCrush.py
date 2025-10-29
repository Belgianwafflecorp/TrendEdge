"""
lunarcrush.py
To use lunarCrush you need a payed subscription.
Use promo code: BELGIANWAFFLE 
To get a 15% subscription discount.
"""
import os
import requests
import logging
import json_utils
from typing import Set, Optional, List
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

BASE = "https://lunarcrush.com/api4"
KEY = os.getenv("LUNAR_KEY")
HEAD = {"Authorization": f"Bearer {KEY}"}


def galaxy50() -> Set[str]:
    """Coins whose Galaxy Score ≥ 50 right now."""
    logger.info("Fetching LunarCrush galaxy50 list")
    if not KEY:
        logger.warning("LUNAR_KEY not set; skipping LunarCrush galaxy50 fetch and returning empty set")
        return set()

    try:
        r = requests.get(f"{BASE}/public/coins/list/v1",
                         params={"galaxy_score_min": 50, "limit": 200},
                         headers=HEAD,
                         timeout=10)
        r.raise_for_status()
        items = {c["symbol"].upper() for c in r.json().get("data", [])}
    except requests.RequestException as e:
        logger.exception("Failed to fetch LunarCrush galaxy50: %s", e)
        return set()
    logger.info("LunarCrush galaxy50: %d symbols", len(items))
    return items


def alt_rank_top100() -> Set[str]:
    """Top-100 by AltRank (lower = hotter)."""
    logger.info("Fetching LunarCrush alt_rank top100")
    if not KEY:
        logger.warning("LUNAR_KEY not set; skipping LunarCrush alt_rank fetch and returning empty set")
        return set()

    try:
        r = requests.get(f"{BASE}/public/coins/list/v1",
                         params={"sort": "alt_rank", "limit": 100},
                         headers=HEAD,
                         timeout=10)
        r.raise_for_status()
        items = {c["symbol"].upper() for c in r.json().get("data", [])}
    except requests.RequestException as e:
        logger.exception("Failed to fetch LunarCrush alt_rank top100: %s", e)
        return set()
    logger.info("LunarCrush alt_rank top100: %d symbols", len(items))
    return items


def save_lunar_lists(var_name: Optional[str] = None) -> List[str]:
    """Save LunarCrush lists into `lunarCrush/` folder.

    - If var_name is None, saves both `GALAXY50` and `ALT_RANK_TOP100`.
    - If var_name matches one of the names (case-insensitive), saves only that list.

    Returns list of written path strings.
    """
    written: List[str] = []

    def _save(name: str, data: Set[str]):
        p = json_utils.save_list_to("lunarCrush", name, data)
        written.append(str(p))

    if var_name is None:
        _save("GALAXY50", galaxy50())
        _save("ALT_RANK_TOP100", alt_rank_top100())
        return written

    key = var_name.upper()
    if key in ("GALAXY50", "GALAXY_50"):
        _save("GALAXY50", galaxy50())
        return written
    if key in ("ALT_RANK_TOP100", "ALT_RANK", "TOP100"):
        _save("ALT_RANK_TOP100", alt_rank_top100())
        return written

    raise ValueError(f"Unknown lunar list name: {var_name}")


if __name__ == "__main__":
    paths = save_lunar_lists()
    for p in paths:
        print(f"Wrote lunar list to: {p}")