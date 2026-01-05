import logging
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, CommandHandler
from telegram.error import BadRequest

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Helper to check admin status with error handling."""
    user = update.effective_user
    chat = update.effective_chat
    
    # 1. Check if user is anonymous admin (Telegram feature)
    if user.id == 1087968824: 
        return True
        
    # 2. Check Member Status
    try:
        member = await chat.get_member(user.id)
        return member.status in ['administrator', 'creator']
    except BadRequest:
        # If user left or cannot be found
        return False

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a user to ban them.")
    
    user_id = update.message.reply_to_message.from_user.id
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text("🔨 Banned.")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to ban: {e}")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    if not update.message.reply_to_message: return
    
    user_id = update.message.reply_to_message.from_user.id
    try:
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text("✅ Unbanned.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    if not update.message.reply_to_message: return
    
    user_id = update.message.reply_to_message.from_user.id
    permissions = ChatPermissions(can_send_messages=False)
    try:
        await context.bot.restrict_chat_member(update.effective_chat.id, user_id, permissions)
        await update.message.reply_text("🤐 Muted.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

def register_handlers(application):
    application.add_handler(CommandHandler("ban", ban))
    application.add_handler(CommandHandler("unban", unban))
    application.add_handler(CommandHandler("mute", mute))