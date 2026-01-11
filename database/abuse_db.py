from database.client import db
from pymongo import ReturnDocument

async def set_abuse_filter(chat_id, status: bool):
    """Enables or Disables the abuse filter for a chat."""
    await db.chats.update_one(
        {'_id': chat_id}, 
        {'$set': {'abuse_enabled': status}}, 
        upsert=True
    )

async def is_abuse_filter_enabled(chat_id) -> bool:
    """Checks if abuse filter is enabled."""
    data = await db.chats.find_one({'_id': chat_id})
    return data.get('abuse_enabled', False) if data else False

async def add_abuse_warn(chat_id, user_id) -> int:
    """
    Increments the abuse warning count for a user in a specific chat.
    Returns the NEW count.
    """
    # We store warnings in a separate collection to keep chat settings clean
    result = await db.abuse_warns.find_one_and_update(
        {'chat_id': chat_id, 'user_id': user_id},
        {'$inc': {'count': 1}},  # Increment by 1
        upsert=True,             # Create if doesn't exist
        return_document=ReturnDocument.AFTER # Return the new value
    )
    return result['count']

async def reset_abuse_warns(chat_id, user_id):
    """Resets warnings (usually after a ban)."""
    await db.abuse_warns.delete_one({'chat_id': chat_id, 'user_id': user_id})
