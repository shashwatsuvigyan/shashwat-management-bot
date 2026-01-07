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
BAD_WORDS = {
    # Copy this list into your modules/abuse_detector.py file

hindi_abuse_list = [
    "kutte ki zat", "कुत्ते की ज़ात",
    "suar ki aulad", "सूअर की औलाद",
    "suar ki zat", "सूअर की ज़ात",
    "gadhe ki aulad", "गधे की औलाद",
    "gadhe ki zat", "गधे की ज़ात",
    "bandar ki aulad", "बंदर की औलाद",
    "bandar ki zat", "बंदर की ज़ात",
    "bhains ki aulad", "भैंस की औलाद",
    "bhains ki zat", "भैंस की ज़ात",
    "ullu ki aulad", "उल्लू की औलाद",
    "ullu ki zat", "उल्लू की ज़ात",
    "lomdi ki aulad", "लोमड़ी की औलाद",
    "lomdi ki zat", "लोमड़ी की ज़ात",
    "bhed ki aulad", "भेड़ की औलाद",
    "bhed ki zat", "भेड़ की ज़ात",
    "bakri ki aulad", "बकरी की औलाद",
    "bakri ki zat", "बकरी की ज़ात",
    "billi ki aulad", "बिल्ली की औलाद",
    "billi ki zat", "बिल्ली की ज़ात",
    "mendhak ki aulad", "मेंढक की औलाद",
    "mendhak ki zat", "मेंढक की ज़ात",
    "badir", "बदीर",
    "badirchand", "बदीरचंद",
    "bakland", "बकलैंड", "बकलंड",
    "bhandwa", "भंडवा",
    "bhadwa", "भड़वा",
    "chinaal", "चिनाल", "छनाल",
    "chutiya", "चूतिया", "चुतिया",
    "ghasti", "घसटी", "घसति",
    "ghassad", "घसड़", "घस्सड़",
    "harami", "हरामी",
    "haram zada", "हरामज़ादा", "हरामजादा",
    "hijda", "हिजड़ा",
    "hijra", "हिजड़ा", "हिजरा",
    "tatti", "टट्टी",
    "chod", "चोद",
    "land", "लंड",
    "lode", "लोडे",
    "takke", "टक्के",
    "chakka", "छक्का",
    "faggot",
    "tatte", "टट्टे",
    "raand", "रांड",
    "randhwa", "रंढवा",
    "jigolo", "जिगोलो",
    "randi", "रंडी",
    "chut", "चूत",
    "bund", "बंड",
    "gaandu", "गांडू",
    "gandi", "गांडी",
    "bhosdi wala", "भोसड़ी वाला",
    "bhonsri wala", "भोंसड़ी वाला",
    "bhosri wala", "भोसरी वाला",
    "boobley", "बूबले",
    "chuchi", "चुची",
    "chuuche", "चूचे",
    "chuchiyan", "चूचियां",
    "chut marike", "चूत मार के",
    "land marike", "लंड मार के",
    "gand mari ke", "गांड मारी के",
    "chodu", "चोदू",
    "lavda", "लौड़ा", "लवड़ा",
    "lawda", "लौंडा",
    "loda", "लोडा",
    "lund", "लंड",
    "muth marna", "मुठ मारना",
    "muthi", "मुठी",
    "mutthal", "मुठल",
    "baable", "बाबले",
    "bur", "बुर",
    "chodna", "चोदना",
    "chudna", "चुदना",
    "chud", "चुद",
    "buuble", "बूबले",
    "bhadwe", "भड़वे",
    "bhadwon", "भड़वों",
    "bhadwi", "भड़वी",
    "bhadwapanti", "भड़वापंती",
    "chodela", "चोदेला",
    "marana", "मारना",
    "marani", "मारनी",
    "marane", "मारने",
    "gandphatu", "गांडफटू", "गांड फटू",
    "gandphati", "गांडफटी", "गांड फटी",
    "gandphata", "गांडफटा", "गांड फटा",
    "gandphaton", "गांडफटों", "गांड फटों",
    "gaandmasti", "गांडमस्ती", "गांड मस्ती",
    "gand marna", "गांड मारना", "गांडमरना",
    "gand maru", "गांड मारू", "गांडमरू",
    "gand mari", "गांड मारी", "गांडमारी",
    "gand marana", "गांड माराना", "गांडमराना",
    "jhaant", "झाँट",
    "randibazar", "रंडीबाज़ार", "रांडिबाजार",
    "chodo", "चोदो",
    "chodi", "चोदी",
    "chodne", "चोदने",
    "chodva", "चोदवा",
    "chudo", "चुदो",
    "chudi", "चुदी",
    "chudne", "चुदने",
    "chudva", "चुदवा",
    "chodai", "चोदाई",
    "chuda", "चुदा",
    "chudai", "चुदाई",
    "chudvana", "चुदवाना",
    "haramia", "हरामिया",
    "haramzadi", "हरामज़ादी",
    "haramkhor", "हरामख़ोर",
    "kamina", "कमीना",
    "kamini", "कमीनी",
    "bhosdi", "भोसड़ी",
    "bhosdike", "भोसड़ीके",
    "bhandi", "भंडी",
    "rand", "रांड",
    "randwa", "रांडवा",
    "hijade", "हिजड़े",
    "gandu", "गंडू",
    "lundwa", "लंडवा",
    "chutmar", "चूतमार",
    "chutiyapa", "चूतियापा"
], 
    "russian": ["badword_russian_1", "badword_russian_2"],
    "arabic": ["badword_arabic_1", "badword_arabic_2"],
    "urdu": ["badword_urdu_1", "badword_urdu_2"],
    "bengali": ["badword_bengali_1", "badword_bengali_2"]
}

# Compile all custom words into a single list for fast checking
# FIX: Convert to lowercase to ensure matching works correctly
ALL_CUSTOM_BAD_WORDS = [word.lower() for lang in BAD_WORDS.values() for word in lang]

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

    # 3. Skip Admins
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
            # Check if the bad word is in the text
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
                # FIX: Strings are now concatenated properly with (+) or implicit joining
                await context.bot.send_message(
                    chat.id,
                    f"🚫 {user.mention_html()} has been **BANNED**.\n"
                    f"Reason: Abusive Language (3/3 Strikes).",
                    parse_mode="HTML"
                )
                await reset_abuse_warns(chat.id, user.id)
            else:
                # WARN
                # FIX: Removed commas between f-strings so they combine into one message
                await context.bot.send_message(
                    chat.id,
                    f"⚠️ {user.mention_html()}, **Watch your language!**\n"
                    f"Abuse is not allowed here.\n"
                    f"Strike: {warns}/3",
                    parse_mode="HTML"
                )

        except Exception as e:
            print(f"Abuse handler error: {e}")

def register_handlers(application):
    application.add_handler(CommandHandler("antiobscene", set_abuse_cmd))
    # Group 6 ensures it runs separately from other text handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_abuse), group=6)
