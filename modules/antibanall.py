import time
import logging
from telegram import Update, ChatMember
from telegram.ext import ContextTypes, ChatMemberHandler
from telegram.error import BadRequest

# --- CONFIGURATION ---
BAN_LIMIT = 5        # Max bans allowed
TIME_WINDOW = 60     # In seconds (e.g., 5 bans in 60 seconds)

# STORAGE: {admin_id: [timestamp1, timestamp2, ...]}
BAN_HISTORY = {}

# LOGGER
logger = logging.getLogger(__name__)

async def watch_bans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Runs automatically whenever a user is BANNED or KICKED.
    Checks if the admin is banning too fast.
    """
    # 1. extract the event
    result = update.chat_member
    if not result:
        return

    # 2. Identify the Admin who did the banning
    admin_user = result.from_user
    chat = update.effective_chat
    
    # Ignore actions by the Bot itself or the Owner
    from config import OWNER_ID
    if admin_user.id == context.bot.id or admin_user.id == OWNER_ID:
        return

    # 3. Check if this event is actually a "Ban"
    # Logic: Status changed from (Member/Admin/Restricted) -> BANNED
    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status
    
    was_member = old_status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.RESTRICTED]
    is_now_banned = new_status == ChatMember.BANNED

    if not (was_member and is_now_banned):
        return # Not a ban event, ignore it.

    # 4. Record the Ban
    now = time.time()
    if admin_user.id not in BAN_HISTORY:
        BAN_HISTORY[admin_user.id] = []

    # Clean old history (older than 60s)
    BAN_HISTORY[admin_user.id] = [t for t in BAN_HISTORY[admin_user.id] if now - t < TIME_WINDOW]
    
    # Add new ban
    BAN_HISTORY[admin_user.id].append(now)

    # 5. Check Threshold
    if len(BAN_HISTORY[admin_user.id]) >= BAN_LIMIT:
        logger.warning(f"🚨 Mass Ban Detected! Admin: {admin_user.first_name} ({admin_user.id})")
        
        try:
            # 6. DEMOTE THE ROGUE ADMIN
            # Setting all permissions to False
            await context.bot.promote_chat_member(
                chat_id=chat.id,
                user_id=admin_user.id,
                can_manage_chat=False,
                can_delete_messages=False,
                can_manage_video_chats=False,
                can_restrict_members=False,
                can_promote_members=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
                can_post_messages=False,
                can_edit_messages=False,
                can_manage_topics=False
            )

            # 7. Alert the Group
            await context.bot.send_message(
                chat_id=chat.id,
                text=(
                    f"🛡️ **Anti-Banall System Triggered**\n\n"
                    f"👮‍♂️ **Admin:** {admin_user.mention_html()}\n"
                    f"⚠️ **Action:** Mass Banning detected ({len(BAN_HISTORY[admin_user.id])} bans in {TIME_WINDOW}s)\n"
                    f"🔨 **Result:** Admin privileges REVOKED."
                ),
                parse_mode="HTML"
            )
            
            # Reset their history so we don't spam alerts
            BAN_HISTORY[admin_user.id] = []

        except BadRequest as e:
            logger.error(f"Failed to demote admin: {e}")
            await context.bot.send_message(chat_id=chat.id, text="⚠️ I tried to stop the mass ban, but I don't have permission to demote that admin!")

def register_handlers(application):
    # We use ChatMemberHandler to watch for status changes (Bans)
    # ChatMemberHandler.CHAT_MEMBER watches for changes in OTHER users
    application.add_handler(ChatMemberHandler(watch_bans, ChatMemberHandler.CHAT_MEMBER))
