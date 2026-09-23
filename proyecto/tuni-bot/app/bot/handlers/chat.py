"""Main chat handler — receives messages, streams LLM response, buffers telemetry.

Telemetry architecture: interactions are buffered in memory on the UserSession
object during active conversations. No disk I/O happens per message. The buffer
is flushed to the student JSON + conversation log only when the session closes
(30-min timeout, /materia, /nueva). Supabase inserts still happen per message
since they're non-blocking network calls that run after the response is delivered.
"""

import io
import logging
import time

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.constants import State, STRINGS
from app.bot.keyboards import build_subject_keyboard, get_all_subjects
from app.bot.services.intent_detector import detect_subject_switch
from app.bot.services.latex_renderer import has_renderable_math, render_all_blocks, clean_text
from app.bot.services.session_manager import UserSession, close_session, create_session
from app.bot.services.student_tracker import record_session_start
from app.bot.services.streaming import stream_response_to_telegram
from app.services.llm_client import stream_chat
from app.db.client import get_supabase

logger = logging.getLogger(__name__)

# Patterns indicating self-correction
SELF_CORRECTION_PHRASES = [
    "espera", "me equivoque", "no, es", "corrijo", "en realidad",
    "perdon", "error mio", "me confundi", "no era", "quise decir",
]


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle a text message in CHATTING state."""
    session: UserSession | None = context.user_data.get("session")
    telegram_id = context.user_data.get("telegram_id")

    # Check session validity — flush telemetry if expired
    if session is None or session.is_expired():
        if session and session.is_expired():
            close_session(session.session_id, session, telegram_id)
            context.user_data.pop("session", None)
            await update.message.reply_text(STRINGS["session_timeout"])

        keyboard = build_subject_keyboard()
        await update.message.reply_text(
            STRINGS["select_subject"],
            reply_markup=keyboard,
        )
        return State.SELECTING_SUBJECT

    session.touch()
    user_message = update.message.text

    # Detect subject switch intent before sending to LLM
    switch_result = detect_subject_switch(
        user_message, session.materia_nombre, get_all_subjects()
    )
    if switch_result is not None:
        materia_id, materia_nombre = switch_result

        if materia_id == "__ambiguous__":
            # Trigger found but no specific subject — show keyboard
            keyboard = build_subject_keyboard()
            await update.message.reply_text(
                STRINGS["switch_ambiguous"], reply_markup=keyboard,
            )
            close_session(session.session_id, session, telegram_id)
            context.user_data.pop("session", None)
            return State.SELECTING_SUBJECT

        # Exact match — close old session, create new one
        close_session(session.session_id, session, telegram_id)
        try:
            new_session_id = create_session(session.user_id, materia_id)
        except Exception as e:
            logger.error("Failed to create session on switch: %s", e)
            await update.message.reply_text(STRINGS["error"])
            return State.CHATTING

        new_session = UserSession(
            user_id=session.user_id,
            session_id=new_session_id,
            materia_id=materia_id,
            materia_nombre=materia_nombre,
        )
        context.user_data["session"] = new_session
        if telegram_id:
            record_session_start(telegram_id, materia_nombre)

        await update.message.reply_text(
            STRINGS["subject_switched"].format(subject=materia_nombre),
            parse_mode="Markdown",
        )
        return State.CHATTING

    # Detect self-correction (checked later when buffering)
    lower_msg = user_message.lower()
    is_self_correction = any(phrase in lower_msg for phrase in SELF_CORRECTION_PHRASES)

    # Build message history for LLM
    messages = list(session.history)
    messages.append({"role": "user", "content": user_message})

    # Send "thinking" placeholder
    thinking_msg = await update.message.reply_text(STRINGS["thinking"])

    # Stream LLM response with progressive editing
    try:
        carrera = context.user_data.get("career_name")
        trimestre = context.user_data.get("trimestre")
        is_general = session.materia_id == "__general__"
        mode = "general" if is_general else "tutor"
        token_gen = stream_chat(messages, mode, session.materia_nombre, carrera, trimestre)
        full_response, total_tokens, elapsed_ms = await stream_response_to_telegram(
            thinking_msg, token_gen
        )
    except Exception as e:
        logger.error("Chat error: %s", e)
        await thinking_msg.edit_text(STRINGS["error"])
        return State.CHATTING

    # Render LaTeX blocks as images and send after the text
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
    max_history = 40
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

    # Record interaction in Supabase (non-blocking network call, runs after response)
    try:
        get_supabase().table("interaccion").insert({
            "id_sesion": session.session_id,
            "modo_seleccionado": "tutor",
            "prompt_estudiante": user_message,
            "respuesta_modelo": full_response,
            "longitud_prompt_tokens": len(user_message.split()),
            "longitud_respuesta_tokens": total_tokens,
            "tiempo_generacion_ms": elapsed_ms,
        }).execute()
    except Exception as e:
        logger.error("Failed to record interaction: %s", e)

    # Record behavioral event in Supabase
    try:
        get_supabase().table("evento_interaccion").insert({
            "id_sesion": session.session_id,
            "tipo_evento": "message_sent",
            "metadata_json": {
                "prompt_length_chars": len(user_message),
                "response_length_chars": len(full_response),
                "generation_time_ms": elapsed_ms,
                "session_depth": session.depth,
            },
        }).execute()
    except Exception as e:
        logger.error("Failed to record event: %s", e)

    return State.CHATTING
