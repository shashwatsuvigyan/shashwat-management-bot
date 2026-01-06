import re
import time
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from modules.admin import is_admin
from database.bio_db import set_bio_lock, is_bio_lock_enabled, add_bio_warn, reset_bio_warns

# --- CONFIGURATION ---
URL_PATTERN = r"(https?://|www\.|t\.me/|bit\.ly/|discord\.gg/)"
CHECK_COOLDOWN = 3600  # Check the same user only once every 1 hour (to save API limits)

# In-Memory Cache to prevent spamming Telegram API
# Format: {user_id: last_check_timestamp}
USER_CACHE = {}

async def set_biolock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usage: /biolock on/off"""
    if not await is_admin(update, context): return
    
    if not context.args:
        return await update.message.reply_text("Usage: /biolock <on/off>")
    
    state = context.args[0].lower()
    if state == "on":
        await set_bio_lock(update.effective_chat.id, True)
        await update.message.reply_text("🧬 **Bio Link Restrictor Enabled.**\nI will check member bios for links and ban after 5 warnings.")
    elif state == "off":
        await set_bio_lock(update.effective_chat.id, False)
        await update.message.reply_text("✅ Bio Link Restrictor Disabled.")
    else:
        await update.message.reply_text("Usage: /biolock <on/off>")

async def check_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Scans user bio for links."""
    chat = update.effective_chat
    user = update.effective_user
    
    # 1. Ignore Private Chats or Bots
    if chat.type == "private" or user.is_bot:
        return

    # 2. Check if Feature is Enabled
    if not await is_bio_lock_enabled(chat.id):
        return

    # 3. Cooldown Check (Optimization)
    # If we checked this user recently, skip them to avoid 'FloodWait' errors
    last_check = USER_CACHE.get(user.id, 0)
    if time.time() - last_check < CHECK_COOLDOWN:
        return
    
    USER_CACHE[user.id] = time.time() # Update cache

    # 4. Fetch User Full Info (API Call)
    # We must use get_chat because the standard 'user' object doesn't have the bio.
    try:
        full_user = await context.bot.get_chat(user.id)
        bio = full_user.bio
    except Exception:
        return # Failed to fetch bio (User might be private)

    if not bio:
        return # No bio, they are safe

    # 5. Regex Check for Links
    if re.search(URL_PATTERN, bio, flags=re.IGNORECASE):
        # LINK FOUND!
        warn_count = await add_bio_warn(chat.id, user.id)
        
        if warn_count >= 5:
            # BAN HAMMER
            try:
                await context.bot.ban_chat_member(chat.id, user.id)
                await context.bot.send_message(
                    chat.id,
                    f"🚫 {user.mention_html()} has been **BANNED**.\n"
                    f"Reason: Persistently keeping links in bio ({warn_count}/5 warnings).",
                    parse_mode="HTML"
                )
                await reset_bio_warns(chat.id, user.id)
            except Exception as e:
                await context.bot.send_message(chat.id, f"⚠️ Tried to ban {user.first_name} for bio link, but failed: {e}")
        else:
            # WARNING
            await update.message.reply_text(
                f"⚠️ {user.mention_html()}, **Links in Bio are NOT allowed!**\n"
                f"Please remove the link from your profile bio immediately.\n"
                f"Warnings: {warn_count}/5",
                parse_mode="HTML"
            )

def register_handlers(application):
    # Command
    application.add_handler(CommandHandler("biolock", set_biolock_cmd))
    
    # Check on Join
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, check_bio), group=5)
    
    # Check on Message (Protected by Cooldown)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_bio), group=5)
