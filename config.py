import os

# Load variables directly from the environment (Google Cloud settings)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))
MONGO_URI = os.environ.get("MONGO_URI")

# Optional: Add other variables here if your bot needs them
NSFW_API_USER = os.environ.get("NSFW_API_USER")
NSFW_API_SECRET = os.environ.get("NSFW_API_SECRET")
