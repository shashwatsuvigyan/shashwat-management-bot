import logging
import os
import importlib
from telegram.ext import Application
from config import BOT_TOKEN

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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
