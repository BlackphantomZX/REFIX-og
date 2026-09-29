"""
Loads database/pricing.json and exposes lookups the estimator needs:
base part/labor ranges per (repair_id, device tier), and regional price
multipliers. Kept separate from estimator.py so pricing data can be edited
without touching any estimation logic.
"""
import json
from functools import lru_cache
from typing import Dict, Tuple

from config import PRICING_FILE

DEFAULT_TIER = "mid"


@lru_cache(maxsize=1)
def _load_pricing_doc() -> dict:
    with open(PRICING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_labor_share() -> float:
    return _load_pricing_doc()["labor_share_of_min"]


def get_currency() -> str:
    return _load_pricing_doc().get("currency", "INR")


def get_pricing_note() -> str:
    return _load_pricing_doc().get("note", "")


def base_range_for(repair_id: str, tier: str) -> Tuple[int, int]:
    """Returns (min, max) base price in INR for a repair type + device tier."""
    tiers = _load_pricing_doc()["tier_pricing"].get(repair_id)
    if tiers is None:
        raise KeyError(f"No pricing configured for repair_id '{repair_id}'")
    r = tiers.get(tier) or tiers.get(DEFAULT_TIER)
    return int(r[0]), int(r[1])


def get_region(region_id: str) -> Dict:
    regions = _load_pricing_doc()["regions"]
    for r in regions:
        if r["id"] == (region_id or ""):
            return r
    # Fall back to the India-wide default (empty id, multiplier 1.0)
    return next(r for r in regions if r["id"] == "")


def get_regions() -> list:
    return _load_pricing_doc()["regions"]
