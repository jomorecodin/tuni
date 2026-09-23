"""Handlers for career and trimester selection."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.constants import State, STRINGS, CAREERS
from app.bot.keyboards import build_career_keyboard, build_trimester_keyboard, build_subject_keyboard
from app.bot.services.student_tracker import update_student

logger = logging.getLogger(__name__)


async def career_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle career selection button press."""
    query = update.callback_query
    await query.answer()

    # Parse callback data: "career_{id}"
    career_id = query.data.replace("career_", "")

    # Find career name
    career_name = None
    for c in CAREERS:
        if c["id"] == career_id:
            career_name = c["name"]
            break

    if not career_name:
        logger.error("Unknown career: %s", career_id)
        await query.edit_message_text(STRINGS["error"])
        return State.SELECTING_CAREER

    # Save to user_data
    context.user_data["career_id"] = career_id
    context.user_data["career_name"] = career_name

    # Save to student JSON
    telegram_id = context.user_data.get("telegram_id")
    if telegram_id:
        update_student(telegram_id, {"career": career_id, "career_name": career_name})

    # Show trimester selection
    keyboard = build_trimester_keyboard(career_id)
    await query.edit_message_text(
        STRINGS["select_trimester"],
        reply_markup=keyboard,
    )
    return State.SELECTING_TRIMESTER


async def back_to_career(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle back button from trimester → career selection."""
    query = update.callback_query
    await query.answer()
    keyboard = build_career_keyboard()
    await query.edit_message_text(STRINGS["select_career"], reply_markup=keyboard)
    return State.SELECTING_CAREER


async def back_to_trimester(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle back button from subject → trimester selection."""
    query = update.callback_query
    await query.answer()
    career_id = context.user_data.get("career_id", "ing_sistemas")
    keyboard = build_trimester_keyboard(career_id)
    await query.edit_message_text(STRINGS["select_trimester"], reply_markup=keyboard)
    return State.SELECTING_TRIMESTER


async def trimester_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle trimester selection button press."""
    query = update.callback_query
    await query.answer()

    raw = query.data.replace("trimester_", "")
    career_name = context.user_data.get("career_name")
    telegram_id = context.user_data.get("telegram_id")

    if raw == "mix":
        # Student has subjects across multiple trimesters — show all subjects
        context.user_data["trimestre"] = None
        if telegram_id:
            update_student(telegram_id, {"trimestre": "mix"})
        keyboard = build_subject_keyboard(carrera=career_name)
        await query.edit_message_text(
            STRINGS["select_subject"],
            reply_markup=keyboard,
        )
        return State.SELECTING_SUBJECT

    try:
        trimestre = int(raw)
    except ValueError:
        logger.error("Invalid trimester: %s", query.data)
        return State.SELECTING_TRIMESTER

    # Save to user_data
    context.user_data["trimestre"] = trimestre

    # Save to student JSON
    if telegram_id:
        update_student(telegram_id, {"trimestre": trimestre})

    # Show subjects filtered by career + trimester
    keyboard = build_subject_keyboard(carrera=career_name, trimestre=trimestre)
    await query.edit_message_text(
        STRINGS["select_subject"],
        reply_markup=keyboard,
    )
    return State.SELECTING_SUBJECT
