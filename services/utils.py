from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📋 Add Task", callback_data="task_add"), InlineKeyboardButton("🔍 View Tasks", callback_data="task_view")],
        [InlineKeyboardButton("⚡ Add Habit", callback_data="habit_add"), InlineKeyboardButton("🔥 Complete Habit", callback_data="habit_complete")],
        [InlineKeyboardButton("📊 Statistics", callback_data="show_stats"), InlineKeyboardButton("📅 Calendar", callback_data="show_calendar")],
        [InlineKeyboardButton("⏰ Reminders", callback_data="show_reminders"), InlineKeyboardButton("⚙️ Settings", callback_data="show_settings")]
    ]
    return InlineKeyboardMarkup(keyboard)
