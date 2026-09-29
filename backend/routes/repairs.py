from typing import List

from fastapi import APIRouter, HTTPException

from models.repair import Repair
from services import repair_service

router = APIRouter(prefix="/api", tags=["repairs"])


@router.get("/repairs", response_model=List[Repair])
def list_repairs():
    return repair_service.get_repairs()


@router.get("/repairs/{repair_id}", response_model=Repair)
def get_repair(repair_id: str):
    repair = repair_service.get_repair(repair_id)
    if repair is None:
        raise HTTPException(status_code=404, detail="We can't reliably estimate this repair remotely. A physical inspection may be required.")
    return repair
