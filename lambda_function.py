import json
import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN
from bot import load_modules

# Setup Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

async def main(event):
    """
    Main Async Function
    """
    # 1. Build the App FRESH every time to avoid Event Loop errors
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    load_modules(application)

    try:
        # 2. Decode the JSON body from AWS
        body = None
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})

        # 3. Process the update
        async with application:
            update = Update.de_json(body, application.bot)
            if update:
                await application.process_update(update)

        # 4. Return a clean JSON response (Crucial for API Gateway)
        return {
            'statusCode': 200,
            'body': json.dumps('OK')
        }
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return {
            'statusCode': 200, 
            'body': json.dumps('Error handled')
        }

def lambda_handler(event, context):
    # RUN ASYNCIO CORRECTLY
    return asyncio.run(main(event))
