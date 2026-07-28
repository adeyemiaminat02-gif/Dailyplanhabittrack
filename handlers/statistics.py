from telegram import Update
from telegram.ext import ContextTypes
from services.stats_service import StatsService

async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    stats = await StatsService.get_user_stats(user_id)
    
    report = (
        "📊 **Productivity Statistics Summary**\n\n"
        f"• **Total Tasks:** {stats['total_tasks']}\n"
        f"• **Completed Tasks:** {stats['completed_tasks']}\n"
        f"• **Pending Tasks:** {stats['pending_tasks']}\n"
        f"• **Task Completion Rate:** {stats['completion_rate']}%\n\n"
        f"• **Active Habits:** {stats['total_habits']}\n"
        f"• **Longest Habit Streak:** {stats['longest_streak']} days 🔥\n"
        f"• **Avg Active Streak:** {stats['avg_active_streak']} days"
    )
    await update.message.reply_text(report, parse_mode="Markdown")
