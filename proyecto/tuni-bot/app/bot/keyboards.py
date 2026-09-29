"""Telegram keyboard builders."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def build_consent_keyboard() -> InlineKeyboardMarkup:
    """Build the consent acceptance/decline keyboard."""
    from app.bot.constants import STRINGS
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(STRINGS["consent_accept"], callback_data="consent_yes")],
        [InlineKeyboardButton(STRINGS["consent_decline"], callback_data="consent_no")],
    ])


def build_checkin_keyboard() -> InlineKeyboardMarkup:
    """Build the class check-in attendance keyboard."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Si, fui", callback_data="checkin_yes"),
            InlineKeyboardButton("No fui", callback_data="checkin_no"),
        ],
    ])


def build_reflection_keyboard() -> InlineKeyboardMarkup:
    """Build the self-assessment scale keyboard (1-5)."""
    buttons = [
        InlineKeyboardButton(str(i), callback_data=f"reflect_score_{i}")
        for i in range(1, 6)
    ]
    return InlineKeyboardMarkup([buttons])
