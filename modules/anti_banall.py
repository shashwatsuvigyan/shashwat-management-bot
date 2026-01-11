import time
import logging
from telegram import Update, ChatMember
from telegram.ext import ContextTypes, ChatMemberHandler
from telegram.error import BadRequest
from config import OWNER_ID

BAN_LIMIT = 5
TIME_WINDOW = 60
BAN_HISTORY = {}
logger = logging.getLogger(__name__)

async def watch_bans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if not result: return
    
    admin_user = result.from_user
    chat = update.effective_chat
    
    # Safety Check
    if not admin_user or admin_user.id == context.bot.id or admin_user.id == OWNER_ID:
        return

    if result.new_chat_member.status == ChatMember.BANNED:
        now = time.time()
        if admin_user.id not in BAN_HISTORY: BAN_HISTORY[admin_user.id] = []
        BAN_HISTORY[admin_user.id] = [t for t in BAN_HISTORY[admin_user.id] if now - t < TIME_WINDOW]
        BAN_HISTORY[admin_user.id].append(now)

        if len(BAN_HISTORY[admin_user.id]) >= BAN_LIMIT:
            try:
                # Demote
                await context.bot.promote_chat_member(
                    chat.id, admin_user.id, can_manage_chat=False, can_delete_messages=False, can_restrict_members=False
                )
                await context.bot.send_message(chat.id, f"🛡️ **Anti-Banall:** Demoted {admin_user.first_name} for mass banning.")
                BAN_HISTORY[admin_user.id] = []
            except Exception:
                pass

def register_handlers(application):
    application.add_handler(ChatMemberHandler(watch_bans, ChatMemberHandler.CHAT_MEMBER))
