from database.client import db
from pymongo import ReturnDocument

async def set_bio_lock(chat_id, status: bool):
    await db.chats.update_one(
        {'_id': chat_id}, 
        {'$set': {'bio_lock_enabled': status}}, 
        upsert=True
    )

async def is_bio_lock_enabled(chat_id) -> bool:
    data = await db.chats.find_one({'_id': chat_id})
    return data.get('bio_lock_enabled', False) if data else False

async def add_bio_warn(chat_id, user_id) -> int:
    """Increments bio warning count. Returns new count."""
    result = await db.bio_warns.find_one_and_update(
        {'chat_id': chat_id, 'user_id': user_id},
        {'$inc': {'count': 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return result['count']

async def reset_bio_warns(chat_id, user_id):
    await db.bio_warns.delete_one({'chat_id': chat_id, 'user_id': user_id})
