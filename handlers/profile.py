from telegram import Update
from telegram.ext import ContextTypes
from services.database_service import DatabaseService

async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = (
        "⚙️ **User Settings**\n\n"
        "• Default Timezone: `UTC`\n"
        "• Notifications: `Enabled`\n"
        "• Daily Summary: `20:00`"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    msg = f"👤 **User Profile:** {user.full_name}\nID: `{user.id}`\nUsername: @{user.username or 'N/A'}"
    await update.message.reply_text(msg, parse_mode="Markdown")
