import logging
import unicodedata
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"
CONTEXT_DIR = Path(__file__).resolve().parent.parent.parent / "context"


def load_template(mode: str) -> str:
    path = PROMPTS_DIR / f"modo_{mode}.md"
    return path.read_text(encoding="utf-8")


def _slugify(text: str) -> str:
    """Convert a subject/career name to a filesystem-safe slug."""
    text = text.lower().strip()
    # Remove accents
    nfkd = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in nfkd if not unicodedata.combining(c))
    # Replace spaces and special chars
    text = text.replace(" ", "_").replace(",", "").replace(".", "")
    return text


def load_subject_context(carrera: str | None, trimestre: int | None, materia_nombre: str) -> str | None:
    """Load additional context for a specific subject from the context folder."""
    if not carrera or not trimestre:
        return None

    carrera_slug = _slugify(carrera)
    materia_slug = _slugify(materia_nombre)
    path = CONTEXT_DIR / carrera_slug / f"trimestre_{trimestre}" / f"{materia_slug}.md"

    if not path.exists():
        return None

    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def build_system_prompt(
    mode: str,
    materia_nombre: str = "General",
    carrera: str | None = None,
    trimestre: int | None = None,
) -> str:
    template = load_template(mode)
    prompt = template.replace("{materia_nombre}", materia_nombre)

    # Inject subject-specific context if available
    context = load_subject_context(carrera, trimestre, materia_nombre)
    if context:
        prompt += f"\n\nCONTEXTO DE LA MATERIA:\n{context}"

    # Inject evaluation proximity context
    eval_ctx = _build_eval_context(materia_nombre)
    if eval_ctx:
        prompt += f"\n\n{eval_ctx}"

    return prompt


def _build_eval_context(materia_nombre: str) -> str | None:
    """Build evaluation proximity context for the system prompt."""
    try:
        from app.bot.services.cronograma_service import get_upcoming_evaluaciones
        upcoming = get_upcoming_evaluaciones(materia_nombre, within_days=7)
        if not upcoming:
            return None

        lines = ["CONTEXTO DE EVALUACIONES PROXIMAS:"]
        for ev in upcoming:
            days = (ev.fecha - date.today()).days
            topics = ", ".join(ev.temas) if ev.temas else "temas por definir"
            lines.append(f"- {ev.nombre} en {days} dia(s) (temas: {topics})")
        lines.append(
            "Ten en cuenta la proximidad de estas evaluaciones al guiar al estudiante. "
            "Prioriza los temas que entraran en la evaluacion proxima."
        )
        return "\n".join(lines)
    except Exception as e:
        logger.debug("Eval context build skipped: %s", e)
        return None
