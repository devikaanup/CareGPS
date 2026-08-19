"""
Route planning and demo endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.schemas.challenges import RoutePlanRequest
from app.schemas.routes import RoutePlanResponse
from app.services.routing.pipeline import RoutePlanningPipeline

router = APIRouter(prefix="/api/routes", tags=["Routes"])


@router.post("/plan", response_model=RoutePlanResponse)
async def plan_route(request: RoutePlanRequest):
    """
    Full route planning pipeline.

    Steps:
    1. Parse challenge → structured constraints
    2. Fetch route candidates (OSRM Routing API or demo fallback)
    3. Analyze traffic
    4. Analyze hazards (proximity to route polyline)
    5. Search pitstops (Overpass API or demo fallback)
    6. Apply hard constraint filter
    7. Score routes (deterministic, explainable)
    8. Rank and recommend

    If OSRM is unavailable, returns a demo response
    that demonstrates the complete concept.
    """
    pipeline = RoutePlanningPipeline()
    return await pipeline.plan(request)
