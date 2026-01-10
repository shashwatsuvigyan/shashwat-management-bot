from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI

# Motor is lazy; it won't connect until the first query
client = AsyncIOMotorClient(MONGO_URI)
db = client.rose_bot_db