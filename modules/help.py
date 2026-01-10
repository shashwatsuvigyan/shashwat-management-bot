from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
🌹 **MyRoseBot Help** 🌹

**Admin:**
`/ban`, `/unban`, `/mute` (Reply to user)

**Warnings:**
`/warn`, `/resetwarn` (3 Warnings = Ban)

**Locks:**
`/lock <type>`, `/unlock <type>`
(Types: sticker, photo, video, document)

**Bio Protection:**
`/biolock on/off`

**Edit Guardian:**
`/editguardian on/off`
    """
    await update.effective_message.reply_text(text, parse_mode='Markdown')

def register_handlers(application):
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("start", help_command))
