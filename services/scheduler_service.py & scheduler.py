from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import Application
from services.reminder_service import ReminderService
from config import logger

scheduler = AsyncIOScheduler()

async def check_and_send_reminders(app: Application):
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
                logger.error(f"Failed to send reminder {rem.id} to {rem.user_id}: {e}")
    except Exception as e:
        logger.error(f"Error in scheduler check loop: {e}")

def setup_scheduler(app: Application):
    scheduler.add_job(check_and_send_reminders, "interval", seconds=60, args=[app])
    scheduler.start()
