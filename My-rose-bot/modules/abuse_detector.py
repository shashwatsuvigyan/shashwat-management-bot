import re
from better_profanity import profanity
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from modules.admin import is_admin
from database.abuse_db import set_abuse_filter, is_abuse_filter_enabled, add_abuse_warn, reset_abuse_warns

# --- CONFIGURATION ---
# Load the English profanity filter
profanity.load_censor_words()

# --- CUSTOM LANGUAGE LISTS ---
# ⚠️ IMPORTANT: Populate these lists with the specific words you want to ban.
# I have provided placeholders. You must replace them with real words.
BAD_WORDS = {
    "hindi": ["badword_hindi_1", "badword_hindi_2"], 
    "russian": ["badword_russian_1", "badword_russian_2"],
    "arabic": ["badword_arabic_1", "badword_arabic_2"],
    "urdu": ["badword_urdu_1", "badword_urdu_2"],
    "bengali": ["badword_bengali_1", "badword_bengali_2"]
}

# Compile all custom words into a single list for fast checking
ALL_CUSTOM_BAD_WORDS = [word for lang in BAD_WORDS.values() for word in lang]

async def set_abuse_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usage: /antiobscene on/off"""
    if not await is_admin(update, context): return
    
    if not context.args:
        return await update.message.reply_text("Usage: /antiobscene <on/off>")
    
    state = context.args[0].lower()
    if state == "on":
        await set_abuse_filter(update.effective_chat.id, True)
        await update.message.reply_text("🤬 **Anti-Abuse Filter Enabled.**\nI will delete bad words and ban users after 3 strikes.")
    elif state == "off":
        await set_abuse_filter(update.effective_chat.id, False)
        await update.message.reply_text("✅ Anti-Abuse Filter Disabled.")

async def check_abuse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Scans message text for bad words."""
    msg = update.message
    chat = update.effective_chat
    user = update.effective_user

    # 1. Ignore if not text or private chat
    if not msg.text or chat.type == "private":
        return

    # 2. Check if enabled
    if not await is_abuse_filter_enabled(chat.id):
        return

    # 3. Skip Admins (Optional: Delete this block if you want to police admins too)
    try:
        member = await chat.get_member(user.id)
        if member.status in ['administrator', 'creator']:
            return
    except:
        pass

    text = msg.text.lower()
    is_abusive = False

    # 4. Check English (Using Library)
    if profanity.contains_profanity(text):
        is_abusive = True

    # 5. Check Other Languages (Using Custom List)
    if not is_abusive:
        for bad_word in ALL_CUSTOM_BAD_WORDS:
            # We use simple substring check. For strict matching, use regex.
            if bad_word in text:
                is_abusive = True
                break

    # 6. PUNISHMENT LOGIC
    if is_abusive:
        try:
            # Delete the message
            await msg.delete()
            
            # Issue Warning
            warns = await add_abuse_warn(chat.id, user.id)
            
            if warns >= 3:
                # BAN
                await context.bot.ban_chat_member(chat.id, user.id)
                await context.bot.send_message(
                    chat.id,
                    f"🚫 {user.mention_html()} has been **BANNED**.\n"
                    f"Reason: Abusive Language (3/3 Strikes).",
                    parse_mode="HTML"
                )
                await reset_abuse_warns(chat.id, user.id)
            else:
                # WARN
                alert = await context.bot.send_message(
                    chat.id,
                    f"⚠️ {user.mention_html()}, **Watch your language!**\n"
                    f"Abuse is not allowed here.\n"
                    f"Strike: {warns}/3",
                    parse_mode="HTML"
                )
                # Auto-delete the warning after 5 seconds to keep chat clean
                # from asyncio import sleep; await sleep(5); await alert.delete()

        except Exception as e:
            print(f"Abuse handler error: {e}")

def register_handlers(application):
    application.add_handler(CommandHandler("antiobscene", set_abuse_cmd))
    # Group 6 ensures it runs separately from other text handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_abuse), group=6)
