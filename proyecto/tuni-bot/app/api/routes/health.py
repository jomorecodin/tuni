"""Health and status endpoints."""

from fastapi import APIRouter

from app.bot.services.analysis_engine import get_pilot_health

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic API health check."""
    return {"status": "ok", "service": "tuni-supervisor-api"}


@router.get("/pilot-health")
async def pilot_health():
    """Comprehensive pilot health metrics for dashboard overview."""
    return get_pilot_health()
