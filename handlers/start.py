from telegram import Update
from telegram.ext import ContextTypes
from services.database_service import DatabaseService
from services.utils import get_main_keyboard

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await DatabaseService.get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name
    )
    
    welcome_text = (
        f"👋 Welcome, **{user.first_name}**!\n\n"
        "I am your production-grade **Daily Planner & Habit Tracker Bot**.\n"
        "Organize tasks, track habits, maintain streaks, and analyze your productivity seamlessly!\n\n"
        "Use the quick action menu below or send `/help` for detailed commands."
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")
