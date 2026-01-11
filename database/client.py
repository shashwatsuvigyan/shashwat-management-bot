import motor.motor_asyncio
from config import MONGO_URI

# Initialize the Async Client
cli = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = cli.MyRoseBot  # Database Name
