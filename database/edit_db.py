from database.client import db

async def set_edit_guardian(chat_id, status: bool):
    await db.chats.update_one(
        {'_id': chat_id}, 
        {'$set': {'edit_guardian_enabled': status}}, 
        upsert=True
    )

async def is_edit_guardian_enabled(chat_id) -> bool:
    data = await db.chats.find_one({'_id': chat_id})
    return data.get('edit_guardian_enabled', False) if data else False
