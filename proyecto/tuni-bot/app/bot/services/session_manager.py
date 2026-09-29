"""Session lifecycle management."""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.core.config import settings
from app.db.client import get_supabase

logger = logging.getLogger(__name__)


@dataclass
class InteractionRecord:
    """Single interaction buffered in memory during a conversation."""
    prompt: str
    response: str
    prompt_length_chars: int
    response_length_chars: int
    total_tokens: int
    elapsed_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    self_correction: bool = False
    copy_paste_suspect: bool = False
    hour: int = field(default_factory=lambda: datetime.now().hour)


@dataclass
class UserSession:
    """In-memory state for an active Telegram user session."""
    user_id: str
    session_id: str
    role: str = "student"  # "student" or "professor"
    history: list[dict[str, str]] = field(default_factory=list)
    last_activity: float = field(default_factory=time.monotonic)
    message_count: int = 0
    # In-memory buffer — flushed on session close, not on each message
    interaction_buffer: list[InteractionRecord] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def is_expired(self) -> bool:
        timeout = settings.bot_session_timeout_minutes * 60
        return (time.monotonic() - self.last_activity) > timeout

    def touch(self) -> None:
        self.last_activity = time.monotonic()

    @property
    def depth(self) -> int:
        """Number of user-assistant exchange pairs."""
        return self.message_count

    def buffer_interaction(
        self,
        prompt: str,
        response: str,
        total_tokens: int,
        elapsed_ms: float,
        self_correction: bool = False,
    ) -> None:
        """Buffer an interaction in memory — zero disk I/O."""
        self.interaction_buffer.append(InteractionRecord(
            prompt=prompt,
            response=response,
            prompt_length_chars=len(prompt),
            response_length_chars=len(response),
            total_tokens=total_tokens,
            elapsed_ms=elapsed_ms,
            self_correction=self_correction,
            copy_paste_suspect=len(prompt) > 200,
            hour=datetime.now().hour,
        ))


def create_session(user_id: str, role: str = "student") -> str:
    """Create a new session in Supabase. Returns session_id."""
    sb = get_supabase()
    row = {
        "user_id": user_id,
        "modo_inicial": "agentic",
        "dispositivo": "telegram",
    }
    result = sb.table("sesion").insert(row).execute()
    session_id = result.data[0]["id_sesion"]
    logger.info("Created session %s for user %s", session_id, user_id)
    return session_id


def close_session(session_id: str, session: "UserSession | None" = None, telegram_id: int | None = None) -> None:
    """Close a session: flush buffered telemetry, then mark closed in Supabase."""
    # Flush buffered interactions to student JSON + conversation log
    if session and telegram_id and session.interaction_buffer:
        from app.bot.services.student_tracker import flush_session_telemetry
        flush_session_telemetry(telegram_id, session)

    # Mark session closed in Supabase
    try:
        sb = get_supabase()
        sb.table("sesion").update({
            "timestamp_fin": datetime.now(timezone.utc).isoformat(),
        }).eq("id_sesion", session_id).execute()
        logger.info("Closed session %s (%d interactions flushed)",
                     session_id, len(session.interaction_buffer) if session else 0)
    except Exception as e:
        logger.error("Failed to close session %s: %s", session_id, e)
