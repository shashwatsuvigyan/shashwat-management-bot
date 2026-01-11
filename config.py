import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))
MONGO_URI = os.environ.get("MONGO_URI")
NSFW_API_USER = os.environ.get("NSFW_API_USER")
NSFW_API_SECRET = os.environ.get("NSFW_API_SECRET")
