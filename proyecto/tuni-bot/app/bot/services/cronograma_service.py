"""Evaluation schedule (cronograma) loader and query service.

Loads YAML files from data/cronogramas/ at bot startup, caches in memory,
and provides query methods for upcoming/past evaluations per subject.
"""

import logging
from datetime import date, timedelta
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

CRONOGRAMA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "cronogramas"


@dataclass
class Evaluacion:
    """Single evaluation event."""
    materia: str
    tipo: str           # "parcial_1", "quiz_1", "proyecto", etc.
    nombre: str         # Human-readable: "Primer Parcial"
    fecha: date
    hora: str | None = None
    temas: list[str] = field(default_factory=list)
    peso: int = 0


# Module-level cache
_cronogramas: dict[str, list[Evaluacion]] = {}
_loaded: bool = False


def load_all_cronogramas() -> None:
    """Load all YAML cronograma files into memory."""
    global _cronogramas, _loaded
    _cronogramas.clear()

    if not CRONOGRAMA_DIR.exists():
        logger.warning("Cronograma directory does not exist: %s", CRONOGRAMA_DIR)
        _loaded = True
        return

    for path in CRONOGRAMA_DIR.glob("*.yaml"):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not data or "materia" not in data:
                continue
            materia = data["materia"]
            evals = []
            for ev in data.get("evaluaciones", []):
                evals.append(Evaluacion(
                    materia=materia,
                    tipo=ev["tipo"],
                    nombre=ev["nombre"],
                    fecha=date.fromisoformat(ev["fecha"]),
                    hora=ev.get("hora"),
                    temas=ev.get("temas", []),
                    peso=ev.get("peso", 0),
                ))
            _cronogramas[materia] = evals
            logger.info("Loaded cronograma for %s: %d evaluaciones", materia, len(evals))
        except Exception as e:
            logger.error("Failed to load cronograma %s: %s", path.name, e)

    _loaded = True
    logger.info("Loaded cronogramas for %d subjects", len(_cronogramas))


def get_evaluaciones(materia: str) -> list[Evaluacion]:
    """Get all evaluations for a subject."""
    if not _loaded:
        load_all_cronogramas()
    return _cronogramas.get(materia, [])


def get_upcoming_evaluaciones(materia: str, within_days: int = 7) -> list[Evaluacion]:
    """Get evaluations for a subject within the next N days."""
    today = date.today()
    cutoff = today + timedelta(days=within_days)
    return [e for e in get_evaluaciones(materia) if today <= e.fecha <= cutoff]


def get_past_evaluaciones(materia: str, within_days: int = 2) -> list[Evaluacion]:
    """Get evaluations that happened within the last N days."""
    today = date.today()
    cutoff = today - timedelta(days=within_days)
    return [e for e in get_evaluaciones(materia) if cutoff <= e.fecha < today]


def get_next_evaluacion(materia: str) -> Evaluacion | None:
    """Get the single next upcoming evaluation for a subject."""
    today = date.today()
    future = [e for e in get_evaluaciones(materia) if e.fecha >= today]
    return min(future, key=lambda e: e.fecha) if future else None


def days_until_eval(materia: str) -> int | None:
    """Days until the next evaluation. None if no upcoming evals."""
    nxt = get_next_evaluacion(materia)
    if nxt is None:
        return None
    return (nxt.fecha - date.today()).days


def get_all_recent_evals(within_days: int = 2) -> list[Evaluacion]:
    """Get all evaluations that recently occurred (for scheduling reflections)."""
    if not _loaded:
        load_all_cronogramas()
    results = []
    for materia in _cronogramas:
        results.extend(get_past_evaluaciones(materia, within_days))
    return results
