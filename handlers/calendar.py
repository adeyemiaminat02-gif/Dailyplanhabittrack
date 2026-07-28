from telegram import Update
from telegram.ext import ContextTypes
from services.planner_service import PlannerService

async def calendar_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    today_tasks = await PlannerService.get_user_tasks(user_id, "today")
    tomorrow_tasks = await PlannerService.get_user_tasks(user_id, "tomorrow")
    
    calendar_text = (
        "📅 **Calendar Overview**\n\n"
        f"**Today ({len(today_tasks)} tasks):**\n" +
        ("\n".join([f" • {t.title}" for t in today_tasks]) if today_tasks else " No tasks scheduled.") +
        f"\n\n**Tomorrow ({len(tomorrow_tasks)} tasks):**\n" +
        ("\n".join([f" • {t.title}" for t in tomorrow_tasks]) if tomorrow_tasks else " No tasks scheduled.")
    )
    await update.message.reply_text(calendar_text, parse_mode="Markdown")
