"""System prompt construction for the agentic LLM."""

import logging
import unicodedata
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"
CONTEXT_DIR = Path(__file__).resolve().parent.parent.parent / "context"


def load_template(name: str) -> str:
    path = PROMPTS_DIR / f"modo_{name}.md"
    return path.read_text(encoding="utf-8")


def _slugify(text: str) -> str:
    """Convert a subject/career name to a filesystem-safe slug."""
    text = text.lower().strip()
    nfkd = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in nfkd if not unicodedata.combining(c))
    text = text.replace(" ", "_").replace(",", "").replace(".", "")
    return text


def load_subject_context(materia_nombre: str) -> str | None:
    """Load curriculum context for a subject from the context folder."""
    # Search across all career/trimester directories
    if not CONTEXT_DIR.exists():
        return None

    materia_slug = _slugify(materia_nombre)
    for career_dir in CONTEXT_DIR.iterdir():
        if not career_dir.is_dir():
            continue
        for trimestre_dir in career_dir.iterdir():
            if not trimestre_dir.is_dir():
                continue
            # Exact match first
            path = trimestre_dir / f"{materia_slug}.md"
            if path.exists():
                try:
                    return path.read_text(encoding="utf-8")
                except OSError:
                    continue
            # Prefix match for truncated names (e.g. "algebra_linea" → "algebra_lineal.md")
            for md_file in trimestre_dir.glob("*.md"):
                if md_file.stem.startswith(materia_slug):
                    try:
                        return md_file.read_text(encoding="utf-8")
                    except OSError:
                        continue
    return None


def _build_student_context(
    student_subjects: list[str] | None = None,
    cronograma: dict | None = None,
) -> str:
    """Build the student context block for the system prompt."""
    lines = []

    if student_subjects:
        lines.append("Materias que cursa: " + ", ".join(student_subjects))

    if cronograma and cronograma.get("materias"):
        lines.append("\nCRONOGRAMA DE EVALUACIONES:")
        for mat in cronograma["materias"]:
            nombre = mat.get("nombre", "?")
            evals = mat.get("evaluaciones", [])
            if evals:
                for ev in evals:
                    fecha = ev.get("fecha", "fecha por definir")
                    tipo = ev.get("tipo", "evaluacion")
                    temas = ", ".join(ev.get("temas", [])) or "temas por definir"
                    lines.append(f"- {nombre}: {tipo} ({fecha}) — temas: {temas}")
            else:
                lines.append(f"- {nombre}: sin evaluaciones registradas")
    elif student_subjects:
        lines.append("\n(El estudiante no ha subido cronograma de evaluaciones)")

    # Add upcoming evaluation alerts
    if student_subjects:
        eval_alerts = _build_eval_alerts(student_subjects)
        if eval_alerts:
            lines.append(eval_alerts)

    return "\n".join(lines) if lines else "Sin informacion del estudiante disponible."


def _build_eval_alerts(subjects: list[str]) -> str | None:
    """Build alerts for evaluations within the next 7 days."""
    try:
        from app.bot.services.cronograma_service import get_upcoming_evaluaciones
        alerts = []
        for subject in subjects:
            upcoming = get_upcoming_evaluaciones(subject, within_days=7)
            for ev in upcoming:
                days = (ev.fecha - date.today()).days
                topics = ", ".join(ev.temas) if ev.temas else "temas por definir"
                alerts.append(f"- ALERTA: {subject} tiene {ev.nombre} en {days} dia(s) (temas: {topics})")
        if alerts:
            return "\nEVALUACIONES PROXIMAS (prioriza estos temas):\n" + "\n".join(alerts)
    except Exception as e:
        logger.debug("Eval alerts skipped: %s", e)
    return None


def build_system_prompt(
    student_subjects: list[str] | None = None,
    cronograma: dict | None = None,
) -> str:
    """Build the complete system prompt for student chat.

    Injects student context (subjects, cronograma, eval alerts)
    and any available curriculum context.
    """
    template = load_template("agente")
    student_context = _build_student_context(student_subjects, cronograma)
    prompt = template.replace("{student_context}", student_context)

    # Inject curriculum context for known subjects
    if student_subjects:
        context_blocks = []
        for subject in student_subjects:
            ctx = load_subject_context(subject)
            if ctx:
                context_blocks.append(f"--- {subject} ---\n{ctx}")
        if context_blocks:
            prompt += "\n\nCONTEXTO CURRICULAR:\n" + "\n\n".join(context_blocks)

    return prompt


def build_professor_prompt() -> str:
    """Build the system prompt for professor mode."""
    return load_template("profesor")
