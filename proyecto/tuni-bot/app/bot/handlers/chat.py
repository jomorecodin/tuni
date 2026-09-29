"""Main chat handler — receives messages, streams LLM response, buffers telemetry.

Single agentic model: no mode selection, no subject switching. The LLM handles
all subjects based on the student's cronograma context.

Telemetry architecture: interactions are buffered in memory on the UserSession
object during active conversations. No disk I/O happens per message. The buffer
is flushed to the student JSON + conversation log only when the session closes.
Supabase inserts still happen per message (non-blocking network calls).
"""

import io
import logging
import time

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.constants import State, STRINGS
from app.bot.services.latex_renderer import has_renderable_math, render_all_blocks, clean_text
from app.bot.services.session_manager import UserSession, close_session, create_session
from app.bot.services.student_tracker import record_session_start, load_student
from app.bot.services.streaming import stream_response_to_telegram
from app.services.llm_client import stream_chat, stream_professor_chat
from app.db.client import get_supabase
from app.core.config import settings

logger = logging.getLogger(__name__)

# Patterns indicating self-correction
SELF_CORRECTION_PHRASES = [
    "espera", "me equivoque", "no, es", "corrijo", "en realidad",
    "perdon", "error mio", "me confundi", "no era", "quise decir",
]


def _get_student_context(telegram_id: int | None) -> tuple[list[str] | None, dict | None]:
    """Load student subjects and cronograma from their profile."""
    if not telegram_id:
        return None, None
    data = load_student(telegram_id)
    if not data:
        return None, None
    subjects = data.get("subjects_used", []) or None
    cronograma = data.get("cronograma") or None
    return subjects, cronograma


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle a text message in CHATTING state."""
    session: UserSession | None = context.user_data.get("session")
    telegram_id = context.user_data.get("telegram_id")

    # Check session validity — create new one if expired
    if session is None or session.is_expired():
        if session and session.is_expired():
            close_session(session.session_id, session, telegram_id)
            context.user_data.pop("session", None)
            await update.message.reply_text(STRINGS["session_timeout"])

        # Auto-create a new session
        user_id = context.user_data.get("user_id")
        if not user_id:
            await update.message.reply_text("Usa /start primero.")
            return State.CHATTING

        try:
            session_id = create_session(user_id)
        except Exception as e:
            logger.error("Failed to create session: %s", e)
            await update.message.reply_text(STRINGS["error"])
            return State.CHATTING

        session = UserSession(user_id=user_id, session_id=session_id)
        context.user_data["session"] = session
        if telegram_id:
            record_session_start(telegram_id, "general")

    session.touch()
    user_message = update.message.text

    # Detect self-correction
    lower_msg = user_message.lower()
    is_self_correction = any(phrase in lower_msg for phrase in SELF_CORRECTION_PHRASES)

    # Build message history for LLM
    messages = list(session.history)
    messages.append({"role": "user", "content": user_message})

    # Send "thinking" placeholder
    thinking_msg = await update.message.reply_text(STRINGS["thinking"])

    # Stream LLM response
    try:
        if session.role == "professor":
            # Professor uses Gemini — keeps qwen free for students
            from app.bot.services.analysis_engine import build_ai_context
            data_context = build_ai_context()
            token_gen = stream_professor_chat(messages, data_context)
        else:
            # Student uses Ollama (production) or Gemini (dev)
            student_subjects, cronograma = _get_student_context(telegram_id)
            token_gen = stream_chat(messages, student_subjects, cronograma)

        full_response, total_tokens, elapsed_ms = await stream_response_to_telegram(
            thinking_msg, token_gen
        )
    except Exception as e:
        logger.error("Chat error: %s", e)
        await thinking_msg.edit_text(STRINGS["error"])
        return State.CHATTING

    # Render LaTeX blocks as images
    if has_renderable_math(full_response):
        try:
            images = render_all_blocks(full_response)
            if images:
                cleaned = clean_text(full_response)
                if cleaned:
                    await thinking_msg.edit_text(cleaned)
                for img_bytes in images:
                    await update.message.reply_photo(
                        photo=io.BytesIO(img_bytes),
                    )
        except Exception as e:
            logger.warning("LaTeX rendering failed, keeping raw text: %s", e)

    # Update conversation history (keep last N messages)
    max_history = settings.bot_max_history_messages
    session.history.append({"role": "user", "content": user_message})
    session.history.append({"role": "assistant", "content": full_response})
    if len(session.history) > max_history:
        session.history = session.history[-max_history:]
    session.message_count += 1

    # Buffer interaction in memory — NO disk I/O
    session.buffer_interaction(
        prompt=user_message,
        response=full_response,
        total_tokens=total_tokens,
        elapsed_ms=elapsed_ms,
        self_correction=is_self_correction,
    )

    # Record interaction in Supabase
    try:
        get_supabase().table("interaccion").insert({
            "id_sesion": session.session_id,
            "modo_seleccionado": "agentic",
            "prompt_estudiante": user_message,
            "respuesta_modelo": full_response,
            "longitud_prompt_tokens": len(user_message.split()),
            "longitud_respuesta_tokens": total_tokens,
            "tiempo_generacion_ms": elapsed_ms,
        }).execute()
    except Exception as e:
        logger.error("Failed to record interaction: %s", e)

    # Record behavioral event
    try:
        get_supabase().table("evento_interaccion").insert({
            "id_sesion": session.session_id,
            "tipo_evento": "message_sent",
            "metadata_json": {
                "prompt_length_chars": len(user_message),
                "response_length_chars": len(full_response),
                "generation_time_ms": elapsed_ms,
                "session_depth": session.depth,
                "role": session.role,
            },
        }).execute()
    except Exception as e:
        logger.error("Failed to record event: %s", e)

    return State.CHATTING
