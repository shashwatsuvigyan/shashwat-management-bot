from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from modules.admin import is_admin
from database.warns_db import add_warn, reset_warns

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to a user to warn.")

    user = update.message.reply_to_message.from_user
    # Prevent warning admins
    chat = update.effective_chat
    target_member = await chat.get_member(user.id)
    if target_member.status in ['administrator', 'creator']:
         return await update.message.reply_text("❌ I cannot warn admins.")

    chat_id = update.effective_chat.id
    count = await add_warn(chat_id, user.id)
    
    if count >= 3:
        await reset_warns(chat_id, user.id)
        try:
            await context.bot.ban_chat_member(chat_id, user.id)
            await update.message.reply_text(f"🚫 {user.first_name} banned (3/3 warnings).")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Limit reached, but failed to ban: {e}")
    else:
        await update.message.reply_text(f"⚠️ Warned {user.first_name} ({count}/3).")

async def reset_warning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    if not update.message.reply_to_message: return

    user = update.message.reply_to_message.from_user
    await reset_warns(update.effective_chat.id, user.id)
    await update.message.reply_text(f"✅ Warnings reset for {user.first_name}.")

def register_handlers(application):
    application.add_handler(CommandHandler("warn", warn))
    application.add_handler(CommandHandler("resetwarn", reset_warning))