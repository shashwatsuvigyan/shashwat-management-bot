import aiohttp
import os
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from modules.admin import is_admin
from database.media_db import set_delete_timer, get_delete_timer
from config import NSFW_API_USER, NSFW_API_SECRET

# --- CONFIGURATION ---
# We use Sightengine for this example (High accuracy, Good Free Tier)
API_ENDPOINT = "https://api.sightengine.com/1.0/check.json"

# --- 1. AUTO-DELETE LOGIC ---

async def set_autodelete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: /setautodelete <seconds> (0 to disable)"""
    if not await is_admin(update, context): return
    
    if not context.args:
        return await update.message.reply_text("Usage: /setautodelete <seconds>\nExample: /setautodelete 60")
    
    try:
        seconds = int(context.args[0])
        if seconds < 0: raise ValueError
    except ValueError:
        return await update.message.reply_text("❌ Please enter a valid number of seconds.")

    await set_delete_timer(update.effective_chat.id, seconds)
    
    if seconds == 0:
        await update.message.reply_text("✅ Auto-delete disabled.")
    else:
        await update.message.reply_text(f"✅ Media will now self-destruct after {seconds} seconds.")

async def scheduled_delete(context: ContextTypes.DEFAULT_TYPE):
    """The job that runs when the timer expires."""
    job = context.job
    try:
        # Delete the message
        await context.bot.delete_message(chat_id=job.chat_id, message_id=job.data)
    except Exception:
        # Message might already be deleted
        pass

# --- 2. NSFW DETECTION LOGIC ---

async def check_image_nsfw(file_url: str) -> bool:
    """
    Sends image URL to Sightengine API. 
    Returns True if Nudity/Porn/Hentai is detected.
    """
    if not NSFW_API_USER or not NSFW_API_SECRET:
        return False # Fail safe if no key configured

    params = {
        'models': 'nudity,wad', # 'wad' = weapons/alcohol/drugs (optional)
        'api_user': NSFW_API_USER,
        'api_secret': NSFW_API_SECRET,
        'url': file_url
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_ENDPOINT, params=params) as resp:
                data = await resp.json()
                
                # Analyze Response
                if data['status'] == 'success':
                    nudity = data['nudity']
                    # Thresholds (Adjust as needed)
                    if (nudity['raw'] > 0.8 or 
                        nudity['partial'] > 0.9 or 
                        nudity['safe'] < 0.1):
                        return True
    except Exception as e:
        print(f"NSFW Check Failed: {e}")
    
    return False

# --- 3. MAIN EVENT WATCHER ---

async def media_watcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Runs on EVERY Photo/Video sent."""
    chat_id = update.effective_chat.id
    msg = update.message
    
    # A. NSFW CHECK (Photos Only)
    # We check NSFW *before* scheduling auto-delete.
    if msg.photo:
        # Get the largest version of the photo
        photo_file = await msg.photo[-1].get_file()
        is_nsfw = await check_image_nsfw(photo_file.file_path)
        
        if is_nsfw:
            try:
                await msg.delete()
                await context.bot.send_message(
                    chat_id, 
                    f"🔞 **NSFW Detected!**\nUser {msg.from_user.mention_html()} posted prohibited content.",
                    parse_mode='HTML'
                )
                # Optional: Ban the user
                # await context.bot.ban_chat_member(chat_id, msg.from_user.id)
                return # Stop processing (it's deleted)
            except Exception:
                pass

    # B. AUTO-DELETE CHECK
    # Get timer from DB
    timer = await get_delete_timer(chat_id)
    
    if timer > 0:
        # Schedule deletion
        context.job_queue.run_once(
            scheduled_delete, 
            timer, 
            chat_id=chat_id, 
            data=msg.message_id
        )

def register_handlers(application):
    application.add_handler(CommandHandler("setautodelete", set_autodelete))
    
    # Watch Photos, Videos, Documents
    application.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.Document.IMAGE, 
        media_watcher
    ), group=3)
