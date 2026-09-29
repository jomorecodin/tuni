"""Slash command handlers: /ayuda, /estado, /horario, /profesor."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.constants import State, STRINGS
from app.bot.services.student_tracker import load_student

logger = logging.getLogger(__name__)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ayuda — show available commands."""
    await update.message.reply_text(STRINGS["help"], parse_mode="Markdown")


async def estado_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /estado — show student progress summary."""
    telegram_id = context.user_data.get("telegram_id")
    if not telegram_id:
        await update.message.reply_text("Usa /start primero.")
        return

    data = load_student(telegram_id)
    if not data:
        await update.message.reply_text("No hay datos de progreso aun.")
        return

    patterns = data["patterns"]
    subjects = ", ".join(data["subjects_used"]) if data["subjects_used"] else "Ninguna"

    await update.message.reply_text(
        STRINGS["status"].format(
            total_sessions=patterns["total_sessions"],
            total_interactions=patterns["total_interactions"],
            subjects_used=subjects,
            avg_depth=round(patterns["avg_session_depth"], 1),
        ),
        parse_mode="Markdown",
    )


async def horario_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /horario — prompt schedule upload."""
    await update.message.reply_text(STRINGS["schedule_prompt"])
    return State.UPLOAD_SCHEDULE


async def profesor_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /profesor — enter professor authentication flow."""
    await update.message.reply_text(STRINGS["professor_prompt"])
    return State.PROFESSOR_AUTH
