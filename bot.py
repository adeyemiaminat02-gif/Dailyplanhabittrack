"""
Main Application Entrypoint.
Sets up Python path resolution, initializes database, loads handlers, and starts polling.
"""
import os
import sys

# Ensure project root directory is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
)

from config import config, logger
from database import init_db
from handlers.calendar import calendar_handler
from handlers.habits import habit_callback_handler, habit_command_handler
from handlers.help import help_handler
from handlers.planner import task_callback_handler, task_command_handler
from handlers.profile import profile_handler
from handlers.reminders import reminder_callback_handler, reminder_command_handler
from handlers.settings import settings_handler
from handlers.start import start_handler
from handlers.statistics import stats_handler
from scheduler import start_scheduler, stop_scheduler


async def callback_router(update, context):
    """Route all inline keyboard callback queries to corresponding handler logic."""
    query = update.callback_query
    await query.answer()
    data = query.data

    logger.info(f"Received callback_data: {data} from user {update.effective_user.id}")

    # --- Navigation & Menus ---
    if data in ["show_stats", "stats"]:
        await stats_handler(update, context)
    elif data in ["show_calendar", "calendar"]:
        await calendar_handler(update, context)
    elif data in ["show_settings", "settings"]:
        await settings_handler(update, context)
    elif data in ["show_profile", "profile"]:
        await profile_handler(update, context)

    # --- Tasks Dispatcher ---
    elif data.startswith(("task_", "add_task", "view_tasks", "complete_task", "delete_task")):
        await task_callback_handler(update, context)

    # --- Habits Dispatcher ---
    elif data.startswith(("habit_", "add_habit", "view_habits", "log_habit", "complete_habit")):
        await habit_callback_handler(update, context)

    # --- Reminders Dispatcher ---
    elif data.startswith(("reminder_", "add_reminder", "view_reminders", "delete_reminder")):
        await reminder_callback_handler(update, context)

    else:
        logger.warning(f"Unhandled callback pattern: {data}")


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

    # Catch-all Callback Query Handler for Inline Buttons
    app.add_handler(CallbackQueryHandler(callback_router))

    logger.info("Bot successfully initialized. Starting long polling loop...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
