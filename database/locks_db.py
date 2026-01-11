from database.client import db

async def lock_type(chat_id, lock_type: str):
    """Adds a type (e.g., 'sticker') to the locked list."""
    await db.chats.update_one(
        {'_id': chat_id}, 
        {'$addToSet': {'locked_types': lock_type}}, # $addToSet prevents duplicates
        upsert=True
    )

async def unlock_type(chat_id, lock_type: str):
    """Removes a type from the locked list."""
    await db.chats.update_one(
        {'_id': chat_id}, 
        {'$pull': {'locked_types': lock_type}} # $pull removes specific item
    )

async def get_locked_types(chat_id) -> list:
    """Returns a list of all locked types for the chat."""
    data = await db.chats.find_one({'_id': chat_id})
    return data.get('locked_types', []) if data else []
