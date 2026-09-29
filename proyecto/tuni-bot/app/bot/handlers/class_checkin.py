"""Class check-in handlers: attendance, last topic, unclear points.

Triggered after subject selection (before CHATTING) to document what
the student covered in their most recent class. Data is saved to the
student JSON and Supabase for pedagogical analysis.
"""

import logging
from datetime import datetime, timezone, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from app.bot.constants import State, STRINGS
from app.bot.services.cronograma_service import get_next_evaluacion, days_until_eval
from app.bot.services.student_tracker import load_student, update_student
from app.db.client import get_supabase

logger = logging.getLogger(__name__)

CHECKIN_COOLDOWN_HOURS = 24
_NO_ISSUE_PHRASES = {"no", "nada", "todo bien", "nada en particular", "no, todo bien", "ninguno"}


def should_show_checkin(telegram_id: int, materia_nombre: str) -> bool:
    """Return True if the check-in should be shown for this subject."""
    if materia_nombre == "Consulta General":
        return False

    data = load_student(telegram_id)
    if data is None:
        return False

    checkins = data.get("class_checkins", [])
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=CHECKIN_COOLDOWN_HOURS)).isoformat()
    recent = [
        c for c in checkins
        if c.get("materia") == materia_nombre and c.get("timestamp", "") > cutoff
    ]
    return len(recent) == 0


async def start_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE, materia: str = "") -> int:
    """Begin the class check-in flow."""
    query = update.callback_query
    if not materia:
        materia = context.user_data.get("checkin_materia", "la materia")

    context.user_data["checkin_data"] = {
        "materia": materia,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    days = days_until_eval(materia)
    if days is not None and days <= 7:
        nxt = get_next_evaluacion(materia)
        opener = STRINGS["checkin_attendance_eval"].format(
            materia=materia,
            eval_name=nxt.nombre,
            days=days,
            plural="s" if days != 1 else "",
        )
    else:
        opener = STRINGS["checkin_attendance_normal"].format(materia=materia)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Si, fui", callback_data="checkin_yes"),
            InlineKeyboardButton("No pude ir", callback_data="checkin_no"),
        ],
        [InlineKeyboardButton("Saltar >>", callback_data="checkin_skip")],
    ])

    await query.edit_message_text(opener, reply_markup=keyboard)
    return State.CLASS_CHECKIN_ATTENDANCE


async def attendance_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle attendance response (yes/no/skip)."""
    query = update.callback_query
    await query.answer()

    choice = query.data

    if choice == "checkin_skip":
        return await _finish_checkin_skip(query, context)

    attended = choice == "checkin_yes"
    context.user_data["checkin_data"]["attended_class"] = attended

    if attended:
        prompt = STRINGS["checkin_topic_attended"]
    else:
        prompt = STRINGS["checkin_topic_missed"]

    await query.edit_message_text(prompt)
    return State.CLASS_CHECKIN_TOPIC


async def topic_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle free-text response about last topic covered."""
    text = update.message.text
    context.user_data["checkin_data"]["last_topic_covered"] = text

    await update.message.reply_text(STRINGS["checkin_unclear"])
    return State.CLASS_CHECKIN_UNCLEAR


async def unclear_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle free-text about unclear points, then transition to CHATTING."""
    text = update.message.text
    context.user_data["checkin_data"]["unclear_points"] = text

    return await _save_and_start_chatting(update, context)


async def _save_and_start_chatting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save check-in data and transition to CHATTING state."""
    telegram_id = context.user_data.get("telegram_id")
    session = context.user_data.get("session")
    checkin = context.user_data.get("checkin_data", {})

    materia = checkin.get("materia", "")
    days = days_until_eval(materia)
    if days is not None:
        nxt = get_next_evaluacion(materia)
        checkin["days_until_next_eval"] = days
        checkin["next_eval_type"] = nxt.tipo if nxt else None

    checkin["session_id"] = session.session_id if session else None

    # Save to student JSON
    if telegram_id:
        data = load_student(telegram_id)
        if data:
            if "class_checkins" not in data:
                data["class_checkins"] = []
            data["class_checkins"].append(checkin)
            data["class_checkins"] = data["class_checkins"][-50:]
            update_student(telegram_id, {"class_checkins": data["class_checkins"]})

    # Record in Supabase
    try:
        get_supabase().table("evento_interaccion").insert({
            "id_sesion": session.session_id if session else None,
            "tipo_evento": "class_checkin",
            "metadata_json": checkin,
        }).execute()
    except Exception as e:
        logger.error("Failed to record class check-in: %s", e)

    # If unclear points are meaningful, inject as context for the LLM
    unclear = checkin.get("unclear_points", "")
    topic = checkin.get("last_topic_covered", "")
    if unclear and unclear.lower().strip() not in _NO_ISSUE_PHRASES and session:
        session.history.append({
            "role": "user",
            "content": (
                f"[Contexto: El estudiante reporta que en su ultima clase vieron "
                f"'{topic}' y no le quedo claro: '{unclear}']"
            ),
        })
        session.history.append({
            "role": "assistant",
            "content": f"Entendido, empecemos por ahi entonces.",
        })
        await update.message.reply_text(
            STRINGS["checkin_transition_unclear"].format(topic=unclear),
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            "Listo! Escribe tu pregunta.",
        )

    context.user_data.pop("checkin_data", None)
    return State.CHATTING


async def _finish_checkin_skip(query, context) -> int:
    """Skip check-in, go directly to CHATTING."""
    context.user_data.pop("checkin_data", None)

    await query.edit_message_text(
        "Listo! Escribe tu pregunta.",
    )
    return State.CHATTING
