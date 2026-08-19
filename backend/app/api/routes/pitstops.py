"""
Pitstop search endpoint.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.core.errors import PitstopAPIError
from app.schemas.pitstops import Pitstop, PitstopSearchRequest
from app.services.places.service import PlacesService

router = APIRouter(prefix="/api/pitstops", tags=["Pitstops"])


@router.post("/search", response_model=dict)
async def search_pitstops(request: PitstopSearchRequest):
    """
    Search for pitstops near a location.
    Uses Overpass API.
    Returns demo data if the API request fails.
    """
    service = PlacesService()
    try:
        pitstops = await service.search_nearby(
            request.latitude,
            request.longitude,
            request.categories,
            request.radius_meters,
        )
        return {
            "places_source": "overpass",
            "pitstops": [p.model_dump() for p in pitstops],
        }
    except PitstopAPIError as e:
        # Return demo pitstops on error
        demo_pitstops = [
            Pitstop(
                place_id="demo_cafe_001",
                name="Saravana Bhavan (T. Nagar)",
                category=request.categories[0] if request.categories else "cafe",
                latitude=request.latitude + 0.002,
                longitude=request.longitude + 0.001,
                rating=4.2,
                accessibility_info=None,
                source="demo",
            ),
            Pitstop(
                place_id="demo_pharmacy_001",
                name="Apollo Pharmacy",
                category="pharmacy",
                latitude=request.latitude - 0.001,
                longitude=request.longitude + 0.002,
                rating=4.0,
                accessibility_info=None,
                source="demo",
            ),
        ]
        return {
            "places_source": "demo",
            "description": f"Demo pitstop data (Overpass API failed: {e}).",
            "pitstops": [p.model_dump() for p in demo_pitstops],
        }
