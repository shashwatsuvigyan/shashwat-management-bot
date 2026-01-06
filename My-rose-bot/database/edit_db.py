from database.client import db

edit_col = db.edit_settings

async def set_edit_guardian(chat_id, status):
    """Status: True (On) or False (Off)"""
    await edit_col.update_one(
        {"chat_id": chat_id},
        {"$set": {"is_enabled": status}},
        upsert=True
    )

async def is_edit_guardian_enabled(chat_id):
    """Returns True if enabled, False otherwise."""
    doc = await edit_col.find_one({"chat_id": chat_id})
    return doc['is_enabled'] if doc else False
