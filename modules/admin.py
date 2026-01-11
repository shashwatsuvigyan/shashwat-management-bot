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

async def get_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Rose Bot Logic:
    1. Check if an argument is provided (Username or ID).
    2. If no argument, check if it's a reply.
    Returns: (user_id, first_name, reason_string) or (None, None, None)
    """
    msg = update.effective_message
    args = context.args
    user_id = None
    first_name = "User"
    reason = ""

    # 1. Check Arguments (Priority)
    if args:
        # Check if the first argument is a user (ID or @username)
        potential_user = args[0]
        
        # A. By Username
        if potential_user.startswith("@"):
            try:
                # Resolve username to object
                user_obj = await context.bot.get_chat(potential_user)
                user_id = user_obj.id
                first_name = user_obj.first_name or potential_user
                reason = " ".join(args[1:]) # Rest is reason
            except BadRequest:
                await msg.reply_text("❌ I can't find that user. Have they interacted with me?")
                return None, None, None
        
        # B. By ID
        elif potential_user.isdigit():
            try:
                user_id = int(potential_user)
                try:
                    # Try to get name if possible
                    user_obj = await context.bot.get_chat(user_id)
                    first_name = user_obj.first_name
                except:
                    first_name = "Unknown"
                reason = " ".join(args[1:])
            except ValueError:
                pass # Not an ID

    # 2. Check Reply (Fallback)
    if not user_id and msg.reply_to_message:
        user_id = msg.reply_to_message.from_user.id
        first_name = msg.reply_to_message.from_user.first_name
        # If we used reply, ALL args are the reason
        reason = " ".join(args)

    return user_id, first_name, reason

# --- COMMANDS ---

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bans a user."""
    msg = update.effective_message
    if not await is_admin(update, context): return
    
    user_id, first_name, reason = await get_target(update, context)
    
    if not user_id:
        return await msg.reply_text("❌ Reply to a user or specify a username (@name) to ban.")

    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        text = f"🔨 Banned {first_name}."
        if reason: text += f"\nReason: {reason}"
        await msg.reply_text(text)
    except Exception as e:
        await msg.reply_text(f"❌ Failed: {e}")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unbans a user."""
    msg = update.effective_message
    if not await is_admin(update, context): return
    
    user_id, first_name, reason = await get_target(update, context)
    
    if not user_id:
        return await msg.reply_text("❌ Reply to a user or specify a username to unban.")
    
    try:
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)
        text = f"✅ Unbanned {first_name}."
        if reason: text += f"\nReason: {reason}"
        await msg.reply_text(text)
    except Exception as e:
        await msg.reply_text(f"❌ Error: {e}")

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kicks a user (Ban then Unban)."""
    msg = update.effective_message
    if not await is_admin(update, context): return
    
    user_id, first_name, reason = await get_target(update, context)
    
    if not user_id:
        return await msg.reply_text("❌ Reply to a user or specify a username to kick.")
    
    try:
        # Ban then Unban immediately
        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)
        
        text = f"👞 Kicked {first_name}."
        if reason: text += f"\nReason: {reason}"
        await msg.reply_text(text)
    except Exception as e:
        await msg.reply_text(f"❌ Error: {e}")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mutes a user."""
    msg = update.effective_message
    if not await is_admin(update, context): return
    
    user_id, first_name, reason = await get_target(update, context)
    
    if not user_id:
        return await msg.reply_text("❌ Reply to a user or specify a username to mute.")
    
    permissions = ChatPermissions(can_send_messages=False)
    
    try:
        await context.bot.restrict_chat_member(update.effective_chat.id, user_id, permissions)
        text = f"🤐 Muted {first_name}."
        if reason: text += f"\nReason: {reason}"
        await msg.reply_text(text)
    except Exception as e:
        await msg.reply_text(f"❌ Error: {e}")

def register_handlers(application):
    application.add_handler(CommandHandler("ban", ban))
    application.add_handler(CommandHandler("unban", unban))
    application.add_handler(CommandHandler("kick", kick))
    application.add_handler(CommandHandler("mute", mute))
