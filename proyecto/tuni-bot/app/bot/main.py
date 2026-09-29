"""TUNI Telegram bot application setup and entry point.

Architecture:
- Single agentic model (no dual modes)
- Simplified onboarding: /start → consent → cronograma upload → CHATTING
- Professor role via /profesor + universal password
- Document uploads handled mid-conversation via Gemini multimodal
"""

import logging

from telegram.ext import (
    ApplicationBuilder,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    PicklePersistence,
)

from app.core.config import settings
from app.bot.constants import State
from app.bot.handlers.start import (
    start_command,
    consent_callback,
    schedule_upload,
    skip_schedule,
)
from app.bot.handlers.class_checkin import (
    attendance_callback,
    topic_response,
    unclear_response,
)
from app.bot.handlers.chat import handle_message
from app.bot.handlers.commands import (
    help_command,
    estado_command,
    horario_command,
    profesor_command,
)
from app.bot.handlers.professor import professor_auth
from app.bot.handlers.document_upload import handle_document
from app.bot.services.cronograma_service import load_all_cronogramas
from app.bot.services.scheduler import post_init
from app.bot.handlers.reflection import (
    reflection_self_assessment_callback,
    reflection_gaps_response,
    reflection_teaching_response,
)

logger = logging.getLogger(__name__)


def create_application():
    """Build and configure the bot application."""
    persistence = PicklePersistence(filepath="data/bot_persistence.pickle")

    # Load evaluation schedules into memory
    load_all_cronogramas()

    app = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .persistence(persistence)
        .build()
    )

    # Main conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            State.AWAITING_CONSENT: [
                CallbackQueryHandler(consent_callback, pattern="^consent_"),
            ],
            State.UPLOAD_SCHEDULE: [
                MessageHandler(
                    filters.PHOTO | filters.Document.ALL,
                    schedule_upload,
                ),
                CommandHandler("saltar", skip_schedule),
            ],
            State.CLASS_CHECKIN_ATTENDANCE: [
                CallbackQueryHandler(attendance_callback, pattern="^checkin_"),
            ],
            State.CLASS_CHECKIN_TOPIC: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, topic_response),
            ],
            State.CLASS_CHECKIN_UNCLEAR: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, unclear_response),
            ],
            State.PROFESSOR_AUTH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, professor_auth),
            ],
            State.CHATTING: [
                CommandHandler("horario", horario_command),
                CommandHandler("profesor", profesor_command),
                MessageHandler(filters.PHOTO | filters.Document.ALL, handle_document),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
            ],
        },
        fallbacks=[
            CommandHandler("start", start_command),
            CommandHandler("ayuda", help_command),
            CommandHandler("profesor", profesor_command),
        ],
        name="tuni_conversation",
        persistent=True,
        per_user=True,
        per_chat=True,
    )

    app.add_handler(conv_handler)

    # Reflection handler (separate — handles proactive post-exam messages)
    reflection_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                reflection_self_assessment_callback, pattern="^reflect_score_"
            ),
        ],
        states={
            State.REFLECTION_GAPS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, reflection_gaps_response),
            ],
            State.REFLECTION_TEACHING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, reflection_teaching_response),
            ],
        },
        fallbacks=[CommandHandler("start", start_command)],
        name="reflection_conversation",
        persistent=True,
        per_user=True,
        per_chat=True,
        conversation_timeout=3600,
    )
    app.add_handler(reflection_conv, group=1)

    # Global commands (work outside conversation)
    app.add_handler(CommandHandler("ayuda", help_command))
    app.add_handler(CommandHandler("estado", estado_command))

    # Initialize scheduler after bot is fully built
    app.post_init = post_init

    return app


def run_bot():
    """Start the bot with long-polling."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    # Silence httpx noise
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger.info("Starting TUNI Telegram bot...")
    logger.info("LLM provider: %s", settings.llm_provider)

    app = create_application()
    app.run_polling(drop_pending_updates=True)
