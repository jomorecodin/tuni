import logging

from app.db.client import get_supabase

logger = logging.getLogger(__name__)


def get_or_create_user(telegram_id: int) -> str:
    """Return the usuario.user_id for a Telegram user, creating if needed."""
    sb = get_supabase()

    # Look up existing user
    result = (
        sb.table("usuario")
        .select("user_id")
        .eq("telegram_id", telegram_id)
        .execute()
    )
    if result.data:
        return result.data[0]["user_id"]

    # Create new user
    result = (
        sb.table("usuario")
        .insert({"telegram_id": telegram_id, "estado_participacion": "activo"})
        .execute()
    )
    user_id = result.data[0]["user_id"]
    logger.info("Created new user %s for telegram_id %d", user_id, telegram_id)
    return user_id
