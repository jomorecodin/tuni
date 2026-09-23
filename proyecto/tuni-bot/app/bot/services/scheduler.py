"""APScheduler integration for proactive post-exam reflection notifications.

Architecture:
- Uses AsyncIOScheduler (compatible with python-telegram-bot v21's asyncio loop)
- Initialized via post_init hook after bot is fully built
- Pre-schedules reflection messages for each known evaluation date
- Also runs a daily fallback check at 10:00 AM VE time
"""

import hashlib
import logging
from datetime import datetime, date, time, timedelta, timezone
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.constants import STRINGS
from app.bot.services.cronograma_service import (
    get_all_recent_evals,
    Evaluacion,
    _cronogramas,
)
from app.bot.services.student_tracker import load_student, update_student
from app.bot.handlers.reflection import register_reflection

logger = logging.getLogger(__name__)

VE_TZ = timezone(timedelta(hours=-4))  # Venezuela UTC-4, no DST

scheduler = AsyncIOScheduler(timezone="America/Caracas")
_bot: Bot | None = None


def _make_hash(ev: Evaluacion) -> str:
    """Create short hash for callback_data (stays under 64 bytes)."""
    raw = f"{ev.materia}|{ev.tipo}|{ev.fecha.isoformat()}"
    return hashlib.md5(raw.encode()).hexdigest()[:8]


async def post_init(application) -> None:
    """Called by python-telegram-bot after the application is fully initialized."""
    init_scheduler(application.bot)


def init_scheduler(bot: Bot) -> None:
    """Start the scheduler with the bot instance."""
    global _bot
    _bot = bot

    # Daily fallback: check for recent exams at 10:00 AM VE
    scheduler.add_job(
        _daily_reflection_check,
        trigger=CronTrigger(hour=10, minute=0),
        id="daily_reflection_check",
        replace_existing=True,
    )

    # Pre-schedule for known future evaluation dates
    _schedule_known_evals()

    scheduler.start()
    logger.info("APScheduler started with %d jobs", len(scheduler.get_jobs()))


def _schedule_known_evals() -> None:
    """Pre-schedule reflection notifications for the morning after each exam."""
    today = date.today()

    for materia, evals in _cronogramas.items():
        for ev in evals:
            reflection_date = ev.fecha + timedelta(days=1)
            if reflection_date < today:
                continue

            run_time = datetime.combine(
                reflection_date,
                time(hour=10, minute=0),
                tzinfo=VE_TZ,
            )

            job_id = f"reflection_{_make_hash(ev)}"
            scheduler.add_job(
                _send_reflection_for_eval,
                trigger=DateTrigger(run_date=run_time),
                id=job_id,
                replace_existing=True,
                kwargs={"evaluacion": ev},
            )
            logger.info(
                "Scheduled reflection for %s %s on %s",
                ev.materia, ev.tipo, reflection_date,
            )


async def _daily_reflection_check() -> None:
    """Fallback: find exams from yesterday and trigger reflections."""
    recent = get_all_recent_evals(within_days=1)
    for ev in recent:
        await _send_reflection_for_eval(ev)


async def _send_reflection_for_eval(evaluacion: Evaluacion) -> None:
    """Send post-exam reflection to all students enrolled in this subject."""
    if _bot is None:
        logger.error("Bot not initialized for scheduler")
        return

    student_ids = _get_students_for_subject(evaluacion.materia)

    for telegram_id in student_ids:
        try:
            await _send_single_reflection(telegram_id, evaluacion)
        except Exception as e:
            logger.error(
                "Failed to send reflection to %d for %s: %s",
                telegram_id, evaluacion.materia, e,
            )


def _get_students_for_subject(materia: str) -> list[int]:
    """Find telegram_ids of students who have used this subject."""
    from app.core.config import settings
    student_dir = Path(settings.data_dir)
    result = []

    for path in student_dir.glob("*.json"):
        try:
            telegram_id = int(path.stem)
            data = load_student(telegram_id)
            if data and materia in data.get("subjects_used", []):
                result.append(telegram_id)
        except (ValueError, Exception):
            continue

    return result


async def _send_single_reflection(telegram_id: int, ev: Evaluacion) -> None:
    """Send the reflection prompt to a single student."""
    if _bot is None:
        return

    # Check for duplicate
    data = load_student(telegram_id)
    if data:
        existing = [
            r for r in data.get("patterns", {}).get("heartbeat_responses", [])
            if (r.get("eval_tipo") == ev.tipo
                and r.get("eval_fecha") == ev.fecha.isoformat()
                and r.get("materia") == ev.materia)
        ]
        if existing:
            logger.info("Already sent reflection for %s %s to %d", ev.materia, ev.tipo, telegram_id)
            return

    hash_id = _make_hash(ev)
    topics_str = ", ".join(ev.temas) if ev.temas else "los temas del examen"

    message_text = STRINGS["reflection_prompt"].format(
        eval_name=ev.nombre,
        materia=ev.materia,
        topics=topics_str,
    )

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            str(i),
            callback_data=f"reflect_score_{hash_id}_{i}",
        )
        for i in range(1, 6)
    ]])

    # Register metadata for the callback handler
    register_reflection(hash_id, {
        "materia": ev.materia,
        "eval_tipo": ev.tipo,
        "eval_fecha": ev.fecha.isoformat(),
        "topics_mentioned": ev.temas,
        "sent_at": datetime.now(timezone.utc).isoformat(),
    })

    await _bot.send_message(
        chat_id=telegram_id,
        text=message_text,
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
    logger.info("Sent reflection prompt to %d for %s %s", telegram_id, ev.materia, ev.tipo)

    # Record that we sent it (prevent duplicates)
    _record_reflection_sent(telegram_id, ev)


def _record_reflection_sent(telegram_id: int, ev: Evaluacion) -> None:
    """Mark that a reflection was sent, even before the student responds."""
    data = load_student(telegram_id)
    if data is None:
        return

    responses = data.get("patterns", {}).get("heartbeat_responses", [])
    responses.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "materia": ev.materia,
        "eval_tipo": ev.tipo,
        "eval_fecha": ev.fecha.isoformat(),
        "self_assessment": None,
        "perceived_gaps": None,
        "teaching_gaps": None,
        "topics_mentioned": ev.temas,
        "responded": False,
        "response_delay_hours": None,
        "sent_at": datetime.now(timezone.utc).isoformat(),
    })
    update_student(telegram_id, {"patterns": {"heartbeat_responses": responses}})
