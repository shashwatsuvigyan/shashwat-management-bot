from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from modules.admin import is_admin
from database.locks_db import lock_type, unlock_type, get_locked_types

async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    if not context.args: return await update.message.reply_text("Usage: /lock <sticker/photo/video>")

    t = context.args[0].lower()
    if t not in ['sticker', 'photo', 'video', 'document']:
         return await update.message.reply_text("Valid types: sticker, photo, video, document")

    await lock_type(update.effective_chat.id, t)
    await update.message.reply_text(f"🔒 Locked {t}.")

async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    if not context.args: return

    t = context.args[0].lower()
    await unlock_type(update.effective_chat.id, t)
    await update.message.reply_text(f"🔓 Unlocked {t}.")

async def enforcer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # OPTIMIZATION: Check DB locks first. 
    # Don't check is_admin() (API Call) unless necessary.
    
    chat_id = update.effective_chat.id
    locked_types = await get_locked_types(chat_id)
    
    if not locked_types: return # Nothing locked, exit fast
    
    msg = update.message
    should_del = False
    
    if "sticker" in locked_types and msg.sticker: should_del = True
    elif "photo" in locked_types and msg.photo: should_del = True
    elif "video" in locked_types and msg.video: should_del = True
    elif "document" in locked_types and msg.document: should_del = True
    
    if should_del:
        # Only NOW check if user is admin (Admins bypass locks)
        if await is_admin(update, context):
            return 
        
        try: 
            await msg.delete()
        except Exception: 
            pass

def register_handlers(application):
    application.add_handler(CommandHandler("lock", lock))
    application.add_handler(CommandHandler("unlock", unlock))
    # Group 1 ensures this runs alongside other handlers
    application.add_handler(MessageHandler(filters.ALL, enforcer), group=1)