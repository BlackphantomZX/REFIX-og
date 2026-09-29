from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from models.device import Device
from services import device_service

router = APIRouter(prefix="/api", tags=["devices"])


@router.get("/brands", response_model=List[str])
def list_brands():
    return device_service.get_brands()


@router.get("/devices", response_model=List[Device])
def list_devices(
    brand: Optional[str] = Query(default=None, description="Filter by brand name"),
    search: Optional[str] = Query(default=None, description="Search by model or brand name"),
):
    return device_service.get_devices(brand=brand, search=search)


@router.get("/devices/{device_id}", response_model=Device)
def get_device(device_id: str):
    device = device_service.get_device(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="We don't have pricing information for this model yet.")
    return device
