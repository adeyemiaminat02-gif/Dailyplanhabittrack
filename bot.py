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

# Module imports
from handlers import calendar, habits, help, planner, profile, reminders, settings, start, statistics
from scheduler import start_scheduler, stop_scheduler


async def callback_router(update, context):
    """Route all inline keyboard callback queries to corresponding handler logic."""
    query = update.callback_query
    await query.answer()
    data = query.data or ""

    logger.info(f"Received callback_data: {data} from user {update.effective_user.id}")

    # --- Navigation & Menus ---
    if data in ["show_stats", "stats"]:
        await statistics.stats_handler(update, context)
    elif data in ["show_calendar", "calendar"]:
        await calendar.calendar_handler(update, context)
    elif data in ["show_settings", "settings"]:
        await settings.settings_handler(update, context)
    elif data in ["show_profile", "profile"]:
        await profile.profile_handler(update, context)

    # --- Tasks Dispatcher ---
    elif any(data.startswith(prefix) for prefix in ["task_", "add_task", "view_tasks", "complete_task", "delete_task"]):
        handler = getattr(planner, "task_callback_handler", getattr(planner, "task_command_handler", None))
        if handler:
            await handler(update, context)

    # --- Habits Dispatcher ---
    elif any(data.startswith(prefix) for prefix in ["habit_", "add_habit", "view_habits", "log_habit", "complete_habit"]):
        handler = getattr(habits, "habit_callback_handler", getattr(habits, "habit_command_handler", None))
        if handler:
            await handler(update, context)

    # --- Reminders Dispatcher ---
    elif any(data.startswith(prefix) for prefix in ["reminder_", "add_reminder", "view_reminders", "delete_reminder"]):
        handler = getattr(reminders, "reminder_callback_handler", getattr(reminders, "reminder_command_handler", None))
        if handler:
            await handler(update, context)

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
    app.add_handler(CommandHandler("start", start.start_handler))
    app.add_handler(CommandHandler("help", help.help_handler))
    app.add_handler(CommandHandler("tasks", planner.task_command_handler))
    app.add_handler(CommandHandler("habit", habits.habit_command_handler))
    app.add_handler(CommandHandler("remind", reminders.reminder_command_handler))
    app.add_handler(CommandHandler("stats", statistics.stats_handler))
    app.add_handler(CommandHandler("calendar", calendar.calendar_handler))
    app.add_handler(CommandHandler("settings", settings.settings_handler))
    app.add_handler(CommandHandler("profile", profile.profile_handler))

    # Catch-all Callback Query Handler for Inline Buttons
    app.add_handler(CallbackQueryHandler(callback_router))

    logger.info("Bot successfully initialized. Starting long polling loop...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
