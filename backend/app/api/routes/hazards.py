"""
Hazard endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.schemas.hazards import Hazard
from app.services.hazards.service import HazardRepository

router = APIRouter(prefix="/api/hazards", tags=["Hazards"])


@router.get("", response_model=list[Hazard])
async def get_hazards():
    """
    Get all active hazards.
    Data source: seeded demonstration/community-report data (NOT live sensor data).
    """
    repo = HazardRepository()
    return repo.get_all(active_only=True)


@router.get("/demo", response_model=dict)
async def get_hazards_demo():
    """
    Get all hazards with source metadata.
    Clearly identifies this as demo data.
    """
    repo = HazardRepository()
    hazards = repo.get_all(active_only=False)
    return {
        "hazard_source": "demo",
        "description": "Seeded demonstration data for Chennai area. NOT live sensor data.",
        "count": len(hazards),
        "hazards": [h.model_dump() for h in hazards],
    }
