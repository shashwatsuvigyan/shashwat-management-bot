from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from modules.admin import is_admin
from database.notes_db import save_note, get_note

async def save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    if not context.args or len(context.args) < 2:
        return await update.message.reply_text("Usage: /save <name> <content>")
    
    name = context.args[0].lower()
    content = ' '.join(context.args[1:])
    
    await save_note(update.effective_chat.id, name, content)
    await update.message.reply_text(f"📝 Note #{name} saved.")

async def get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text or not text.startswith("#"): return
    
    # Handle cases like "#rules" or "#rules please"
    try:
        name = text.split()[0][1:].lower()
        if not name: return
    except IndexError:
        return

    content = await get_note(update.effective_chat.id, name)
    if content:
        await update.message.reply_text(content)

def register_handlers(application):
    application.add_handler(CommandHandler("save", save))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get))