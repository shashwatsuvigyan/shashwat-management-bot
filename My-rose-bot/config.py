import os

# Using .get helps avoid crashes if keys are missing, but ensure you set them!
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7769815394:AAFO22QfHpGXlX_k3emqfW3-xI1BLh74bbc")
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://Zachroost:Zachroost-owl@shashwat-group-cluster.uu4qeif.mongodb.net/?appName=shashwat-group-cluster")

# Safely convert OWNER_ID to int, defaulting to a dummy ID if fails
try:
    OWNER_ID = int(os.environ.get("OWNER_ID", "8419778466"))
except ValueError:
    OWNER_ID = 123456789