"""
Hazard schemas.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class HazardType(str, Enum):
    """Types of road hazards."""
    POTHOLE = "pothole"
    ROADBLOCK = "roadblock"
    CONSTRUCTION = "construction"
    UNPAVED_SEGMENT = "unpaved_segment"
    FLOODED_ROAD = "flooded_road"
    DANGEROUS_INTERSECTION = "dangerous_intersection"


class HazardSeverity(str, Enum):
    """Hazard severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class HazardStatus(str, Enum):
    """Hazard reporting status."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    UNVERIFIED = "unverified"


class Hazard(BaseModel):
    """A reported road hazard."""

    id: str = Field(..., description="Hazard identifier", examples=["HZ-001"])
    type: HazardType = Field(..., description="Type of hazard")
    severity: HazardSeverity = Field(..., description="Severity level")
    latitude: float = Field(..., description="Hazard latitude")
    longitude: float = Field(..., description="Hazard longitude")
    radius_meters: float = Field(default=25.0, ge=0, description="Affected radius in meters")
    description: str = Field(default="", description="Human-readable description")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Report confidence")
    reported_at: str = Field(default="", description="ISO 8601 report timestamp")
    status: HazardStatus = Field(default=HazardStatus.ACTIVE, description="Current status")


class HazardOnRoute(BaseModel):
    """A hazard that affects a specific route."""

    hazard: Hazard = Field(..., description="The hazard details")
    distance_from_route_meters: float = Field(..., description="Distance from nearest route point")
    penalty: float = Field(default=0.0, ge=0.0, description="Scoring penalty applied")
