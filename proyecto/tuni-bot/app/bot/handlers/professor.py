"""Professor authentication and session handler.

Flow: /profesor → password prompt → validate → professor CHATTING session.
Professor chat uses Gemini (not qwen) to keep local model free for students.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.constants import State, STRINGS
from app.bot.services.session_manager import UserSession, create_session, close_session
from app.bot.services.user_manager import get_or_create_user
from app.core.config import settings

logger = logging.getLogger(__name__)


async def professor_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle password input for professor authentication."""
    password = update.message.text.strip()

    if password != settings.professor_password:
        await update.message.reply_text(STRINGS["professor_auth_fail"])
        return State.PROFESSOR_AUTH

    # Auth successful — set up professor session
    telegram_id = update.effective_user.id
    context.user_data["telegram_id"] = telegram_id

    # Ensure user exists in Supabase
    try:
        user_id = get_or_create_user(telegram_id)
        context.user_data["user_id"] = user_id
    except Exception as e:
        logger.error("Failed to register professor user %d: %s", telegram_id, e)
        await update.message.reply_text(STRINGS["error"])
        return State.CHATTING

    # Close any existing session
    old_session = context.user_data.get("session")
    if old_session:
        close_session(old_session.session_id, old_session, telegram_id)

    # Create professor session
    try:
        session_id = create_session(user_id, role="professor")
    except Exception as e:
        logger.error("Failed to create professor session: %s", e)
        await update.message.reply_text(STRINGS["error"])
        return State.CHATTING

    session = UserSession(
        user_id=user_id,
        session_id=session_id,
        role="professor",
    )
    context.user_data["session"] = session
    context.user_data["is_professor"] = True

    await update.message.reply_text(STRINGS["professor_auth_success"])
    return State.CHATTING
