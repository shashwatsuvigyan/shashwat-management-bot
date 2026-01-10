from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from modules.admin import is_admin

async def purge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to start of purge.")
    
    msg_id = update.message.reply_to_message.message_id
    curr_id = update.message.message_id
    chat_id = update.effective_chat.id
    
    # Generate list of IDs
    ids = list(range(msg_id, curr_id + 1))
    
    # Telegram bulk delete limit is 100
    try:
        for i in range(0, len(ids), 100):
            chunk = ids[i:i+100]
            await context.bot.delete_messages(chat_id, chunk)
            
        confirm = await update.message.reply_text("🗑️ Purged.")
        # Optional: Auto-delete the confirmation message?
        # await asyncio.sleep(3); await confirm.delete()
        
    except Exception as e:
        if "Message to delete not found" in str(e):
             await update.message.reply_text("❌ Some messages were too old to delete (>48h).")
        else:
             await update.message.reply_text(f"❌ Error: {e}")

def register_handlers(application):
    application.add_handler(CommandHandler("purge", purge))