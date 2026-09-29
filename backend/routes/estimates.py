from fastapi import APIRouter, HTTPException

from models.estimate import Breakdown, EstimateRequest, EstimateResponse, RepairLineItem
from services import device_service, estimator, pricing as pricing_service, repair_service

router = APIRouter(prefix="/api", tags=["estimate"])


@router.post("/estimate", response_model=EstimateResponse)
def calculate_estimate(payload: EstimateRequest):
    device = device_service.get_device(payload.device_id)
    if device is None:
        raise HTTPException(
            status_code=404,
            detail="We don't have pricing information for this model yet.",
        )

    repair_names = {}
    for repair_id in payload.repair_ids:
        repair = repair_service.get_repair(repair_id)
        if repair is None:
            raise HTTPException(
                status_code=404,
                detail=f"We can't reliably estimate '{repair_id}' remotely. A physical inspection may be required.",
            )
        repair_names[repair_id] = repair.name

    try:
        per_category = {
            repair_id: estimator.estimate_category(
                repair_id, device.tier, payload.answers.get(repair_id, {})
            )
            for repair_id in payload.repair_ids
        }
    except KeyError as exc:
        # Missing pricing configuration for a repair/tier combination.
        raise HTTPException(
            status_code=422,
            detail="We need a little more information to calculate an estimate.",
        ) from exc

    combined = estimator.combine_estimates(per_category)

    total_min = estimator.apply_region_multiplier(combined.total_min, payload.region or "")
    total_max = estimator.apply_region_multiplier(combined.total_max, payload.region or "")
    parts_min = estimator.apply_region_multiplier(combined.parts_min, payload.region or "")
    parts_max = estimator.apply_region_multiplier(combined.parts_max, payload.region or "")
    labor_min = estimator.apply_region_multiplier(combined.labor_min, payload.region or "")
    labor_max = estimator.apply_region_multiplier(combined.labor_max, payload.region or "")

    repair_items = [
        RepairLineItem(
            repair_id=repair_id,
            name=repair_names[repair_id],
            likely_repair=est.likely,
            confidence=est.confidence,
            minimum=est.minimum,
            maximum=est.maximum,
            note=est.note,
        )
        for repair_id, est in per_category.items()
    ]

    device_value = payload.device_value_override
    if device_value is None:
        device_value = device.approx_value_inr

    repair_vs_value_pct = None
    if device_value:
        mid_estimate = (total_min + total_max) / 2
        repair_vs_value_pct = round((mid_estimate / device_value) * 100, 1)

    likely_repair_summary = repair_items[0].likely_repair
    if len(repair_items) > 1:
        likely_repair_summary += f" +{len(repair_items) - 1} more"

    return EstimateResponse(
        device_id=device.id,
        device=f"{device.brand} {device.model}",
        repairs=[repair_names[r] for r in payload.repair_ids],
        repair_items=repair_items,
        currency=pricing_service.get_currency(),
        minimum=total_min,
        maximum=total_max,
        repair_time=estimator.repair_time_for(payload.repair_ids),
        confidence=combined.confidence,
        likely_repair=likely_repair_summary,
        breakdown=Breakdown(
            parts_min=parts_min, parts_max=parts_max,
            labor_min=labor_min, labor_max=labor_max,
        ),
        region=payload.region or "",
        device_value_estimate=device_value,
        repair_vs_value_pct=repair_vs_value_pct,
        disclaimer=(
            "Estimate only. Repair prices vary by location, repair shop, replacement-part "
            "quality, warranty, and additional damage discovered during inspection. This tool "
            "provides an approximate estimate and is not a guaranteed quotation."
        ),
    )
