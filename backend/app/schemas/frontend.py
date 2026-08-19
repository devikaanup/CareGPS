"""
Frontend-specific request and response schemas.
"""
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class FrontendOptions(BaseModel):
    avoidHighways: bool = False
    avoidUnpaved: bool = False
    avoidPoorlyLit: bool = False
    avoidComplexRoundabouts: bool = False
    wheelchairAccessible: bool = False
    manyPitStops: bool = False
    womenSafety: bool = False
    scenicRoute: bool = False

class FrontendRequest(BaseModel):
    challenge: str = Field(default="")
    origin: str = Field(..., description="Origin address or place name")
    destination: str = Field(..., description="Destination address or place name")
    options: FrontendOptions = Field(default_factory=FrontendOptions)

class FrontendPitstop(BaseModel):
    id: str
    name: str
    type: Literal["rest", "coffee", "restroom", "accessible"]
    distance: str
    note: str

class FrontendBadge(BaseModel):
    text: str
    tone: Literal["leaf", "sky", "sun"]

class FrontendRouteOption(BaseModel):
    id: str
    label: str
    emoji: str
    duration: str
    distance: str
    why: List[str]
    pitstops: List[FrontendPitstop]
    badge: FrontendBadge
    polyline: str = ""
