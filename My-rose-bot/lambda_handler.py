import asyncio
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN
from bot import load_modules  # Import the loader from your existing bot.py

# Setup Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize the Application
# We build it here so it stays "warm" in memory for faster responses
application = ApplicationBuilder().token(BOT_TOKEN).build()
load_modules(application)

async def process_update(event):
    """Async function to handle the Telegram Update"""
    try:
        # 1. Parse the incoming JSON from AWS API Gateway
        body = json.loads(event['body'])
        
        # 2. Decode the JSON into a Telegram Update object
        update = Update.de_json(body, application.bot)
        
        # 3. Process the update
        await application.initialize()
        await application.process_update(update)
        await application.shutdown()
        
        return {'statusCode': 200, 'body': 'OK'}
        
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return {'statusCode': 500, 'body': 'Error'}

def lambda_handler(event, context):
    """The standard entry point for AWS Lambda"""
    return asyncio.get_event_loop().run_until_complete(process_update(event))
