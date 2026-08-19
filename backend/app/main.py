"""
RouteEase FastAPI application.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.challenges import router as challenges_router
from app.api.routes.hazards import router as hazards_router
from app.api.routes.health import router as health_router
from app.api.routes.pitstops import router as pitstops_router
from app.api.routes.routing import router as routing_router
from app.api.routes.frontend import router as frontend_router
from app.core.config import get_settings
from app.core.errors import (
    ErrorCode,
    RouteEaseError,
    error_response,
    routeease_exception_handler,
)
from app.core.logging import get_logger, setup_logging
from app.services.routing.demo import generate_demo_response

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    settings = get_settings()
    setup_logging(settings.debug)
    logger.info("RouteEase backend starting")

    logger.info("LLM provider: %s", settings.llm_provider)
    yield
    logger.info("RouteEase backend shutting down")


app = FastAPI(
    title="RouteEase API",
    description=(
        "Routes built around you, not just the fastest route. "
        "Navigation for people with disabilities, elderly users, and new drivers."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ──
app.add_exception_handler(RouteEaseError, routeease_exception_handler)  # type: ignore[arg-type]


@app.exception_handler(422)
async def validation_exception_handler(_request: Request, exc):
    """Convert FastAPI validation errors to our error format."""
    return error_response(
        ErrorCode.VALIDATION_ERROR,
        str(exc),
        422,
    )


# ── Routes ──
app.include_router(health_router)
app.include_router(challenges_router)
app.include_router(routing_router)
app.include_router(hazards_router)
app.include_router(pitstops_router)
app.include_router(frontend_router)


# ── Demo endpoint ──
@app.get("/api/demo", tags=["Demo"])
async def demo_endpoint():
    """
    Returns a complete demo response without requiring any external services.
    All data is clearly labelled as demo. This endpoint is for frontend
    development and demonstration purposes.
    """
    response = generate_demo_response()
    return response.model_dump()
