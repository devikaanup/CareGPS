"""
Coordinate schema with geographic validation.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class Coordinate(BaseModel):
    """A geographic coordinate with validation."""

    latitude: float = Field(..., description="Latitude in degrees", examples=[13.0827])
    longitude: float = Field(..., description="Longitude in degrees", examples=[80.2707])

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        if not -90 <= v <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {v}")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        if not -180 <= v <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {v}")
        return v
