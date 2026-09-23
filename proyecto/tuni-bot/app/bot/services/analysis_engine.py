"""Automated gap analysis engine.

Reads all student JSONs, conversation logs, cronogramas, and reflections
to produce weekly reports identifying educational gaps per subject.

Key analyses:
- Recurring unclear_points from class check-ins
- Perceived knowledge gaps from post-exam reflections
- Teaching gaps (instructor feedback) from reflections
- Pre-eval usage spikes and study patterns
- Per-subject and cross-subject aggregations
"""

import json
import logging
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from app.core.config import settings
from app.bot.services.cronograma_service import (
    get_evaluaciones,
    get_all_recent_evals,
    load_all_cronogramas,
    _cronogramas,
    _loaded,
)

logger = logging.getLogger(__name__)

DATA_DIR = Path(settings.data_dir)
CONVERSATIONS_DIR = DATA_DIR.parent / "conversations"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_all_students() -> list[dict]:
    """Load all student JSON files."""
    students = []
    if not DATA_DIR.exists():
        return students
    for path in DATA_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            students.append(data)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Skipping %s: %s", path.name, e)
    return students


def _load_conversations(since: date | None = None) -> list[dict]:
    """Load conversation log files, optionally filtered by date."""
    logs = []
    if not CONVERSATIONS_DIR.exists():
        return logs
    for path in CONVERSATIONS_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if since:
                started = data.get("started_at", "")
                if started:
                    dt = datetime.fromisoformat(started)
                    if dt.date() < since:
                        continue
            logs.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return logs


# ---------------------------------------------------------------------------
# Gap extraction
# ---------------------------------------------------------------------------

def _extract_checkin_gaps(students: list[dict], since: date | None = None) -> dict[str, list[str]]:
    """Extract unclear_points from class check-ins, grouped by subject.

    Returns: {materia: [unclear_point_text, ...]}
    """
    gaps = defaultdict(list)
    for student in students:
        for checkin in student.get("class_checkins", []):
            unclear = checkin.get("unclear_points", "")
            if not unclear or unclear.lower() in ("no", "nada", "ninguno", "-"):
                continue
            # Date filter
            if since:
                ts = checkin.get("timestamp", "")
                if ts:
                    try:
                        dt = datetime.fromisoformat(ts)
                        if dt.date() < since:
                            continue
                    except ValueError:
                        pass
            materia = checkin.get("materia", "Desconocida")
            gaps[materia].append(unclear)
    return dict(gaps)


def _extract_reflection_gaps(students: list[dict], since: date | None = None) -> dict[str, dict]:
    """Extract perceived_gaps and teaching_gaps from heartbeat_responses.

    Returns: {materia: {"perceived": [...], "teaching": [...], "scores": [int]}}
    """
    result = defaultdict(lambda: {"perceived": [], "teaching": [], "scores": []})
    for student in students:
        for ref in student.get("patterns", {}).get("heartbeat_responses", []):
            materia = ref.get("materia", "Desconocida")
            if since:
                ts = ref.get("timestamp", "")
                if ts:
                    try:
                        dt = datetime.fromisoformat(ts)
                        if dt.date() < since:
                            continue
                    except ValueError:
                        pass

            pg = ref.get("perceived_gaps", "")
            tg = ref.get("teaching_gaps", "")
            score = ref.get("self_assessment")

            if pg and pg.lower() not in ("no", "nada", "ninguno", "-"):
                result[materia]["perceived"].append(pg)
            if tg and tg.lower() not in ("no", "nada", "ninguno", "-"):
                result[materia]["teaching"].append(tg)
            if score is not None:
                result[materia]["scores"].append(score)

    return dict(result)


def _extract_usage_spikes(students: list[dict]) -> dict[str, list[dict]]:
    """Extract pre-eval usage spikes, grouped by subject."""
    spikes = defaultdict(list)
    for student in students:
        for spike in student.get("patterns", {}).get("pre_eval_usage_spikes", []):
            materia = spike.get("materia", "Desconocida")
            spikes[materia].append(spike)
    return dict(spikes)


def _count_topics_mentioned(texts: list[str], eval_topics: list[str]) -> Counter:
    """Count how often each evaluation topic appears in free-text responses."""
    counter = Counter()
    for text in texts:
        text_lower = text.lower()
        for topic in eval_topics:
            if topic.lower() in text_lower:
                counter[topic] += 1
    return counter


# ---------------------------------------------------------------------------
# Public report generators
# ---------------------------------------------------------------------------

def generate_weekly_report(weeks_back: int = 1) -> dict:
    """Generate a comprehensive weekly gap analysis report.

    Args:
        weeks_back: How many weeks back to analyze (default 1).

    Returns a dict with:
        - period: {start, end}
        - per_subject: {materia: {checkin_gaps, reflection_gaps, ...}}
        - overview: {total_students, active_students, total_sessions, ...}
        - top_gaps: [{topic, mentions, subjects}]
    """
    if not _loaded:
        load_all_cronogramas()

    since = date.today() - timedelta(weeks=weeks_back)
    students = _load_all_students()
    conversations = _load_conversations(since)

    checkin_gaps = _extract_checkin_gaps(students, since)
    reflection_data = _extract_reflection_gaps(students, since)
    usage_spikes = _extract_usage_spikes(students)

    # Per-subject analysis
    all_subjects = set(checkin_gaps.keys()) | set(reflection_data.keys()) | set(_cronogramas.keys())
    per_subject = {}

    for materia in sorted(all_subjects):
        subj_convos = [c for c in conversations if c.get("materia") == materia]
        subj_checkins = checkin_gaps.get(materia, [])
        subj_reflections = reflection_data.get(materia, {"perceived": [], "teaching": [], "scores": []})
        subj_spikes = usage_spikes.get(materia, [])

        # Get eval topics for matching
        evals = get_evaluaciones(materia)
        all_eval_topics = []
        for ev in evals:
            all_eval_topics.extend(ev.temas)

        # Count topic mentions across all gaps
        all_gap_texts = subj_checkins + subj_reflections["perceived"] + subj_reflections["teaching"]
        topic_mentions = _count_topics_mentioned(all_gap_texts, all_eval_topics)

        avg_score = (
            sum(subj_reflections["scores"]) / len(subj_reflections["scores"])
            if subj_reflections["scores"]
            else None
        )

        per_subject[materia] = {
            "sessions_count": len(subj_convos),
            "total_exchanges": sum(c.get("total_exchanges", 0) for c in subj_convos),
            "checkin_unclear_points": subj_checkins,
            "checkin_count": len(subj_checkins),
            "reflection_perceived_gaps": subj_reflections["perceived"],
            "reflection_teaching_gaps": subj_reflections["teaching"],
            "reflection_avg_score": avg_score,
            "reflection_count": len(subj_reflections["scores"]),
            "pre_eval_spikes": len(subj_spikes),
            "topic_gap_frequency": dict(topic_mentions.most_common(10)),
        }

    # Overview metrics
    active_ids = set()
    for conv in conversations:
        tid = conv.get("telegram_id")
        if tid:
            active_ids.add(tid)

    total_exchanges = sum(c.get("total_exchanges", 0) for c in conversations)

    # Top gaps across all subjects
    global_gap_counter = Counter()
    for materia, data in per_subject.items():
        for topic, count in data.get("topic_gap_frequency", {}).items():
            global_gap_counter[(topic, materia)] += count

    top_gaps = [
        {"topic": topic, "subject": materia, "mentions": count}
        for (topic, materia), count in global_gap_counter.most_common(15)
    ]

    return {
        "period": {
            "start": since.isoformat(),
            "end": date.today().isoformat(),
        },
        "overview": {
            "total_students": len(students),
            "active_students": len(active_ids),
            "total_sessions": len(conversations),
            "total_exchanges": total_exchanges,
            "subjects_with_data": len([s for s in per_subject.values() if s["sessions_count"] > 0]),
        },
        "per_subject": per_subject,
        "top_gaps": top_gaps,
    }


def get_subject_gap_detail(materia: str) -> dict:
    """Deep-dive analysis for a single subject.

    Returns structured gap analysis including:
    - All unclear points from check-ins
    - All reflection responses
    - Topic-gap correlation with eval schedule
    - Usage patterns
    """
    if not _loaded:
        load_all_cronogramas()

    students = _load_all_students()
    conversations = _load_conversations()

    # Collect all data for this subject
    checkin_gaps = []
    teaching_gaps = []
    perceived_gaps = []
    scores = []
    spikes = []

    for student in students:
        for checkin in student.get("class_checkins", []):
            if checkin.get("materia") != materia:
                continue
            unclear = checkin.get("unclear_points", "")
            if unclear and unclear.lower() not in ("no", "nada", "ninguno", "-"):
                checkin_gaps.append({
                    "text": unclear,
                    "timestamp": checkin.get("timestamp"),
                    "attended": checkin.get("attended_class"),
                    "last_topic": checkin.get("last_topic_covered"),
                })

        for ref in student.get("patterns", {}).get("heartbeat_responses", []):
            if ref.get("materia") != materia:
                continue
            pg = ref.get("perceived_gaps", "")
            tg = ref.get("teaching_gaps", "")
            if pg and pg.lower() not in ("no", "nada", "ninguno", "-"):
                perceived_gaps.append({"text": pg, "eval_tipo": ref.get("eval_tipo"), "timestamp": ref.get("timestamp")})
            if tg and tg.lower() not in ("no", "nada", "ninguno", "-"):
                teaching_gaps.append({"text": tg, "eval_tipo": ref.get("eval_tipo"), "timestamp": ref.get("timestamp")})
            if ref.get("self_assessment"):
                scores.append(ref["self_assessment"])

        for spike in student.get("patterns", {}).get("pre_eval_usage_spikes", []):
            if spike.get("materia") == materia:
                spikes.append(spike)

    # Session analysis
    subj_convos = [c for c in conversations if c.get("materia") == materia]
    avg_depth = (
        sum(c.get("total_exchanges", 0) for c in subj_convos) / len(subj_convos)
        if subj_convos
        else 0
    )

    # Eval schedule
    evals = get_evaluaciones(materia)
    eval_timeline = [
        {
            "tipo": ev.tipo,
            "nombre": ev.nombre,
            "fecha": ev.fecha.isoformat(),
            "temas": ev.temas,
            "peso": ev.peso,
        }
        for ev in evals
    ]

    # Topic-gap correlation
    all_topics = []
    for ev in evals:
        all_topics.extend(ev.temas)
    all_texts = [g["text"] for g in checkin_gaps] + [g["text"] for g in perceived_gaps] + [g["text"] for g in teaching_gaps]
    topic_freq = _count_topics_mentioned(all_texts, all_topics)

    return {
        "materia": materia,
        "checkin_gaps": checkin_gaps,
        "perceived_gaps": perceived_gaps,
        "teaching_gaps": teaching_gaps,
        "self_assessment_scores": scores,
        "avg_self_assessment": sum(scores) / len(scores) if scores else None,
        "pre_eval_spikes": spikes,
        "sessions_count": len(subj_convos),
        "avg_session_depth": round(avg_depth, 1),
        "eval_timeline": eval_timeline,
        "topic_gap_frequency": dict(topic_freq.most_common()),
    }


def get_students_overview() -> list[dict]:
    """Summary of all registered students for the dashboard."""
    students = _load_all_students()
    overview = []
    for s in students:
        patterns = s.get("patterns", {})
        overview.append({
            "telegram_id": s.get("telegram_id"),
            "consent_date": s.get("consent_date"),
            "career": s.get("career_name", s.get("career", "")),
            "trimestre": s.get("trimestre"),
            "subjects_used": s.get("subjects_used", []),
            "total_sessions": patterns.get("total_sessions", 0),
            "total_interactions": patterns.get("total_interactions", 0),
            "avg_session_depth": patterns.get("avg_session_depth", 0),
            "formative_substitutive_index": patterns.get("formative_substitutive_index", 0),
            "copy_paste_indicators": patterns.get("copy_paste_indicators", 0),
            "self_correction_count": patterns.get("self_correction_count", 0),
            "checkin_count": len(s.get("class_checkins", [])),
            "reflection_count": len(patterns.get("heartbeat_responses", [])),
        })
    return overview


def get_pilot_health() -> dict:
    """Overall pilot health metrics for real-time monitoring."""
    students = _load_all_students()
    conversations = _load_conversations()

    today = date.today()
    week_ago = today - timedelta(days=7)
    day_ago = today - timedelta(days=1)

    # Recent activity
    recent_convos = [
        c for c in conversations
        if c.get("started_at") and datetime.fromisoformat(c["started_at"]).date() >= week_ago
    ]
    today_convos = [
        c for c in conversations
        if c.get("started_at") and datetime.fromisoformat(c["started_at"]).date() >= day_ago
    ]

    # Active students this week
    active_week = set()
    for c in recent_convos:
        tid = c.get("telegram_id")
        if tid:
            active_week.add(tid)

    # Subject usage distribution
    subject_usage = Counter()
    for c in recent_convos:
        materia = c.get("materia", "Desconocida")
        subject_usage[materia] += 1

    # Check-in completion rate
    total_checkins = sum(len(s.get("class_checkins", [])) for s in students)
    total_reflections = sum(len(s.get("patterns", {}).get("heartbeat_responses", [])) for s in students)

    # Upcoming evals
    if not _loaded:
        load_all_cronogramas()
    upcoming = []
    for materia in _cronogramas:
        from app.bot.services.cronograma_service import get_upcoming_evaluaciones
        for ev in get_upcoming_evaluaciones(materia, within_days=14):
            upcoming.append({
                "materia": ev.materia,
                "nombre": ev.nombre,
                "fecha": ev.fecha.isoformat(),
                "dias": (ev.fecha - today).days,
            })
    upcoming.sort(key=lambda x: x["fecha"])

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "registered_students": len(students),
        "active_students_week": len(active_week),
        "sessions_today": len(today_convos),
        "sessions_this_week": len(recent_convos),
        "total_conversations": len(conversations),
        "total_checkins": total_checkins,
        "total_reflections": total_reflections,
        "subject_usage_week": dict(subject_usage.most_common()),
        "upcoming_evaluations": upcoming[:10],
    }


def build_ai_context() -> str:
    """Build a context string with all collected data for AI consultation.

    This is fed to the LLM when the supervisor asks questions about the pilot.
    """
    health = get_pilot_health()
    students_overview = get_students_overview()
    report = generate_weekly_report(weeks_back=4)

    lines = [
        "# Datos del piloto TUNI",
        f"Fecha: {date.today().isoformat()}",
        "",
        "## Estado general",
        f"- Estudiantes registrados: {health['registered_students']}",
        f"- Activos esta semana: {health['active_students_week']}",
        f"- Sesiones esta semana: {health['sessions_this_week']}",
        f"- Total conversaciones: {health['total_conversations']}",
        f"- Check-ins completados: {health['total_checkins']}",
        f"- Reflexiones completadas: {health['total_reflections']}",
        "",
        "## Uso por materia (ultima semana)",
    ]
    for materia, count in health.get("subject_usage_week", {}).items():
        lines.append(f"- {materia}: {count} sesiones")

    lines.append("")
    lines.append("## Evaluaciones proximas")
    for ev in health.get("upcoming_evaluations", []):
        lines.append(f"- {ev['materia']}: {ev['nombre']} en {ev['dias']} dias ({ev['fecha']})")

    lines.append("")
    lines.append("## Brechas detectadas (ultimas 4 semanas)")
    for materia, data in report.get("per_subject", {}).items():
        if data["checkin_count"] == 0 and data["reflection_count"] == 0:
            continue
        lines.append(f"\n### {materia}")
        if data["checkin_unclear_points"]:
            lines.append("Dudas en check-ins:")
            for gap in data["checkin_unclear_points"][:5]:
                lines.append(f"  - {gap}")
        if data["reflection_perceived_gaps"]:
            lines.append("Brechas percibidas post-examen:")
            for gap in data["reflection_perceived_gaps"][:5]:
                lines.append(f"  - {gap}")
        if data["reflection_teaching_gaps"]:
            lines.append("Brechas de ensenanza reportadas:")
            for gap in data["reflection_teaching_gaps"][:5]:
                lines.append(f"  - {gap}")
        if data["reflection_avg_score"] is not None:
            lines.append(f"Autoevaluacion promedio: {data['reflection_avg_score']:.1f}/5")
        if data["topic_gap_frequency"]:
            lines.append("Temas mas mencionados como dificiles:")
            for topic, count in list(data["topic_gap_frequency"].items())[:5]:
                lines.append(f"  - {topic}: {count} menciones")

    lines.append("")
    lines.append("## Resumen de estudiantes")
    for s in students_overview:
        lines.append(
            f"- TG:{s['telegram_id']} | sesiones:{s['total_sessions']} | "
            f"interacciones:{s['total_interactions']} | materias:{', '.join(s['subjects_used']) or 'ninguna'} | "
            f"FSI:{s['formative_substitutive_index']:.2f}"
        )

    return "\n".join(lines)
