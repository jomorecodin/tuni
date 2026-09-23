"""Handlers for /start command, consent flow, and schedule upload."""

import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.bot.constants import State, STRINGS
from app.bot.keyboards import build_consent_keyboard, build_career_keyboard
from app.bot.services.user_manager import get_or_create_user
from app.bot.services.student_tracker import create_student_file, update_student

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

    # Show disclaimer + ask for schedule upload
    await query.edit_message_text(
        STRINGS["onboarding_disclaimer"]
        + "\n\n"
        + STRINGS["schedule_prompt"]
    )
    return State.UPLOAD_SCHEDULE


async def schedule_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle schedule photo/document upload."""
    telegram_id = context.user_data["telegram_id"]

    # Store the file reference (photo or document)
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        file_type = "photo"
    elif update.message.document:
        file = await update.message.document.get_file()
        file_type = "document"
    else:
        await update.message.reply_text(
            "Envia una foto o PDF de tu horario, o escribe /saltar"
        )
        return State.UPLOAD_SCHEDULE

    # Download and store
    file_path = f"data/students/{telegram_id}_schedule.{file_type}"
    await file.download_to_drive(file_path)

    update_student(telegram_id, {
        "schedule": {"raw_text": f"file:{file_path}", "parsed": None}
    })

    await update.message.reply_text(STRINGS["schedule_received"])

    # Move to career selection
    keyboard = build_career_keyboard()
    await update.message.reply_text(
        STRINGS["select_career"],
        reply_markup=keyboard,
    )
    return State.SELECTING_CAREER


async def skip_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /saltar — skip schedule upload."""
    await update.message.reply_text(STRINGS["schedule_skipped"])

    # Move to career selection
    keyboard = build_career_keyboard()
    await update.message.reply_text(
        STRINGS["select_career"],
        reply_markup=keyboard,
    )
    return State.SELECTING_CAREER
