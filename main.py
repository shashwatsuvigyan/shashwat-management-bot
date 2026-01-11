import asyncio
import os
import logging
import importlib
import functions_framework
from telegram import Update
from telegram.ext import ApplicationBuilder, Application
from telegram.request import HTTPXRequest

# Setup Logging
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
        logger.error(f"❌ Modules directory not found at: {modules_path}")
        return

    module_files = [
        f[:-3] for f in os.listdir(modules_path)
        if f.endswith('.py') and f != '__init__.py'
    ]

    for module_name in module_files:
        try:
            module = importlib.import_module(f'modules.{module_name}')
            if hasattr(module, 'register_handlers'):
                module.register_handlers(application)
                logger.info(f"✅ Loaded: {module_name}")
            else:
                logger.warning(f"⚠️ Skipped {module_name}: No register_handlers")
        except Exception as e:
            logger.error(f"❌ Failed to load {module_name}: {e}")

# --- APP BUILDER ---
application = None

def get_application():
    global application
    if application is None:
        token = os.environ.get("BOT_TOKEN")
        
        # Connection Settings (Prevents Timeouts)
        trequest = HTTPXRequest(
            connection_pool_size=8,
            read_timeout=30.0,
            write_timeout=30.0,
            connect_timeout=30.0,
            pool_timeout=30.0
        )

        application = ApplicationBuilder().token(token).request(trequest).build()
        load_modules(application)
        
    return application

async def process_update(request):
    app = get_application()
    if request.is_json:
        request_json = request.get_json(silent=True)
        if request_json:
            update = Update.de_json(request_json, app.bot)
            async with app:
                await app.process_update(update)
    return "OK"

# --- ENTRY POINT ---
@functions_framework.http
def telegram_webhook(request):
    asyncio.run(process_update(request))
    return "OK"
