import asyncio
import json
import os
import functions_framework
from telegram import Update
from telegram.ext import ApplicationBuilder
from telegram.request import HTTPXRequest # Import this
from bot import load_modules

# Global variables
application = None

def get_application():
    global application
    if application is None:
        token = os.environ.get("BOT_TOKEN")
        
        # Define Timeouts (To prevent "ReadTimeout" errors)
        trequest = HTTPXRequest(
            connection_pool_size=8,
            read_timeout=30.0,
            write_timeout=30.0,
            connect_timeout=30.0,
            pool_timeout=30.0
        )

        # Build App with Timeouts
        application = ApplicationBuilder().token(token).request(trequest).build()
        load_modules(application)
        
    return application

async def process_update(request):
    app = get_application()
    request_json = request.get_json(silent=True)
    if request_json:
        update = Update.de_json(request_json, app.bot)
        async with app:
            await app.process_update(update)
    return "OK"

@functions_framework.http
def telegram_webhook(request):
    asyncio.run(process_update(request))
    return "OK"
