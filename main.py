import asyncio
import os
import logging
import importlib
import functions_framework
from telegram import Update
from telegram.ext import ApplicationBuilder, Application
from telegram.request import HTTPXRequest

# --- LOGGING SETUP ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- MODULE LOADER ---
def load_modules(application: Application):
    """Dynamically loads all modules from the 'modules' folder."""
    modules_path = os.path.join(os.path.dirname(__file__), 'modules')
    
    if not os.path.exists(modules_path):
        logger.error(f"❌ CRITICAL: Modules directory not found at: {modules_path}")
        return

    logger.info(f"📂 Scanning modules in: {modules_path}")
    module_files = [
        f[:-3] for f in os.listdir(modules_path)
        if f.endswith('.py') and f != '__init__.py'
    ]

    for module_name in module_files:
        try:
            module = importlib.import_module(f'modules.{module_name}')
            if hasattr(module, 'register_handlers'):
                module.register_handlers(application)
                logger.info(f"✅ Loaded Module: {module_name}")
            else:
                logger.warning(f"⚠️ Skipped {module_name}: Missing 'register_handlers' function")
        except Exception as e:
            logger.error(f"❌ CRASH: Failed to load {module_name}. Error: {e}")

# --- APP FACTORY ---
global_app = None

async def get_initialized_app():
    """Returns the initialized application."""
    global global_app
    if global_app is None:
        logger.info("⚙️ Building Application...")
        token = os.environ.get("BOT_TOKEN")
        if not token:
            logger.error("❌ FATAL: BOT_TOKEN is missing in Environment Variables!")
            return None

        # Robust Connection Settings
        trequest = HTTPXRequest(
            connection_pool_size=8,
            read_timeout=30.0,
            write_timeout=30.0,
            connect_timeout=30.0,
            pool_timeout=30.0
        )

        app = ApplicationBuilder().token(token).request(trequest).build()
        load_modules(app)
        await app.initialize()
        await app.start()
        global_app = app
        logger.info("🚀 Application Built and Started!")
    
    return global_app

async def process_telegram_update(request):
    """Async handler for the request."""
    try:
        app = await get_initialized_app()
        if not app:
            return "Config Error"

        # Parse JSON
        if not request.is_json:
            return "Not JSON"
            
        data = request.get_json(silent=True)
        if not data:
            return "Empty JSON"

        # Process Update
        update = Update.de_json(data, app.bot)
        await app.process_update(update)
        return "OK"

    except Exception as e:
        logger.error(f"🔥 Unhandled Error in process_update: {e}", exc_info=True)
        return "Error"

# --- GOOGLE CLOUD ENTRY POINT ---
# This is the function you MUST type in the "Entry point" field
@functions_framework.http
def telegram_webhook(request):
    """
    Google Cloud Functions Entry Point.
    This function is 'Exposed' to the web.
    """
    # Run the async logic
    asyncio.run(process_telegram_update(request))
    return "OK"
