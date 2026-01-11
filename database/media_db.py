from database.client import db

async def set_delete_timer(chat_id, seconds: int):
    """Sets the auto-delete timer (in seconds)."""
    await db.chats.update_one(
        {'_id': chat_id}, 
        {'$set': {'media_delete_timer': seconds}}, 
        upsert=True
    )

async def get_delete_timer(chat_id) -> int:
    """Gets the current timer value. Returns 0 if not set."""
    data = await db.chats.find_one({'_id': chat_id})
    return data.get('media_delete_timer', 0) if data else 0
