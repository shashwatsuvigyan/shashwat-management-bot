import logging
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, CommandHandler
from telegram.error import BadRequest

# Logger
logger = logging.getLogger(__name__)

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Helper to check admin status."""
    user = update.effective_user
    chat = update.effective_chat
    
    if not user or not chat: return False

    # 1. Anonymous Admin Check
    if user.id == 1087968824: 
        return True
        
    # 2. Member Status Check
    try:
        member = await chat.get_member(user.id)
        return member.status in ['administrator', 'creator']
    except BadRequest:
        return False

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bans a user."""
    msg = update.effective_message
    if not await is_admin(update, context): return
    
    if not msg.reply_to_message:
        return await msg.reply_text("❌ Reply to a user to ban them.")
    
    user_id = msg.reply_to_message.from_user.id
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        await msg.reply_text("🔨 **Banned.**", parse_mode="Markdown")
    except Exception as e:
        await msg.reply_text(f"❌ Failed: {e}")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unbans a user."""
    msg = update.effective_message
    if not await is_admin(update, context): return
    
    if not msg.reply_to_message:
        return await msg.reply_text("❌ Reply to a user to unban.")
    
    user_id = msg.reply_to_message.from_user.id
    try:
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)
        await msg.reply_text("✅ **Unbanned.**", parse_mode="Markdown")
    except Exception as e:
        await msg.reply_text(f"❌ Error: {e}")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mutes a user."""
    msg = update.effective_message
    if not await is_admin(update, context): return
    
    if not msg.reply_to_message:
        return await msg.reply_text("❌ Reply to a user to mute.")
    
    user_id = msg.reply_to_message.from_user.id
    permissions = ChatPermissions(can_send_messages=False)
    
    try:
        await context.bot.restrict_chat_member(update.effective_chat.id, user_id, permissions)
        await msg.reply_text("🤐 **Muted.**", parse_mode="Markdown")
    except Exception as e:
        await msg.reply_text(f"❌ Error: {e}")

def register_handlers(application):
    application.add_handler(CommandHandler("ban", ban))
    application.add_handler(CommandHandler("unban", unban))
    application.add_handler(CommandHandler("mute", mute))
