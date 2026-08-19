"""
Challenge parsing endpoint.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.schemas.challenges import ChallengeRequest, ChallengeResponse
from app.services.llm.service import ChallengeParserService, create_llm_provider

router = APIRouter(prefix="/api/challenges", tags=["Challenges"])


@router.post("/parse", response_model=ChallengeResponse)
async def parse_challenge(request: ChallengeRequest):
    """
    Parse a natural-language challenge into structured routing constraints.

    The LLM extracts constraints from the user's description.
    Falls back to a deterministic keyword parser if the LLM is unavailable.
    """
    provider = create_llm_provider()
    parser = ChallengeParserService(provider)
    constraints, source = await parser.parse(request.challenge_text)

    return ChallengeResponse(
        raw_text=request.challenge_text,
        parsed_constraints=constraints,
        parser_source=source,
    )
