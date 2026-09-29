"""
Repair cost estimation engine.

This is a direct port of the estimation logic that originally lived in the
browser-only prototype (estimateCategory / combineEstimates in the artifact's
inline JavaScript). The behaviour is intentionally unchanged -- only the
language and data source changed (pricing now comes from pricing.json via
services/pricing.py instead of a hardcoded JS object).

Nothing in here should reference HTTP, FastAPI, or request/response shapes --
that translation happens in routes/estimates.py. This module only knows about
plain Python data (dicts, tuples).
"""
import math
from typing import Dict, List, Optional, Tuple

from services import pricing as pricing_service

CONFIDENCE_RANK = {"high": 3, "moderate": 2, "low": 1}


def _lower_confidence(a: str, b: str) -> str:
    return a if CONFIDENCE_RANK[a] <= CONFIDENCE_RANK[b] else b


def _round(n: float) -> int:
    return int(round(n))


class CategoryEstimate:
    def __init__(self, minimum: int, maximum: int, labor_min: int, labor_max: int,
                 confidence: str, likely: str, note: Optional[str] = None):
        self.minimum = minimum
        self.maximum = maximum
        self.labor_min = labor_min
        self.labor_max = labor_max
        self.confidence = confidence
        self.likely = likely
        self.note = note


def estimate_category(repair_id: str, tier: str, answers: Optional[Dict[str, str]]) -> CategoryEstimate:
    """
    Mirrors the JS `estimateCategory(categoryKey, tier, answers)` function.
    Returns a CategoryEstimate for a single repair category.
    """
    a = answers or {}
    base_min, base_max = pricing_service.base_range_for(repair_id, tier)
    labor_share = pricing_service.get_labor_share()

    minimum, maximum = base_min, base_max
    confidence = "moderate"
    likely = ""
    note = None

    def widen(pct: float):
        nonlocal minimum, maximum
        minimum = _round(minimum * (1 - pct))
        maximum = _round(maximum * (1 + pct))

    if repair_id == "screen":
        likely = "Display assembly / glass replacement"
        damage_type = a.get("damage_type")
        display_working = a.get("display_working")
        touch_working = a.get("touch_working")

        if damage_type == "glass_only" and display_working == "yes" and touch_working == "yes":
            confidence = "high"
            maximum = _round(maximum * 0.75)
            likely = "Outer glass replacement"
        elif damage_type == "display_damaged" or touch_working == "no" or display_working == "no":
            confidence = "high"
            minimum = _round(minimum * 1.1)
            likely = "Full display assembly replacement"
        else:
            confidence = "low"
            widen(0.25)
            note = "Confidence is lower because the exact extent of display damage can't be confirmed remotely."

        if damage_type == "not_sure" or touch_working == "not_sure" or display_working == "not_sure":
            confidence = "low"
            widen(0.2)
            note = note or "Confidence is lower because some answers were marked \u201cnot sure.\u201d"

    elif repair_id == "battery":
        likely = "Battery replacement"
        swollen = a.get("swollen")
        shuts_down = a.get("shuts_down")
        phone_age = a.get("phone_age")

        if swollen == "yes":
            confidence = "high"
            minimum = _round(minimum * 1.05)
            note = "A swollen battery should be treated as urgent \u2014 stop charging it and get it inspected soon."
        elif shuts_down == "yes" or phone_age in ("gt3", "2to3"):
            confidence = "high"
        else:
            confidence = "moderate"

        if phone_age == "not_sure" or swollen == "not_sure":
            confidence = "moderate"
            widen(0.1)

    elif repair_id == "charging":
        likely = "Charging port cleaning or replacement"
        port_debris = a.get("port_debris")
        charges_at_all = a.get("charges_at_all")
        cable_tested = a.get("cable_tested")

        if port_debris == "yes":
            confidence = "high"
            maximum = _round(maximum * 0.7)
            likely = "Charging port cleaning"
            note = "If it's just debris, a cleaning may resolve it for near the lower end of this range."
        elif charges_at_all == "no" and cable_tested == "yes_same":
            confidence = "high"
            likely = "Charging port replacement"
        else:
            confidence = "moderate"
            widen(0.15)

    elif repair_id == "camera":
        which_camera = a.get("which_camera")
        symptom = a.get("symptom")
        depth = a.get("depth")
        camera_word = "Front and rear camera work" if which_camera == "both" else \
            f"{'Front' if which_camera == 'front' else 'Rear'} camera replacement"
        likely = camera_word

        if symptom == "glass_cracked" and depth == "glass_only":
            confidence = "high"
            maximum = _round(maximum * 0.6)
            likely = "Camera lens glass replacement"
        elif symptom == "not_working" or depth == "deeper":
            confidence = "moderate"
        else:
            confidence = "low"
            widen(0.2)

        if which_camera == "both":
            minimum = _round(minimum * 1.6)
            maximum = _round(maximum * 1.6)

    elif repair_id == "audio":
        which_part = a.get("which_part")
        symptom = a.get("symptom")
        likely = "Speaker replacement" if which_part == "speaker" else \
            "Microphone replacement" if which_part == "mic" else "Earpiece replacement"
        confidence = "high" if symptom == "silent" else "moderate"

    elif repair_id == "buttons":
        which_button = a.get("which_button")
        symptom = a.get("symptom")
        button_word = "Power" if which_button == "power" else "Volume" if which_button == "volume" else "Button"
        likely = f"{button_word} assembly replacement"
        confidence = "high" if symptom == "stuck" else "moderate"

    elif repair_id == "water":
        likely = "Diagnostic cleaning, corrosion treatment, and component-level repair as needed"
        confidence = "low"
        widen(0.3)
        submerged = a.get("submerged")
        turns_on = a.get("turns_on")

        if turns_on == "no":
            maximum = _round(maximum * 1.3)

        if submerged == "submerged" and turns_on == "no":
            confidence = "low"
            note = ("Liquid damage can only be accurately priced after the phone is opened and "
                    "inspected \u2014 this range assumes anything from cleaning to component-level repair.")
        elif turns_on == "yes_normal":
            minimum = _round(minimum * 0.6)
            maximum = _round(maximum * 0.6)
            note = ("The phone is currently functioning, so a full inspection and preventative "
                    "cleaning is often enough \u2014 but corrosion can still surface later.")
        else:
            note = "Confidence is low because water damage often can't be fully assessed without opening the device."

    elif repair_id == "body":
        which_part = a.get("which_part")
        severity = a.get("severity")
        part_word = "Multiple panel replacement" if which_part == "multiple" else \
            f"{'Back glass' if which_part == 'back_glass' else 'Frame' if which_part == 'frame' else 'Camera housing'} replacement"
        likely = part_word
        confidence = "high" if severity == "cosmetic" else "moderate" if severity == "functional" else "low"

        if which_part == "multiple":
            minimum = _round(minimum * 1.4)
            maximum = _round(maximum * 1.5)
        if confidence == "low":
            widen(0.2)

    elif repair_id == "software":
        likely = "Software diagnosis and reset/reflash"
        confidence = "moderate"
        note = ("Many software issues can be resolved with a reset or reflash rather than a paid "
                "part replacement \u2014 this range covers diagnostic and software service time.")

    else:
        raise KeyError(f"Unknown repair_id '{repair_id}'")

    labor_min = _round(minimum * labor_share)
    labor_max = _round(maximum * labor_share)

    return CategoryEstimate(
        minimum=minimum, maximum=maximum,
        labor_min=labor_min, labor_max=labor_max,
        confidence=confidence, likely=likely, note=note,
    )


class CombinedEstimate:
    def __init__(self, parts_min: int, parts_max: int, labor_min: int, labor_max: int,
                 total_min: int, total_max: int, confidence: str):
        self.parts_min = parts_min
        self.parts_max = parts_max
        self.labor_min = labor_min
        self.labor_max = labor_max
        self.total_min = total_min
        self.total_max = total_max
        self.confidence = confidence


def combine_estimates(per_category: Dict[str, CategoryEstimate]) -> CombinedEstimate:
    """
    Mirrors the JS `combineEstimates(perCategory)` function: sums parts
    costs, but combines labor with an overlap discount (the technician is
    already inside the phone) rather than naively summing every repair's
    labor cost.
    """
    parts_min = 0.0
    parts_max = 0.0
    overall_confidence = "high"
    labor_values: List[Tuple[int, int]] = []

    for est in per_category.values():
        parts_min += (est.minimum - est.labor_min)
        parts_max += (est.maximum - est.labor_max)
        labor_values.append((est.labor_min, est.labor_max))
        overall_confidence = _lower_confidence(overall_confidence, est.confidence)

    labor_values.sort(key=lambda lv: lv[0], reverse=True)
    labor_min = 0.0
    labor_max = 0.0
    for i, (lmin, lmax) in enumerate(labor_values):
        weight = 1.0 if i == 0 else 0.35
        labor_min += lmin * weight
        labor_max += lmax * weight

    labor_min = _round(labor_min)
    labor_max = _round(labor_max)
    parts_min = _round(parts_min)
    parts_max = _round(parts_max)

    return CombinedEstimate(
        parts_min=parts_min, parts_max=parts_max,
        labor_min=labor_min, labor_max=labor_max,
        total_min=parts_min + labor_min, total_max=parts_max + labor_max,
        confidence=overall_confidence,
    )


def repair_time_for(repair_ids: List[str]) -> str:
    if "water" in repair_ids:
        return "Same day \u2013 2 days (diagnosis dependent)"
    if "software" in repair_ids:
        return "30 min \u2013 2 hours"
    if len(repair_ids) > 1:
        return "2 \u2013 5 hours"
    return "1 \u2013 3 hours"


def apply_region_multiplier(value: float, region_id: str) -> int:
    region = pricing_service.get_region(region_id)
    return _round(value * region["multiplier"])
