from telegram import Update
from telegram.ext import ContextTypes

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "🛠 **Available Commands:**\n\n"
        "• `/start` - Launch menu & welcome screen\n"
        "• `/help` - List commands\n"
        "• `/about` - Bot specs & information\n"
        "• `/settings` - Manage preferences\n"
        "• `/profile` - Overview of productivity\n"
        "• `/tasks` - Manage daily tasks\n"
        "• `/habits` - Manage & check habits\n"
        "• `/stats` - View statistics & streaks\n"
        "• `/calendar` - Schedule & deadlines"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")
