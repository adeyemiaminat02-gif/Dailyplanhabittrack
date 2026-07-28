from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from services.reminder_service import ReminderService

async def reminder_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    user_id = update.effective_user.id
    
    if len(args) >= 2:
        minutes = int(args[0])
        title = " ".join(args[1:])
        remind_at = datetime.utcnow() + timedelta(minutes=minutes)
        await ReminderService.create_reminder(user_id, title, remind_at)
        await update.message.reply_text(f"⏰ Reminder set for **{minutes} minutes** from now: _{title}_", parse_mode="Markdown")
    else:
        await update.message.reply_text("Usage: `/remind <minutes> <message>`", parse_mode="Markdown")
