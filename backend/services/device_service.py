"""
Loads device data from database/devices.json and provides simple lookup
helpers. Swap this module for a real database-backed implementation later
without touching the routes or the estimator.
"""
import json
from functools import lru_cache
from typing import List, Optional

from config import DEVICES_FILE
from models.device import Device


@lru_cache(maxsize=1)
def _load_devices() -> List[Device]:
    with open(DEVICES_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [Device(**item) for item in raw]


def get_brands() -> List[str]:
    seen = []
    for d in _load_devices():
        if d.brand not in seen:
            seen.append(d.brand)
    return seen


def get_devices(brand: Optional[str] = None, search: Optional[str] = None) -> List[Device]:
    devices = _load_devices()
    if brand:
        devices = [d for d in devices if d.brand.lower() == brand.lower()]
    if search:
        q = search.lower().strip()
        devices = [d for d in devices if q in d.model.lower() or q in d.brand.lower()]
    return devices


def get_device(device_id: str) -> Optional[Device]:
    for d in _load_devices():
        if d.id == device_id:
            return d
    return None
