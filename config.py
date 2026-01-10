import os
# Get variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")
OWNER_ID = os.environ.get("OWNER_ID")

# Security Check: Stop the bot if secrets are missing
if not BOT_TOKEN:
    raise ValueError("❌ FATAL ERROR: BOT_TOKEN is missing. Set it in your environment variables or .env file.")

if not MONGO_URI:
    raise ValueError("❌ FATAL ERROR: MONGO_URI is missing. Set it in your environment variables or .env file.")

# Safely convert Owner ID
try:
    OWNER_ID = int(OWNER_ID)
except (TypeError, ValueError):
    print("⚠️ WARNING: OWNER_ID is invalid or missing. You won't be able to use Admin commands.")
    OWNER_ID = None
