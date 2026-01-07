import logging
import os
import importlib
from telegram import Update
from telegram.ext import ApplicationBuilder, Defaults
from telegram.request import HTTPXRequest  # <--- Import this
from config import BOT_TOKEN
from keep_alive import keep_alive

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def load_modules(application):
    """Dynamically loads all modules from the 'modules' folder."""
    modules_path = os.path.join(os.path.dirname(__file__), 'modules')
    
    if os.path.exists(modules_path):
        module_files = [
            f[:-3] for f in os.listdir(modules_path)
            if f.endswith('.py') and f != '__init__.py'
        ]
    else:
        logger.error(f"❌ Modules directory not found at: {modules_path}")
        return

    for module_name in module_files:
        try:
            module = importlib.import_module(f'modules.{module_name}')
            if hasattr(module, 'register_handlers'):
                module.register_handlers(application)
                logger.info(f"✅ Loaded module: {module_name}")
            else:
                logger.warning(f"⚠️ Skipped {module_name}: Missing 'register_handlers'")
        except Exception as e:
            logger.error(f"❌ Failed to load {module_name}: {e}")

if __name__ == '__main__':
    # 1. Start the Background Web Server (Keep-Alive)
    keep_alive()

    # 2. Check Configuration
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("⚠️ BOT_TOKEN is not set in config.py or Environment Variables!")
        exit(1)

    print("🧱 Building Application...")

    # --- FIX START: Configure Timeouts Here ---
    trequest = HTTPXRequest(
        connection_pool_size=8,
        read_timeout=30.0,      # Wait 30s for data
        write_timeout=30.0,
        connect_timeout=30.0,   # Wait 30s to connect
        pool_timeout=30.0       # Wait 30s for pool slots
    )
    
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .request(trequest) # Pass the request settings here
        .build()
    )
    # --- FIX END ---

    print("🔌 Loading Modules...")
    load_modules(application)

    print("🚀 Bot is running with Anti-Ban & Polling Fixes Enabled...")
    
    # 3. Start Polling
    # Remove timeout arguments from here; they are now in 'trequest'
    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )
