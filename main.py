import asyncio
import json
import os
import functions_framework
from telegram import Update
from telegram.ext import ApplicationBuilder
from bot import load_modules

# Global variables
application = None

# Initialize App Logic
def get_application():
    global application
    if application is None:
        token = os.environ.get("BOT_TOKEN")
        application = ApplicationBuilder().token(token).build()
        load_modules(application)
    return application

async def process_update(request):
    """Async function to process the update"""
    app = get_application()
    
    # Get JSON from Google Request object
    request_json = request.get_json(silent=True)
    
    if request_json:
        # Process Update
        update = Update.de_json(request_json, app.bot)
        async with app:
            await app.process_update(update)
            
    return "OK"

@functions_framework.http
def telegram_webhook(request):
    """The entry point that Google calls"""
    # Run the async process
    asyncio.run(process_update(request))
    return "OK"
