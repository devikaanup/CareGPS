"""
Constraint profile schema.
Strict Pydantic model — no arbitrary fields allowed.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class MobilityLevel(str, Enum):
    """User mobility classification."""
    FULL = "full"
    MODERATE = "moderate"
    LIMITED = "limited"
    WHEELCHAIR = "wheelchair"


class DrivingExperience(str, Enum):
    """User driving experience level."""
    LEARNER = "learner"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERIENCED = "experienced"


class Priority(str, Enum):
    """Primary routing priority."""
    SAFETY = "safety"
    ACCESSIBILITY = "accessibility"
    COMFORT = "comfort"
    SPEED = "speed"
    BALANCED = "balanced"


class ConstraintProfile(BaseModel):
    """
    Structured constraint profile extracted from natural language.
    No arbitrary fields allowed (model_config forbids extras).
    """

    # --- Hard avoidance constraints ---
    avoid_highways: bool = Field(default=False, description="Avoid highway segments")
    avoid_tolls: bool = Field(default=False, description="Avoid toll roads")
    avoid_ferries: bool = Field(default=False, description="Avoid ferry crossings")
    avoid_unpaved: bool = Field(default=False, description="Avoid unpaved/dirt roads")
    avoid_potholes: bool = Field(default=False, description="Avoid known pothole areas")
    avoid_roadblocks: bool = Field(default=False, description="Avoid active roadblocks")
    avoid_complex_intersections: bool = Field(default=False, description="Avoid complex intersections")
    avoid_roundabouts: bool = Field(default=False, description="Avoid roundabouts")
    avoid_heavy_merges: bool = Field(default=False, description="Avoid heavy merge lanes")
    avoid_high_traffic: bool = Field(default=False, description="Prefer lower traffic routes")
    avoid_unlit_roads: bool = Field(default=False, description="Avoid poorly-lit roads")

    # --- Pitstop needs ---
    needs_rest_stops: bool = Field(default=False, description="Needs rest stop along route")
    needs_accessible_restrooms: bool = Field(default=False, description="Needs accessible restroom")
    needs_pharmacy: bool = Field(default=False, description="Needs pharmacy along route")
    needs_hospital: bool = Field(default=False, description="Needs hospital nearby")
    needs_fuel: bool = Field(default=False, description="Needs fuel station")
    needs_ev_charging: bool = Field(default=False, description="Needs EV charging station")

    # --- User profile ---
    mobility_level: MobilityLevel = Field(default=MobilityLevel.FULL, description="User mobility level")
    driving_experience: DrivingExperience = Field(
        default=DrivingExperience.EXPERIENCED, description="User driving experience"
    )
    vision_sensitivity: bool = Field(default=False, description="User has vision sensitivity")

    # --- Meta ---
    priority: Priority = Field(default=Priority.BALANCED, description="Primary routing priority")
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Parser confidence in constraint extraction (0-1)",
    )
    reasoning_summary: str = Field(
        default="",
        description="Brief explanation of why these constraints were chosen",
    )

    model_config = {"extra": "forbid"}
