"""Handlers for post-exam reflection flow.

Initiated by scheduler proactive messages. Runs in a separate
ConversationHandler (group=1) so it doesn't conflict with the
main conversation flow.
"""

import logging
from datetime import datetime, timezone

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.bot.constants import State, STRINGS
from app.bot.services.student_tracker import load_student, update_student
from app.db.client import get_supabase

logger = logging.getLogger(__name__)

# Module-level cache: maps hash → eval metadata (populated by scheduler)
_reflection_cache: dict[str, dict] = {}


def register_reflection(hash_id: str, metadata: dict) -> None:
    """Store reflection metadata for later lookup by callback handler."""
    _reflection_cache[hash_id] = metadata


async def reflection_self_assessment_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle the 1-5 score button from the reflection prompt."""
    query = update.callback_query
    await query.answer()

    # Parse "reflect_score_{hash}_{score}"
    parts = query.data.rsplit("_", 2)
    if len(parts) < 3:
        await query.edit_message_text("Error procesando respuesta.")
        return ConversationHandler.END

    hash_id = parts[-2]
    try:
        score = int(parts[-1])
    except ValueError:
        await query.edit_message_text("Error procesando respuesta.")
        return ConversationHandler.END

    telegram_id = update.effective_user.id

    # Look up reflection metadata
    meta = _reflection_cache.get(hash_id)
    if not meta:
        # Fallback: find most recent un-responded reflection in student JSON
        data = load_student(telegram_id)
        if data:
            responses = data.get("patterns", {}).get("heartbeat_responses", [])
            pending = [r for r in responses if not r.get("responded")]
            if pending:
                meta = pending[-1]

    if not meta:
        await query.edit_message_text("Gracias por tu respuesta!")
        return ConversationHandler.END

    # Store context for follow-up questions
    context.user_data["active_reflection"] = {
        "hash_id": hash_id,
        "materia": meta.get("materia", ""),
        "eval_tipo": meta.get("eval_tipo", ""),
        "eval_fecha": meta.get("eval_fecha", ""),
        "topics_mentioned": meta.get("topics_mentioned", []),
        "self_assessment": score,
        "sent_at": meta.get("sent_at"),
    }

    if score <= 3:
        prompt = STRINGS["reflection_followup_low"]
    else:
        prompt = STRINGS["reflection_followup_high"]

    await query.edit_message_text(f"Registrado: {score}/5.\n\n{prompt}")
    return State.REFLECTION_GAPS


async def reflection_gaps_response(
    update: Update, context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle free-text about perceived study gaps."""
    text = update.message.text
    reflection = context.user_data.get("active_reflection", {})
    reflection["perceived_gaps"] = text

    materia = reflection.get("materia", "la materia")
    topics = reflection.get("topics_mentioned", [])
    topics_hint = f" (por ejemplo: {', '.join(topics[:3])})" if topics else ""

    await update.message.reply_text(
        STRINGS["reflection_teaching"].format(
            materia=materia,
            topics_hint=topics_hint,
        )
    )
    return State.REFLECTION_TEACHING


async def reflection_teaching_response(
    update: Update, context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle teaching gaps response and finalize the reflection."""
    text = update.message.text
    telegram_id = context.user_data.get("telegram_id", update.effective_user.id)
    reflection = context.user_data.get("active_reflection", {})

    no_issues = text.lower().strip() in {"no", "nada", "no, todo bien", "ninguno"}
    teaching_text = None if no_issues else text
    reflection["teaching_gaps"] = teaching_text
    reflection["responded"] = True
    reflection["response_delay_hours"] = _calc_delay(reflection)

    # Save to student JSON: update the matching heartbeat_response entry
    data = load_student(telegram_id)
    if data:
        responses = data.get("patterns", {}).get("heartbeat_responses", [])
        # Find the matching pending entry
        for r in responses:
            if (not r.get("responded")
                    and r.get("materia") == reflection.get("materia")
                    and r.get("eval_tipo") == reflection.get("eval_tipo")):
                r["self_assessment"] = reflection.get("self_assessment")
                r["perceived_gaps"] = reflection.get("perceived_gaps")
                r["teaching_gaps"] = teaching_text
                r["responded"] = True
                r["response_delay_hours"] = reflection.get("response_delay_hours")
                break
        update_student(telegram_id, {"patterns": {"heartbeat_responses": responses}})

        # Also append to self_regulation.heartbeat_reflections
        hr = data.get("patterns", {}).get("self_regulation", {}).get("heartbeat_reflections", [])
        hr.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "materia": reflection.get("materia"),
            "type": "post_exam",
            "self_assessment": reflection.get("self_assessment"),
        })
        update_student(telegram_id, {
            "patterns": {"self_regulation": {"heartbeat_reflections": hr}},
        })

    # Save to Supabase
    try:
        get_supabase().table("reflexion_post_evaluacion").insert({
            "telegram_id": telegram_id,
            "materia": reflection.get("materia"),
            "eval_tipo": reflection.get("eval_tipo"),
            "eval_fecha": reflection.get("eval_fecha"),
            "self_assessment": reflection.get("self_assessment"),
            "perceived_gaps": reflection.get("perceived_gaps"),
            "teaching_gaps": teaching_text,
            "response_delay_hours": reflection.get("response_delay_hours"),
        }).execute()
    except Exception as e:
        logger.error("Failed to save reflection to Supabase: %s", e)

    # Clean up
    context.user_data.pop("active_reflection", None)

    await update.message.reply_text(STRINGS["reflection_thanks"])
    return ConversationHandler.END


def _calc_delay(reflection: dict) -> float | None:
    """Calculate hours between sending and responding."""
    sent = reflection.get("sent_at")
    if not sent:
        return None
    try:
        sent_dt = datetime.fromisoformat(sent)
        now = datetime.now(timezone.utc)
        return round((now - sent_dt).total_seconds() / 3600, 2)
    except Exception:
        return None
