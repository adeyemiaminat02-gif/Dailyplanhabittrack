from telegram import Update
from telegram.ext import ContextTypes
from services.planner_service import PlannerService

async def task_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    user_id = update.effective_user.id
    
    if not args:
        tasks = await PlannerService.get_user_tasks(user_id, "today")
        if not tasks:
            await update.message.reply_text("📋 No tasks scheduled for today!")
            return
        msg = "📋 **Today's Tasks:**\n" + "\n".join([f"• [{t.id}] {t.title} ({t.priority.value})" for t in tasks])
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    subcommand = args[0].lower()
    if subcommand == "add" and len(args) > 1:
        title = " ".join(args[1:])
        task = await PlannerService.create_task(user_id=user_id, title=title)
        await update.message.reply_text(f"✅ Created Task `#{task.id}`: **{task.title}**", parse_mode="Markdown")
    elif subcommand == "done" and len(args) > 1:
        try:
            task_id = int(args[1])
            res = await PlannerService.complete_task(task_id, user_id)
            if res:
                await update.message.reply_text(f"🎉 Marked task `#{task_id}` as complete and archived!", parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ Task not found.")
        except ValueError:
            await update.message.reply_text("Invalid task ID.")
