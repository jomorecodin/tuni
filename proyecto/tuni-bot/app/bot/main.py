"""TUNI Telegram bot application setup and entry point."""

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
from app.bot.handlers.career_selection import (
    career_callback, trimester_callback, back_to_career, back_to_trimester,
)
from app.bot.handlers.subject_selection import subject_callback
from app.bot.handlers.class_checkin import (
    attendance_callback,
    topic_response,
    unclear_response,
)
from app.bot.handlers.chat import handle_message
from app.bot.handlers.commands import (
    help_command,
    materia_command,
    estado_command,
    horario_command,
)
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
            State.SELECTING_CAREER: [
                CallbackQueryHandler(career_callback, pattern="^career_"),
            ],
            State.SELECTING_TRIMESTER: [
                CallbackQueryHandler(back_to_career, pattern="^back_career$"),
                CallbackQueryHandler(trimester_callback, pattern="^trimester_"),
            ],
            State.SELECTING_SUBJECT: [
                CallbackQueryHandler(back_to_trimester, pattern="^back_trimester$"),
                CallbackQueryHandler(subject_callback, pattern="^subject_"),
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
            State.CHATTING: [
                CommandHandler("materia", materia_command),
                CommandHandler("horario", horario_command),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
            ],
        },
        fallbacks=[
            CommandHandler("start", start_command),
            CommandHandler("ayuda", help_command),
        ],
        name="tuni_conversation",
        persistent=True,
        per_user=True,
        per_chat=True,
    )

    app.add_handler(conv_handler)

    # Reflection handler (separate from main conversation — handles proactive messages)
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
