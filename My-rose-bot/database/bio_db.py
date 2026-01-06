from database.client import db

bio_col = db.bio_settings
bio_warns_col = db.bio_warns

# --- SETTINGS (ON/OFF) ---
async def set_bio_lock(chat_id, status):
    """Status: True (On) or False (Off)"""
    await bio_col.update_one(
        {"chat_id": chat_id},
        {"$set": {"is_enabled": status}},
        upsert=True
    )

async def is_bio_lock_enabled(chat_id):
    doc = await bio_col.find_one({"chat_id": chat_id})
    return doc['is_enabled'] if doc else False

# --- WARNINGS SYSTEM ---
async def add_bio_warn(chat_id, user_id):
    """Increments warn count. Returns new count."""
    doc = await bio_warns_col.find_one({"chat_id": chat_id, "user_id": user_id})
    new_count = (doc['count'] + 1) if doc else 1
    
    await bio_warns_col.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": new_count}},
        upsert=True
    )
    return new_count

async def reset_bio_warns(chat_id, user_id):
    await bio_warns_col.delete_one({"chat_id": chat_id, "user_id": user_id})
