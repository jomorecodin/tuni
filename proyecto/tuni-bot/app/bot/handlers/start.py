"""Handlers for /start command, consent flow, and cronograma upload.

Onboarding flow:
  /start → consent → upload cronograma (PDF/photo) → Gemini processes → CHATTING
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.bot.constants import State, STRINGS
from app.bot.keyboards import build_consent_keyboard
from app.bot.services.user_manager import get_or_create_user
from app.bot.services.student_tracker import create_student_file, update_student
from app.bot.services.session_manager import UserSession, create_session
from app.services.gemini_vision import extract_cronograma

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /start — show welcome and consent prompt."""
    user = update.effective_user
    context.user_data["telegram_id"] = user.id

    keyboard = build_consent_keyboard()
    await update.message.reply_text(
        STRINGS["welcome"].format(name=user.first_name)
        + "\n\n"
        + STRINGS["consent_prompt"],
        reply_markup=keyboard,
    )
    return State.AWAITING_CONSENT


async def consent_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle consent button press."""
    query = update.callback_query
    await query.answer()

    if query.data == "consent_no":
        await query.edit_message_text(STRINGS["consent_declined"])
        return ConversationHandler.END

    # Consent accepted — register user
    telegram_id = context.user_data["telegram_id"]
    try:
        user_id = get_or_create_user(telegram_id)
        context.user_data["user_id"] = user_id
        create_student_file(telegram_id, user_id)
    except Exception as e:
        logger.error("Failed to register user %d: %s", telegram_id, e)
        await query.edit_message_text(STRINGS["error"])
        return ConversationHandler.END

    # Show disclaimer + ask for cronograma upload
    await query.edit_message_text(
        STRINGS["onboarding_disclaimer"]
        + "\n\n"
        + STRINGS["schedule_prompt"]
    )
    return State.UPLOAD_SCHEDULE


async def schedule_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle cronograma photo/document upload → Gemini extracts → CHATTING."""
    telegram_id = context.user_data["telegram_id"]
    user_id = context.user_data["user_id"]

    # Download the file
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        mime_type = "image/jpeg"
    elif update.message.document:
        file = await update.message.document.get_file()
        doc = update.message.document
        mime_type = doc.mime_type or "application/pdf"
    else:
        await update.message.reply_text(
            "Envia una foto o PDF de tu cronograma, o escribe /saltar"
        )
        return State.UPLOAD_SCHEDULE

    # Save raw file
    file_ext = "photo" if update.message.photo else "document"
    file_path = f"data/students/{telegram_id}_schedule.{file_ext}"
    await file.download_to_drive(file_path)

    # Notify user we're processing
    await update.message.reply_text(STRINGS["schedule_received"])

    # Download file bytes for Gemini
    file_bytes = await file.download_as_bytearray()

    # Process with Gemini multimodal
    cronograma = await extract_cronograma(bytes(file_bytes), mime_type)

    if cronograma and cronograma.get("materias"):
        # Extract subject names from cronograma
        subjects = [m["nombre"] for m in cronograma["materias"] if m.get("nombre")]

        # Save to student profile
        update_student(telegram_id, {
            "schedule": {"raw_text": f"file:{file_path}", "parsed": True},
            "cronograma": cronograma,
            "subjects_used": subjects,
        })

        subjects_text = "\n".join(f"  - {s}" for s in subjects)
        await update.message.reply_text(
            STRINGS["schedule_processed"].format(subjects=subjects_text),
        )
    else:
        # Gemini couldn't parse — save raw file reference anyway
        update_student(telegram_id, {
            "schedule": {"raw_text": f"file:{file_path}", "parsed": False},
        })
        await update.message.reply_text(STRINGS["schedule_process_error"])

    # Create session and go to CHATTING
    return await _start_chatting(update, context)


async def skip_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /saltar — skip cronograma upload."""
    await update.message.reply_text(STRINGS["schedule_skipped"])
    return await _start_chatting(update, context)


async def _start_chatting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Create a session and transition to CHATTING state."""
    user_id = context.user_data["user_id"]
    telegram_id = context.user_data["telegram_id"]

    try:
        session_id = create_session(user_id)
    except Exception as e:
        logger.error("Failed to create session: %s", e)
        await update.message.reply_text(STRINGS["error"])
        return State.CHATTING

    session = UserSession(user_id=user_id, session_id=session_id)
    context.user_data["session"] = session

    from app.bot.services.student_tracker import record_session_start
    record_session_start(telegram_id, "general")

    return State.CHATTING
