from better_profanity import profanity
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from modules.admin import is_admin
from database.abuse_db import set_abuse_filter, is_abuse_filter_enabled, add_abuse_warn

profanity.load_censor_words()

BAD_WORDS = {
    "hindi": ["kutte", "kutta", "kamina", "harami", "bhosdike", "chutiya", "gandu", "land", "loda"],
    "english": ["fuck", "bitch", "bastard"]
}
ALL_CUSTOM_BAD_WORDS = [w.lower() for lang in BAD_WORDS.values() for w in lang]

async def set_abuse_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    if not context.args: return await update.message.reply_text("Usage: /antiobscene <on/off>")
    
    state = context.args[0].lower() == "on"
    await set_abuse_filter(update.effective_chat.id, state)
    await update.message.reply_text(f"Abuse filter: {'ON' if state else 'OFF'}")

async def check_abuse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text or update.effective_chat.type == "private": return
    if not await is_abuse_filter_enabled(update.effective_chat.id): return

    try:
        user = await update.effective_chat.get_member(update.effective_user.id)
        if user.status in ['administrator', 'creator']: return
    except: pass

    text = msg.text.lower()
    if profanity.contains_profanity(text) or any(w in text for w in ALL_CUSTOM_BAD_WORDS):
        try:
            await msg.delete()
            await context.bot.send_message(update.effective_chat.id, f"⚠️ Language! {update.effective_user.mention_html()}", parse_mode="HTML")
        except: pass

def register_handlers(application):
    application.add_handler(CommandHandler("antiobscene", set_abuse_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_abuse), group=6)
