from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.constants import CAREERS, TRIMESTERS
from app.db.client import get_supabase


def build_consent_keyboard() -> InlineKeyboardMarkup:
    """Build the consent acceptance/decline keyboard."""
    from app.bot.constants import STRINGS
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(STRINGS["consent_accept"], callback_data="consent_yes")],
        [InlineKeyboardButton(STRINGS["consent_decline"], callback_data="consent_no")],
    ])


def build_career_keyboard() -> InlineKeyboardMarkup:
    """Build inline keyboard with available careers."""
    buttons = [
        [InlineKeyboardButton(c["name"], callback_data=f"career_{c['id']}")]
        for c in CAREERS
    ]
    return InlineKeyboardMarkup(buttons)


def build_trimester_keyboard(career_id: str) -> InlineKeyboardMarkup:
    """Build inline keyboard with trimesters available for a career."""
    trimesters = TRIMESTERS.get(career_id, [])
    roman = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
             7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"}
    buttons = [
        InlineKeyboardButton(
            f"Trimestre {roman.get(t, str(t))}",
            callback_data=f"trimester_{t}",
        )
        for t in trimesters
    ]
    rows = [buttons]
    rows.append([InlineKeyboardButton("Mezcla de varios", callback_data="trimester_mix")])
    rows.append([InlineKeyboardButton("<< Atras", callback_data="back_career")])
    return InlineKeyboardMarkup(rows)


# Module-level cache: maps short index → (id_materia, nombre)
_subject_cache: dict[str, tuple[str, str]] = {}


def build_subject_keyboard(carrera: str = None, trimestre: int = None) -> InlineKeyboardMarkup:
    """Fetch subjects from Supabase, optionally filtered by career+trimester.

    Uses short numeric indices in callback_data to stay under Telegram's
    64-byte limit.
    """
    global _subject_cache
    try:
        sb = get_supabase()
        query = sb.table("materia").select("id_materia, nombre, carrera, trimestre")
        if carrera:
            query = query.eq("carrera", carrera)
        if trimestre:
            query = query.eq("trimestre", trimestre)
        result = query.execute()
        subjects = result.data or []
    except Exception:
        subjects = []

    if not subjects:
        # Fallback — should not happen in production
        subjects = [
            {"id_materia": "1", "nombre": "Sin materias disponibles"},
        ]

    # Cache mapping and use short indices as callback_data
    _subject_cache.clear()
    buttons = []
    for i, s in enumerate(subjects):
        idx = str(i)
        _subject_cache[idx] = (str(s["id_materia"]), s["nombre"])
        buttons.append(
            InlineKeyboardButton(s["nombre"], callback_data=f"subject_{idx}")
        )

    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    rows.append([InlineKeyboardButton("Consulta General", callback_data="subject_general")])
    rows.append([InlineKeyboardButton("<< Atras", callback_data="back_trimester")])
    _subject_cache["general"] = ("__general__", "Consulta General")
    return InlineKeyboardMarkup(rows)


def get_subject_by_index(idx: str) -> tuple[str, str] | None:
    """Look up (id_materia, nombre) from a callback index."""
    return _subject_cache.get(idx)


def get_all_subjects() -> dict[str, tuple[str, str]]:
    """Return the cached subject map. Builds it if empty."""
    if not _subject_cache:
        build_subject_keyboard()
    return _subject_cache
