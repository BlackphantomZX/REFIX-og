"""
Loads repair category + dynamic question data from database/repairs.json.
"""
import json
from functools import lru_cache
from typing import List, Optional

from config import REPAIRS_FILE
from models.repair import Repair


@lru_cache(maxsize=1)
def _load_repairs() -> List[Repair]:
    with open(REPAIRS_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [Repair(**item) for item in raw]


def get_repairs() -> List[Repair]:
    return _load_repairs()


def get_repair(repair_id: str) -> Optional[Repair]:
    for r in _load_repairs():
        if r.id == repair_id:
            return r
    return None
