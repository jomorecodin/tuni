"""Handler for subject selection via inline keyboard."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.constants import State, STRINGS
from app.bot.keyboards import get_subject_by_index
from app.bot.handlers.class_checkin import should_show_checkin, start_checkin
from app.bot.services.session_manager import UserSession, create_session
from app.bot.services.student_tracker import record_session_start

logger = logging.getLogger(__name__)


async def subject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle subject selection button press."""
    query = update.callback_query
    await query.answer()

    # Parse callback data: "subject_{index}"
    parts = query.data.split("_", 1)
    if len(parts) < 2:
        logger.error("Invalid subject callback data: %s", query.data)
        return State.SELECTING_SUBJECT

    subject = get_subject_by_index(parts[1])
    if subject is None:
        logger.error("Subject index not found: %s", parts[1])
        return State.SELECTING_SUBJECT

    materia_id, materia_nombre = subject
    is_general = materia_id == "__general__"

    user_id = context.user_data.get("user_id")
    telegram_id = context.user_data.get("telegram_id")

    if not user_id:
        await query.edit_message_text(STRINGS["error"])
        return State.SELECTING_SUBJECT

    # For general queries, use a placeholder materia_id
    session_materia_id = materia_id if not is_general else None

    # Create session in Supabase
    try:
        session_id = create_session(user_id, session_materia_id)
    except Exception as e:
        logger.error("Failed to create session: %s", e)
        await query.edit_message_text(STRINGS["error"])
        return State.SELECTING_SUBJECT

    # Set up in-memory session
    session = UserSession(
        user_id=user_id,
        session_id=session_id,
        materia_id=materia_id,
        materia_nombre=materia_nombre,
    )
    context.user_data["session"] = session

    # Track in student JSON
    if telegram_id:
        record_session_start(telegram_id, materia_nombre)

    # Route to class check-in if appropriate
    if not is_general and should_show_checkin(telegram_id, materia_nombre):
        return await start_checkin(update, context)

    if is_general:
        await query.edit_message_text(
            STRINGS["general_selected"],
            parse_mode="Markdown",
        )
    else:
        await query.edit_message_text(
            STRINGS["subject_selected"].format(subject=materia_nombre),
            parse_mode="Markdown",
        )
    return State.CHATTING
