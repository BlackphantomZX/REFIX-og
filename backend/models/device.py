from typing import Optional

from pydantic import BaseModel, Field


class Device(BaseModel):
    id: str
    brand: str
    model: str
    tier: str = Field(description="Rough pricing tier: budget | mid | flagship")
    approx_value_inr: Optional[int] = Field(
        default=None,
        description="Approximate current second-hand market value in INR, used for the repair-vs-value comparison. Sample data only.",
    )
