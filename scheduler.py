"""
Background Scheduler Module.
Handles periodic tasks such as dispatching pending reminders.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import Application
from services.reminder_service import ReminderService
from config import logger

scheduler = AsyncIOScheduler()


async def check_and_send_reminders(app: Application) -> None:
    """Periodically check database for pending reminders and dispatch via Telegram bot."""
    try:
        reminders = await ReminderService.get_pending_reminders()
        for rem in reminders:
            try:
                await app.bot.send_message(
                    chat_id=rem.user_id,
                    text=f"⏰ **Reminder:** {rem.title}\nType: {rem.reminder_type}",
                    parse_mode="Markdown"
                )
                await ReminderService.mark_sent(rem.id)
            except Exception as e:
                logger.error(f"Failed to send reminder #{rem.id} to user {rem.user_id}: {e}")
    except Exception as e:
        logger.error(f"Error executing reminder check loop: {e}")


def setup_scheduler(app: Application) -> None:
    """Initialize and start the APScheduler background loop."""
    scheduler.add_job(
        check_and_send_reminders,
        trigger="interval",
        seconds=60,
        args=[app],
        id="reminder_checker",
        replace_existing=True
    )
    scheduler.start()
    logger.info("APScheduler initialized and running.")
