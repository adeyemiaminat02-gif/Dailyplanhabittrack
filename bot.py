"""
Main Application Entrypoint.
Sets up Python path resolution, initializes database, loads handlers, and starts polling.
"""
import sys
import os

# Ensure project root directory is in sys.path to prevent ModuleNotFoundError on Render
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler
)
from config import config, logger
from database import init_db
from scheduler import start_scheduler, stop_scheduler

from handlers.start import start_handler
from handlers.help import help_handler
from handlers.planner import task_command_handler
from handlers.habits import habit_command_handler
from handlers.reminders import reminder_command_handler
from handlers.statistics import stats_handler
from handlers.calendar import calendar_handler
from handlers.settings import settings_handler
from handlers.profile import profile_handler


async def callback_router(update, context):
    """Route inline keyboard callback queries to corresponding handler logic."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "show_stats":
        await stats_handler(update, context)
    elif query.data == "show_calendar":
        await calendar_handler(update, context)
    elif query.data == "show_settings":
        await settings_handler(update, context)


async def post_init(app) -> None:
    """Runs after application build and inside the active event loop."""
    logger.info("Ensuring database schema exists...")
    await init_db()
    logger.info("Starting background scheduler...")
    await start_scheduler(app)


async def post_shutdown(app) -> None:
    """Runs when the application is shutting down."""
    logger.info("Shutting down background scheduler...")
    await stop_scheduler(app)


def main():
    logger.info("Building Telegram Application...")
    
    app = (
        ApplicationBuilder()
        .token(config.BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # Register Primary Command Handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("tasks", task_command_handler))
    app.add_handler(CommandHandler("habit", habit_command_handler))
    app.add_handler(CommandHandler("remind", reminder_command_handler))
    app.add_handler(CommandHandler("stats", stats_handler))
    app.add_handler(CommandHandler("calendar", calendar_handler))
    app.add_handler(CommandHandler("settings", settings_handler))
    app.add_handler(CommandHandler("profile", profile_handler))
    
    # Register Callback Handler
    app.add_handler(CallbackQueryHandler(callback_router))

    logger.info("Bot successfully initialized. Starting long polling loop...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
