from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        # Skip bots if needed, or welcome everyone
        if member.is_bot: continue
        await update.message.reply_text(f"Welcome {member.mention_html()}!", parse_mode='HTML')

def register_handlers(application):
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))