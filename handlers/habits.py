from telegram import Update
from telegram.ext import ContextTypes
from services.habit_service import HabitService

async def habit_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    user_id = update.effective_user.id
    
    if not args:
        habits = await HabitService.get_user_habits(user_id)
        if not habits:
            await update.message.reply_text("⚡ No active habits found. Create one with `/habit add <name>`!")
            return
        msg = "⚡ **Your Active Habits:**\n" + "\n".join([f"• [{h.id}] {h.name} (🔥 Streak: {h.current_streak})" for h in habits])
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    subcommand = args[0].lower()
    if subcommand == "add" and len(args) > 1:
        name = " ".join(args[1:])
        habit = await HabitService.create_habit(user_id=user_id, name=name)
        await update.message.reply_text(f"🔥 Started habit `#{habit.id}`: **{habit.name}**", parse_mode="Markdown")
    elif subcommand == "check" and len(args) > 1:
        try:
            habit_id = int(args[1])
            habit = await HabitService.mark_habit_complete(habit_id, user_id)
            if habit:
                await update.message.reply_text(f"🔥 Awesome! Habit **{habit.name}** completed!\nCurrent Streak: **{habit.current_streak}** days!", parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ Habit not found.")
        except ValueError:
            await update.message.reply_text("Invalid habit ID.")
