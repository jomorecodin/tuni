"""Detect subject-switch intent from natural language messages."""

import unicodedata

# Trigger phrases that indicate the student wants to change subject
_SWITCH_TRIGGERS = [
    "ayuda con", "ayudame con", "cambiar a", "cambiemos a", "cambio a",
    "pasemos a", "pasamos a", "ahora con", "ahora necesito",
    "necesito ayuda con", "hablemos de", "pregunta de", "pregunta sobre",
    "sobre la materia", "quiero estudiar", "quiero repasar",
    "vamos con", "vamos a ver", "me ayudas con",
]

# Short aliases for each subject — maps alias → canonical subject name
_SUBJECT_ALIASES = {
    # Trimestre III
    "mate 2": "Matematicas II",
    "matematicas 2": "Matematicas II",
    "matematicas ii": "Matematicas II",
    "mate ii": "Matematicas II",
    "fisica": "Fisica I",
    "fisica 1": "Fisica I",
    "fisica i": "Fisica I",
    "algoritmos": "Algoritmos y Programacion",
    "programacion": "Algoritmos y Programacion",
    "algoritmos y programacion": "Algoritmos y Programacion",
    "progra": "Algoritmos y Programacion",
    "quimica": "Laboratorio de Quimica General",
    "lab quimica": "Laboratorio de Quimica General",
    "laboratorio de quimica": "Laboratorio de Quimica General",
    "emprendedoras": "Ideas emprendedoras",
    "ideas emprendedoras": "Ideas emprendedoras",
    "emprendimiento": "Ideas emprendedoras",
    # Trimestre IV
    "mate 3": "Matematicas III",
    "matematicas 3": "Matematicas III",
    "matematicas iii": "Matematicas III",
    "mate iii": "Matematicas III",
    "fisica 2": "Fisica II",
    "fisica ii": "Fisica II",
    "estructuras": "Estructuras de Datos",
    "estructuras de datos": "Estructuras de Datos",
    "edd": "Estructuras de Datos",
    "discretas": "Matematicas Discretas",
    "matematicas discretas": "Matematicas Discretas",
    "mate discreta": "Matematicas Discretas",
    "venezuela": "Venezuela, identidad y contexto",
    "identidad y contexto": "Venezuela, identidad y contexto",
    # Trimestre V
    "mate 4": "Matematicas IV",
    "matematicas 4": "Matematicas IV",
    "matematicas iv": "Matematicas IV",
    "mate iv": "Matematicas IV",
    "lab fisica": "Laboratorio de Fisica aplicada",
    "laboratorio de fisica": "Laboratorio de Fisica aplicada",
    "fisica aplicada": "Laboratorio de Fisica aplicada",
    "sistemas de informacion": "Sistemas de Informacion",
    "sistemas info": "Sistemas de Informacion",
    "informacion": "Sistemas de Informacion",
    "arquitectura": "Arquitectura del Computador",
    "arquitectura del computador": "Arquitectura del Computador",
    "arq computador": "Arquitectura del Computador",
    "algebra": "Algebra Lineal",
    "algebra lineal": "Algebra Lineal",
    "lineal": "Algebra Lineal",
}


def _normalize(text: str) -> str:
    """Lowercase and strip accents for matching."""
    text = text.lower().strip()
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def detect_subject_switch(
    message: str,
    current_subject: str,
    subjects: dict[str, tuple[str, str]],
) -> tuple[str, str] | None:
    """Detect if the user wants to switch subjects.

    Args:
        message: The raw user message.
        current_subject: The name of the currently active subject.
        subjects: Dict of index → (materia_id, nombre) from keyboard cache.

    Returns:
        (materia_id, materia_nombre) if switch detected, None otherwise.
    """
    normalized = _normalize(message)

    # Check if any trigger phrase is present
    has_trigger = any(trigger in normalized for trigger in _SWITCH_TRIGGERS)
    if not has_trigger:
        return None

    # Try alias matching first (more precise)
    for alias, canonical in _SUBJECT_ALIASES.items():
        if alias in normalized:
            if _normalize(canonical) == _normalize(current_subject):
                return None  # Already on this subject
            # Find the materia_id from the subjects cache
            for _idx, (mid, name) in subjects.items():
                if _normalize(name) == _normalize(canonical):
                    return (mid, name)

    # Try direct matching against subject names from DB
    for _idx, (mid, name) in subjects.items():
        name_normalized = _normalize(name)
        # Check if any significant word from the subject name appears
        name_words = name_normalized.split()
        if any(word in normalized and len(word) > 3 for word in name_words):
            if _normalize(name) == _normalize(current_subject):
                return None
            return (mid, name)

    # Trigger phrase found but no subject matched — return sentinel for ambiguous
    return ("__ambiguous__", "")
