"""Per-student JSON file management for behavioral tracking."""

import json
import logging
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


def _student_path(telegram_id: int) -> Path:
    return Path(settings.data_dir) / f"{telegram_id}.json"


def create_student_file(telegram_id: int, user_id: str) -> dict:
    """Create initial student tracking JSON file after consent."""
    data = {
        "telegram_id": telegram_id,
        "user_id": user_id,
        "consent_date": datetime.now(timezone.utc).isoformat(),
        "schedule": {"raw_text": None, "parsed": None},
        "subjects_used": [],
        "class_checkins": [],
        "subject_histories": {},
        "patterns": {
            "total_sessions": 0,
            "total_interactions": 0,
            "avg_session_depth": 0.0,
            "avg_time_between_msgs_sec": 0.0,
            "abandonment_after_socratic": 0,
            "self_correction_count": 0,
            "copy_paste_indicators": 0,
            "cognitive_level_progression": [],
            "scaffolding_effectiveness": {
                "assisted_success_rate": 0.0,
                "avg_iterations_to_solve": 0.0,
                "difficulty_abandonments": 0,
            },
            "self_regulation": {
                "planning_instances": 0,
                "self_corrections": 0,
                "heartbeat_reflections": [],
            },
            "cognitive_load_indicators": {
                "rapid_responses_count": 0,
                "long_pauses_count": 0,
                "fragmented_sequences": 0,
                "abrupt_topic_changes": 0,
            },
            "dependency_indicators": {
                "own_attempt_ratio": 0.0,
                "avg_first_message_length": 0.0,
                "usage_trend_slope": 0.0,
            },
            "desirable_difficulty": {
                "abandonment_after_socratic": 0,
                "persistence_rate": 0.0,
                "topic_revisit_count": 0,
            },
            "metacognition": {
                "metacognitive_questions_count": 0,
                "self_assessment_history": [],
                "calibration_trend": 0.0,
            },
            "formative_substitutive_index": 0.0,
            "usage_hours_histogram": {},
            "pre_eval_usage_spikes": [],
            "heartbeat_responses": [],
        },
        "weekly_snapshots": [],
    }
    _save(telegram_id, data)
    logger.info("Created student tracking file for %d", telegram_id)
    return data


def load_student(telegram_id: int) -> dict | None:
    """Load student tracking data. Returns None if file doesn't exist."""
    path = _student_path(telegram_id)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.error("Failed to load student %d: %s", telegram_id, e)
        return None


def update_student(telegram_id: int, updates: dict) -> None:
    """Apply incremental updates to student tracking data."""
    data = load_student(telegram_id)
    if data is None:
        logger.warning("No student file for %d, skipping update", telegram_id)
        return
    _deep_merge(data, updates)
    _save(telegram_id, data)


def save_subject_history(telegram_id: int, materia: str, history: list[dict]) -> None:
    """Persist conversation history for a subject (last N messages)."""
    data = load_student(telegram_id)
    if data is None:
        return
    max_messages = settings.bot_max_history_messages if hasattr(settings, 'bot_max_history_messages') else 40
    truncated = history[-max_messages:] if len(history) > max_messages else history
    histories = data.get("subject_histories", {})
    histories[materia] = truncated
    data["subject_histories"] = histories
    _save(telegram_id, data)
    logger.debug("Saved %d history messages for %s (student %d)", len(truncated), materia, telegram_id)


def load_subject_history(telegram_id: int, materia: str) -> list[dict]:
    """Load persisted conversation history for a subject."""
    data = load_student(telegram_id)
    if data is None:
        return []
    return data.get("subject_histories", {}).get(materia, [])


def record_session_start(telegram_id: int, subject: str) -> None:
    """Track a new session starting (lightweight — only increments counter)."""
    data = load_student(telegram_id)
    if data is None:
        return

    data["patterns"]["total_sessions"] += 1
    if subject not in data["subjects_used"]:
        data["subjects_used"].append(subject)

    _save(telegram_id, data)


def flush_session_telemetry(telegram_id: int, session) -> None:
    """Batch-process all buffered interactions at session close.

    This is the core of the deferred telemetry architecture:
    - Called ONCE when a conversation ends (timeout, /materia, /nueva)
    - Processes all buffered interactions in a single read-modify-write
    - Also writes a per-conversation JSON log for later analysis

    Zero disk I/O during active conversations — all tracking happens here.
    """
    from app.bot.services.session_manager import InteractionRecord

    data = load_student(telegram_id)
    if data is None:
        logger.warning("No student file for %d, skipping telemetry flush", telegram_id)
        return

    buffer: list[InteractionRecord] = session.interaction_buffer
    if not buffer:
        return

    patterns = data["patterns"]

    # Aggregate all buffered interactions in one pass
    total_new = len(buffer)
    patterns["total_interactions"] += total_new

    self_corrections = 0
    copy_paste_count = 0
    for record in buffer:
        # Usage hours histogram
        hour = str(record.hour)
        hist = patterns["usage_hours_histogram"]
        hist[hour] = hist.get(hour, 0) + 1

        # Copy-paste detection
        if record.copy_paste_suspect:
            copy_paste_count += 1

        # Self-corrections
        if record.self_correction:
            self_corrections += 1

    patterns["copy_paste_indicators"] += copy_paste_count
    patterns["self_correction_count"] += self_corrections
    patterns["self_regulation"]["self_corrections"] += self_corrections

    # Update average session depth
    total_sessions = patterns["total_sessions"] or 1
    current_avg = patterns["avg_session_depth"]
    patterns["avg_session_depth"] = (
        (current_avg * (total_sessions - 1) + total_new) / total_sessions
    )

    # Pre-eval usage spike detection
    _detect_pre_eval_spike(patterns, session)

    # Single write for all accumulated changes
    _save(telegram_id, data)

    # Write per-conversation log file
    _save_conversation_log(telegram_id, session, buffer)

    logger.info(
        "Flushed %d interactions for student %d (session %s)",
        total_new, telegram_id, session.session_id,
    )


def _detect_pre_eval_spike(patterns: dict, session) -> None:
    """Record if this session happened close to an upcoming evaluation."""
    try:
        from app.bot.services.cronograma_service import days_until_eval, get_next_evaluacion
        days = days_until_eval(session.materia_nombre)
        if days is not None and days <= 3:
            nxt = get_next_evaluacion(session.materia_nombre)
            spikes = patterns.get("pre_eval_usage_spikes", [])
            spikes.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "materia": session.materia_nombre,
                "days_until_eval": days,
                "eval_type": nxt.tipo if nxt else None,
                "eval_date": nxt.fecha.isoformat() if nxt else None,
                "session_depth": session.depth,
                "interaction_count": len(session.interaction_buffer),
            })
            patterns["pre_eval_usage_spikes"] = spikes
    except Exception as e:
        logger.debug("Pre-eval spike check skipped: %s", e)


def _save_conversation_log(telegram_id: int, session, buffer) -> None:
    """Write a per-conversation JSON log for post-hoc analysis."""
    from app.bot.services.session_manager import InteractionRecord

    log_dir = Path(settings.data_dir).parent / "conversations"
    log_dir.mkdir(parents=True, exist_ok=True)

    log = {
        "session_id": session.session_id,
        "telegram_id": telegram_id,
        "materia": session.materia_nombre,
        "started_at": session.started_at,
        "closed_at": datetime.now(timezone.utc).isoformat(),
        "total_exchanges": len(buffer),
        "interactions": [
            {
                "timestamp": r.timestamp,
                "prompt": r.prompt,
                "response": r.response,
                "prompt_length_chars": r.prompt_length_chars,
                "response_length_chars": r.response_length_chars,
                "total_tokens": r.total_tokens,
                "elapsed_ms": r.elapsed_ms,
                "self_correction": r.self_correction,
                "copy_paste_suspect": r.copy_paste_suspect,
            }
            for r in buffer
        ],
    }

    path = log_dir / f"{session.session_id}.json"
    fd, tmp_path = tempfile.mkstemp(dir=log_dir, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise

    logger.info("Saved conversation log: %s", path)


def _save(telegram_id: int, data: dict) -> None:
    """Atomic write: write to temp file then rename."""
    path = _student_path(telegram_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def _deep_merge(base: dict, updates: dict) -> None:
    """Recursively merge updates into base dict."""
    for key, value in updates.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
