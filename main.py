import asyncio
import os
import logging
import importlib
import functions_framework
from telegram import Update
from telegram.ext import ApplicationBuilder, Application
from telegram.request import HTTPXRequest

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- MODULE LOADER (Fixed & Integrated) ---
def load_modules(application: Application):
    """Dynamically loads all modules from the 'modules' folder."""
    # Ensure we look in the correct directory relative to this file
    modules_path = os.path.join(os.path.dirname(__file__), 'modules')
    
    if not os.path.exists(modules_path):
        logger.error(f"❌ Modules directory not found at: {modules_path}")
        return

    # List all .py files in the modules folder
    module_files = [
        f[:-3] for f in os.listdir(modules_path)
        if f.endswith('.py') and f != '__init__.py'
    ]

    for module_name in module_files:
        try:
            # Import the module
            module = importlib.import_module(f'modules.{module_name}')
            
            # Check if it has the registration function
            if hasattr(module, 'register_handlers'):
                module.register_handlers(application)
                logger.info(f"✅ Loaded module: {module_name}")
            else:
                logger.warning(f"⚠️ Skipped {module_name}: Missing 'register_handlers'")
                
        except Exception as e:
            logger.error(f"❌ Failed to load {module_name}: {e}")

# --- GLOBAL VARIABLES ---
application = None

def get_application():
    """Builds the bot application (Singleton Pattern)."""
    global application
    if application is None:
        # Load token safely from Environment Variables
        token = os.environ.get("BOT_TOKEN")
        if not token:
            logger.error("❌ BOT_TOKEN is missing! Check Google Cloud Environment Variables.")
            return None

        # 1. Setup Connection Options (Crucial to prevent 'Timed Out' errors)
        trequest = HTTPXRequest(
            connection_pool_size=8,
            read_timeout=30.0,
            write_timeout=30.0,
            connect_timeout=30.0,
            pool_timeout=30.0
        )

        # 2. Build the Application
        application = ApplicationBuilder().token(token).request(trequest).build()
        
        # 3. Load your Modules (The logic you provided)
        load_modules(application)
        
    return application

async def process_update(request):
    """Processes the incoming update from Telegram."""
    app = get_application()
    if not app:
        return "Error: Bot Token not set"
    
    # Handle JSON request safely
    if request.is_json:
        request_json = request.get_json(silent=True)
        if request_json:
            update = Update.de_json(request_json, app.bot)
            async with app:
                await app.process_update(update)
            
    return "OK"

# --- GOOGLE CLOUD ENTRY POINT ---
@functions_framework.http
def telegram_webhook(request):
    """The Function that Google Cloud calls."""
    # Run the async process in a synchronous runner
    asyncio.run(process_update(request))
    return "OK"
