from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class EstimateRequest(BaseModel):
    """
    Request body for POST /api/estimate.

    `repair_ids` supports selecting more than one problem at once (the
    original prototype allows multi-issue selection). If you only have a
    single repair, just pass a one-item list.

    `answers` is keyed by repair_id, then by question key, e.g.:

        {
          "device_id": "apple-iphone-13",
          "repair_ids": ["screen", "battery"],
          "answers": {
            "screen": {"display_working": "yes", "touch_working": "yes", "damage_type": "glass_only"},
            "battery": {"phone_age": "2to3", "shuts_down": "yes", "swollen": "no", "overheating": "no"}
          },
          "region": "delhi",
          "device_value_override": null
        }
    """

    device_id: str
    repair_ids: List[str] = Field(min_length=1)
    answers: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    region: Optional[str] = ""
    device_value_override: Optional[float] = None

    @field_validator("repair_ids")
    @classmethod
    def repair_ids_not_empty(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("At least one repair_id is required")
        return v


class RepairLineItem(BaseModel):
    repair_id: str
    name: str
    likely_repair: str
    confidence: str
    minimum: int
    maximum: int
    note: Optional[str] = None


class Breakdown(BaseModel):
    parts_min: int
    parts_max: int
    labor_min: int
    labor_max: int


class EstimateResponse(BaseModel):
    device_id: str
    device: str
    repairs: List[str]
    repair_items: List[RepairLineItem]
    currency: str = "INR"
    minimum: int
    maximum: int
    repair_time: str
    confidence: str
    likely_repair: str
    breakdown: Breakdown
    region: Optional[str] = ""
    device_value_estimate: Optional[float] = None
    repair_vs_value_pct: Optional[float] = None
    disclaimer: str
