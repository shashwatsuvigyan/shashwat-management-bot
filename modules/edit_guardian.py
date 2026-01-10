from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, TypeHandler
from modules.admin import is_admin
from database.edit_db import set_edit_guardian, is_edit_guardian_enabled

# --- CONFIGURATION ---
# Admins are usually immune to this check.
# If you want to check admins too, remove the is_admin check in the watcher.

# --- 1. COMMANDS (Toggle ON/OFF) ---

async def set_edit_guardian_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usage: /editguardian on/off"""
    if not await is_admin(update, context): return
    
    if not context.args:
        return await update.message.reply_text("Usage: /editguardian <on/off>")
    
    state = context.args[0].lower()
    if state == "on":
        await set_edit_guardian(update.effective_chat.id, True)
        await update.message.reply_text("🛡️ **Edit Guardian Enabled.**\nAny edited message by non-admins will be deleted immediately.")
    elif state == "off":
        await set_edit_guardian(update.effective_chat.id, False)
        await update.message.reply_text("✅ Edit Guardian Disabled.")
    else:
        await update.message.reply_text("Usage: /editguardian <on/off>")

# --- 2. THE WATCHER (Detects Edits) ---

async def edit_watcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Runs on EVERY update to check if it contains an 'edited_message'.
    """
    # 1. Check if this is actually an edited message
    if not update.edited_message:
        return

    msg = update.edited_message
    chat = update.effective_chat
    user = msg.from_user

    # 2. Ignore Private Chats and Channels
    if chat.type == "private":
        return

    # 3. Check if Guardian is Enabled in DB
    if not await is_edit_guardian_enabled(chat.id):
        return

    # 4. Check Admin Immunity
    # (We re-use the is_admin logic, but we must manually construct a dummy 'update' 
    # or just check privileges directly because 'is_admin' expects a standard message)
    try:
        member = await chat.get_member(user.id)
        if member.status in ['administrator', 'creator']:
            return # Admins are allowed to edit
    except Exception:
        pass

    # 5. EXECUTE: Delete the Edited Message
    try:
        await msg.delete()
        
        # 6. Warn the user (Optional: Delete warning after 5s to reduce spam)
        warning = await context.bot.send_message(
            chat_id=chat.id,
            text=f"🚫 {user.mention_html()}, **editing messages is not allowed** in this group.",
            parse_mode="HTML"
        )
        # Optional cleanup
        # from asyncio import sleep
        # await sleep(5)
        # await warning.delete()
        
    except Exception as e:
        print(f"Failed to delete edited message: {e}")

def register_handlers(application):
    # Command to toggle
    application.add_handler(CommandHandler("editguardian", set_edit_guardian_cmd))
    
    # TypeHandler catches ALL updates, including edits
    application.add_handler(TypeHandler(Update, edit_watcher), group=4)
