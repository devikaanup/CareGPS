from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.frontend import (
    FrontendRequest, 
    FrontendRouteOption, 
    FrontendPitstop, 
    FrontendBadge
)
from app.schemas.challenges import RoutePlanRequest
from app.schemas.constraints import ConstraintProfile
from app.services.geocoding.service import GeocodingService, GeocodingAPIError
from app.services.routing.pipeline import RoutePlanningPipeline

router = APIRouter(prefix="/api/routes/frontend", tags=["Frontend"])

geocoder = GeocodingService()

def map_options_to_constraints(options) -> ConstraintProfile:
    constraints = ConstraintProfile()
    if options.avoidHighways:
        constraints.avoid_highways = True
    if options.avoidUnpaved:
        constraints.avoid_unpaved = True
    if options.avoidPoorlyLit:
        constraints.avoid_unlit_roads = True
    if options.avoidComplexRoundabouts:
        constraints.avoid_roundabouts = True
        constraints.avoid_complex_intersections = True
    if options.wheelchairAccessible:
        constraints.mobility_level = "wheelchair"
        constraints.needs_accessible_restrooms = True
    if options.manyPitStops:
        constraints.needs_rest_stops = True
    if options.womenSafety:
        constraints.priority = "safety"
        constraints.avoid_unlit_roads = True
    if options.scenicRoute:
        constraints.priority = "comfort"
    return constraints

def get_badge_and_emoji(route) -> tuple[FrontendBadge, str]:
    if route.recommended:
        return FrontendBadge(text="Recommended", tone="leaf"), "⭐ Best overall"
    if route.label == "Fastest":
        return FrontendBadge(text="Fastest", tone="sky"), "⚡ Quickest route"
    
    # Check what scored highest
    s = route.scores
    if s.comfort > s.time and s.comfort > 80:
        return FrontendBadge(text="Most restful", tone="sun"), "🍃 Scenic & slow"
    if s.safety > s.time and s.safety > 80:
        return FrontendBadge(text="Safest", tone="leaf"), "🛡️ Protected route"
    
    return FrontendBadge(text="Alternative", tone="sky"), "🛣️ Standard route"

@router.post("", response_model=List[FrontendRouteOption])
async def plan_frontend_route(request: FrontendRequest):
    try:
        origin_coord = await geocoder.geocode(request.origin)
        dest_coord = await geocoder.geocode(request.destination)
    except GeocodingAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))

    plan_req = RoutePlanRequest(
        origin=origin_coord,
        destination=dest_coord,
        challenge_text=request.challenge
    )

    base_constraints = map_options_to_constraints(request.options)
    pipeline = RoutePlanningPipeline()
    response = await pipeline.plan(plan_req, base_constraints=base_constraints)

    frontend_routes = []
    for r in response.routes:
        badge, emoji = get_badge_and_emoji(r)
        
        # Format duration
        mins = int(r.duration_seconds // 60)
        duration_str = f"{mins} min"
        
        # Format distance
        km = r.distance_meters / 1000.0
        distance_str = f"{km:.1f} km"
        
        # Combine advantages and warnings for "why"
        why_list = r.advantages.copy()
        if r.warnings:
            why_list.extend(r.warnings)
            
        # Ensure we always mention explicitly selected advanced options
        if request.options.avoidHighways and "Highway avoided" not in why_list:
            why_list.insert(0, "Highway avoided")
        if request.options.avoidUnpaved and "Unpaved roads avoided" not in why_list:
            why_list.insert(0, "Unpaved roads avoided")
        if request.options.avoidPoorlyLit and "Poorly lit areas avoided" not in why_list:
            why_list.insert(0, "Poorly lit areas avoided")
        if request.options.avoidComplexRoundabouts and "Complex intersections avoided" not in why_list:
            why_list.insert(0, "Complex intersections avoided")
        if request.options.scenicRoute and "Scenic route" not in why_list:
            why_list.insert(0, "Scenic route")
            
        # Ensure fastest route is clearly marked
        is_fastest = any(dur == min(c.duration_seconds for c in response.routes) for dur in [r.duration_seconds])
        if is_fastest and "Fastest route" not in why_list:
            why_list.insert(0, "Fastest route")
            
        # Remove the limit to top 3 reasons so all user preferences show
        why_list = why_list if why_list else ["Standard route"]

        # If it's the fastest, update the badge to clearly show it
        badge, emoji = get_badge_and_emoji(r)
        if len(response.routes) > 1 and is_fastest:
            if r.recommended:
                badge = FrontendBadge(text="Fastest & Recommended", tone="leaf")
                emoji = "⚡ Best overall"
            else:
                badge = FrontendBadge(text="Fastest", tone="sky")
                emoji = "⚡ Quickest route"

        # Map pitstops
        fpitstops = []
        for i, p in enumerate(r.pitstops):
            # map backend type to frontend type
            ptype = "rest"
            t = p.category.lower()
            if "cafe" in t or "coffee" in t:
                ptype = "coffee"
            elif "restroom" in t or "toilet" in t:
                ptype = "restroom"
            elif p.accessibility_info and "wheelchair" in str(p.accessibility_info).lower():
                ptype = "accessible"

            fpitstops.append(FrontendPitstop(
                id=f"p{i}",
                name=p.name,
                type=ptype,
                distance="Along route",
                note=str(p.accessibility_info) if p.accessibility_info else "Pitstop"
            ))

        frontend_routes.append(FrontendRouteOption(
            id=r.route_id,
            label=r.label if r.label else "Route",
            emoji=emoji,
            duration=duration_str,
            distance=distance_str,
            why=why_list,
            pitstops=fpitstops,
            badge=badge,
            polyline=r.polyline
        ))

    return frontend_routes
