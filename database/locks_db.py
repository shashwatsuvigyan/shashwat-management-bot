from database.client import db

locks_col = db.locks

async def lock_type(chat_id, lock_type):
    await locks_col.update_one(
        {"chat_id": chat_id},
        {"$addToSet": {"locked": lock_type}},
        upsert=True
    )

async def unlock_type(chat_id, lock_type):
    await locks_col.update_one(
        {"chat_id": chat_id},
        {"$pull": {"locked": lock_type}}
    )

async def get_locked_types(chat_id):
    doc = await locks_col.find_one({"chat_id": chat_id})
    return doc['locked'] if doc and 'locked' in doc else []