from database.client import db

media_col = db.media_settings

async def set_delete_timer(chat_id, seconds):
    """Sets the auto-delete timer in seconds. 0 = Disabled."""
    await media_col.update_one(
        {"chat_id": chat_id},
        {"$set": {"delete_seconds": seconds}},
        upsert=True
    )

async def get_delete_timer(chat_id):
    """Returns the timer in seconds, or 0 if not set."""
    doc = await media_col.find_one({"chat_id": chat_id})
    return doc['delete_seconds'] if doc else 0
