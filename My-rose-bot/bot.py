from keep_alive import keep_alive
keep_alive()
import logging
import os
import importlib
from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def load_modules(application):
    """Dynamically loads all modules from the 'modules' folder."""
    # Ensure we are looking at the correct directory relative to this file
    modules_path = os.path.join(os.path.dirname(__file__), 'modules')
    
    # Get list of .py files (excluding __init__.py)
    module_files = [
        f[:-3] for f in os.listdir(modules_path)
        if f.endswith('.py') and f != '__init__.py'
    ]

    for module_name in module_files:
        try:
            # Import modules.admin, modules.notes, etc.
            module = importlib.import_module(f'modules.{module_name}')
            
            # Check for the setup function
            if hasattr(module, 'register_handlers'):
                module.register_handlers(application)
                logger.info(f"✅ Loaded module: {module_name}")
            else:
                logger.warning(f"⚠️ Skipped {module_name}: Missing 'register_handlers'")
        except Exception as e:
            logger.error(f"❌ Failed to load {module_name}: {e}")

if __name__ == '__main__':
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("⚠️ BOT_TOKEN is not set in config.py or Environment Variables!")
        exit(1)

    print("🧱 Building Application...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    print("🔌 Loading Modules...")
    load_modules(application)

    print("🚀 Bot is running...")
    application.run_polling()