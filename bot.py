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


async def send_response(update, text, reply_markup=None):
    """Helper to send or edit a message seamlessly for both commands and callbacks."""
    if update.callback_query and update.callback_query.message:
        try:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        except Exception:
            await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def callback_router(update, context):
    """Route all inline keyboard callback queries to corresponding handler logic safely."""
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

    # --- Task Action Callbacks ---
    elif data in ["task_add", "add_task"]:
        await send_response(update, "📝 **Add Task:** Please enter your task title using the `/tasks` command or reply here.")
    elif data in ["task_view", "view_tasks"]:
        if hasattr(planner, "view_tasks_handler"):
            await planner.view_tasks_handler(update, context)
        else:
            await planner.task_command_handler(update, context)

    # --- Habit Action Callbacks ---
    elif data in ["habit_add", "add_habit"]:
        await send_response(update, "➕ **Add Habit:** Use `/habit add <name>` to track a new habit.")
    elif data in ["habit_view", "view_habits"]:
        if hasattr(habits, "view_habits_handler"):
            await habits.view_habits_handler(update, context)
        else:
            await habits.habit_command_handler(update, context)

    # --- Reminder Action Callbacks ---
    elif data in ["reminder_add", "add_reminder"]:
        await send_response(update, "⏰ **Add Reminder:** Use `/remind <text> at <HH:MM>` to set a new reminder.")
    elif data in ["reminder_view", "view_reminders"]:
        if hasattr(reminders, "view_reminders_handler"):
            await reminders.view_reminders_handler(update, context)
        else:
            await reminders.reminder_command_handler(update, context)

    else:
        # Fallback dynamic dispatcher
        for module in [planner, habits, reminders]:
            if hasattr(module, "callback_handler"):
                try:
                    await module.callback_handler(update, context)
                    return
                except Exception as e:
                    logger.error(f"Error executing callback in {module.__name__}: {e}")
        
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
