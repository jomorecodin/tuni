"""Analysis endpoints for gap detection and telemetry."""

from fastapi import APIRouter, Query

from app.bot.services.analysis_engine import (
    generate_weekly_report,
    get_subject_gap_detail,
    get_students_overview,
)
from app.bot.services.cronograma_service import _cronogramas, load_all_cronogramas, _loaded

router = APIRouter()


@router.get("/weekly-report")
async def weekly_report(weeks: int = Query(1, ge=1, le=12)):
    """Generate a weekly gap analysis report."""
    return generate_weekly_report(weeks_back=weeks)


@router.get("/gaps/{materia}")
async def subject_gaps(materia: str):
    """Deep-dive gap analysis for a specific subject."""
    return get_subject_gap_detail(materia)


@router.get("/students")
async def students_overview():
    """Summary of all registered students."""
    return get_students_overview()


@router.get("/subjects")
async def list_subjects():
    """List all subjects with loaded cronogramas."""
    if not _loaded:
        load_all_cronogramas()
    return {
        "subjects": sorted(_cronogramas.keys()),
        "count": len(_cronogramas),
    }
