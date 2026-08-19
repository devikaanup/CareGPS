"""
Challenge request and response schemas.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from .constraints import ConstraintProfile
from .coordinates import Coordinate


class ChallengeRequest(BaseModel):
    """Request body for the challenge parsing endpoint."""

    challenge_text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language description of the user's challenge",
        examples=["I'm a new driver and highways make me nervous."],
    )

    @field_validator("challenge_text")
    @classmethod
    def validate_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Challenge text must not be blank")
        return v.strip()


class ChallengeResponse(BaseModel):
    """Response from the challenge parsing endpoint."""

    raw_text: str = Field(..., description="Original challenge text")
    parsed_constraints: ConstraintProfile = Field(..., description="Extracted constraint profile")
    parser_source: str = Field(..., description="Which parser was used: ollama | fallback | openai | etc.")


class RoutePlanRequest(BaseModel):
    """Request body for the full route planning endpoint."""

    origin: Coordinate = Field(..., description="Starting point")
    destination: Coordinate = Field(..., description="Destination point")
    challenge_text: str = Field(
        default="",
        max_length=2000,
        description="Natural language challenge (optional; empty = default balanced routing)",
    )
