import asyncio
import json
import os
import functions_framework
from telegram import Update
from telegram.ext import ApplicationBuilder
from telegram.request import HTTPXRequest 
from bot import load_modules

# Global variable to keep the bot running in memory
application = None

def get_application():
    global application
    if application is None:
        token = os.environ.get("BOT_TOKEN")
        
        # 1. Setup Connection Options (Prevents Timed Out errors)
        trequest = HTTPXRequest(
            connection_pool_size=8,
            read_timeout=30.0,
            write_timeout=30.0,
            connect_timeout=30.0,
            pool_timeout=30.0
        )

        # 2. Build the Application
        application = ApplicationBuilder().token(token).request(trequest).build()
        
        # 3. Load your Modules (commands)
        load_modules(application)
        
    return application

async def process_update(request):
    """Processes the update from Telegram"""
    app = get_application()
    
    # Handle JSON request safely
    if request.is_json:
        request_json = request.get_json(silent=True)
        if request_json:
            update = Update.de_json(request_json, app.bot)
            async with app:
                await app.process_update(update)
            
    return "OK"

@functions_framework.http
def telegram_webhook(request):
    """The Entry Point function for Google Cloud"""
    # Run the async process in a synchronous runner
    asyncio.run(process_update(request))
    return "OK"
