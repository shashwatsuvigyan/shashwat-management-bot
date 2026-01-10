from database.client import db

warns_col = db.warns

async def get_warns(chat_id, user_id):
    """Returns the number of warnings a user has."""
    doc = await warns_col.find_one({"chat_id": chat_id, "user_id": user_id})
    return doc['count'] if doc else 0

async def add_warn(chat_id, user_id):
    """Increments warning count. Returns new count."""
    current = await get_warns(chat_id, user_id)
    new_count = current + 1
    await warns_col.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": new_count}},
        upsert=True
    )
    return new_count

async def reset_warns(chat_id, user_id):
    """Resets warnings to 0."""
    await warns_col.delete_one({"chat_id": chat_id, "user_id": user_id})
