"""Progressive message editing for streaming LLM responses in Telegram."""

import asyncio
import logging

from telegram import Message
from telegram.error import BadRequest, TimedOut

from app.core.config import settings

logger = logging.getLogger(__name__)

MIN_CHARS_BEFORE_EDIT = 40


async def stream_response_to_telegram(
    message: Message,
    token_generator,
) -> tuple[str, int, int]:
    """
    Consume an async token generator and progressively edit a Telegram message.

    Returns (full_text, total_tokens, elapsed_ms).
    """
    buffer = ""
    last_edit_len = 0
    total_tokens = 0
    elapsed_ms = 0
    edit_interval = settings.bot_edit_interval_seconds

    async for chunk in token_generator:
        if chunk["done"]:
            total_tokens = chunk["total_tokens"]
            elapsed_ms = chunk["elapsed_ms"]
            break
        else:
            buffer += chunk["content"]
            total_tokens += 1

            # Debounced edit: only update if enough new content
            if len(buffer) - last_edit_len >= MIN_CHARS_BEFORE_EDIT:
                await _safe_edit(message, buffer + " ...")
                last_edit_len = len(buffer)
                await asyncio.sleep(edit_interval)

    # Final edit with complete text (no trailing "...")
    if buffer:
        await _safe_edit(message, buffer)

    return buffer, total_tokens, elapsed_ms


async def _safe_edit(message: Message, text: str) -> None:
    """Edit message text, silently handling common errors."""
    # Telegram message limit is 4096 chars
    if len(text) > 4000:
        text = text[:4000] + "\n\n_(respuesta truncada)_"
    try:
        await message.edit_text(text)
    except BadRequest as e:
        if "message is not modified" not in str(e).lower():
            logger.warning("Edit failed: %s", e)
    except TimedOut:
        pass
