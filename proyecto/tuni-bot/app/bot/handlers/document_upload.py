"""Document/photo upload handler for CHATTING state.

Processes uploads mid-conversation using Gemini multimodal.
Also handles /horario schedule uploads from the CHATTING state.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.constants import State, STRINGS
from app.bot.services.session_manager import UserSession
from app.bot.services.student_tracker import update_student
from app.services.gemini_vision import analyze_document, extract_cronograma
from app.db.client import get_supabase

logger = logging.getLogger(__name__)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle photo/document upload during CHATTING state."""
    session: UserSession | None = context.user_data.get("session")
    telegram_id = context.user_data.get("telegram_id")

    if not session:
        await update.message.reply_text("Usa /start primero.")
        return State.CHATTING

    session.touch()

    # Download file
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        mime_type = "image/jpeg"
    elif update.message.document:
        file = await update.message.document.get_file()
        doc = update.message.document
        mime_type = doc.mime_type or "application/octet-stream"
    else:
        return State.CHATTING

    file_bytes = await file.download_as_bytearray()

    # Notify user we're processing
    thinking_msg = await update.message.reply_text("Analizando documento...")

    # Build conversation context for Gemini
    recent_messages = session.history[-4:] if session.history else []
    context_text = "\n".join(
        f"{m['role']}: {m['content'][:200]}" for m in recent_messages
    )

    try:
        analysis = await analyze_document(bytes(file_bytes), mime_type, context_text)
        await thinking_msg.edit_text(analysis)

        # Add to conversation history
        session.history.append({"role": "user", "content": "[Documento/imagen enviado]"})
        session.history.append({"role": "assistant", "content": analysis})
        session.message_count += 1

    except Exception as e:
        logger.error("Document analysis failed: %s", e)
        await thinking_msg.edit_text(
            "No pude analizar el documento. Intenta describirme el problema en texto."
        )

    # Log upload event in Supabase
    try:
        get_supabase().table("evento_interaccion").insert({
            "id_sesion": session.session_id,
            "tipo_evento": "document_upload",
            "metadata_json": {
                "mime_type": mime_type,
                "file_size": len(file_bytes),
                "role": session.role,
            },
        }).execute()
    except Exception as e:
        logger.error("Failed to record upload event: %s", e)

    return State.CHATTING


async def handle_schedule_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle cronograma upload from UPLOAD_SCHEDULE state (re-upload via /horario)."""
    telegram_id = context.user_data.get("telegram_id")

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

    await update.message.reply_text(STRINGS["schedule_received"])

    # Process with Gemini
    file_bytes = await file.download_as_bytearray()
    cronograma = await extract_cronograma(bytes(file_bytes), mime_type)

    if cronograma and cronograma.get("materias"):
        subjects = [m["nombre"] for m in cronograma["materias"] if m.get("nombre")]
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
        update_student(telegram_id, {
            "schedule": {"raw_text": f"file:{file_path}", "parsed": False},
        })
        await update.message.reply_text(STRINGS["schedule_process_error"])

    return State.CHATTING
