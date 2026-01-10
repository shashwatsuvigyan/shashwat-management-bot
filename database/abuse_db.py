from database.client import db

abuse_settings = db.abuse_settings
abuse_warns = db.abuse_warns

# --- SETTINGS ---
async def set_abuse_filter(chat_id, status):
    """True = On, False = Off"""
    await abuse_settings.update_one(
        {"chat_id": chat_id},
        {"$set": {"is_enabled": status}},
        upsert=True
    )

async def is_abuse_filter_enabled(chat_id):
    doc = await abuse_settings.find_one({"chat_id": chat_id})
    return doc['is_enabled'] if doc else False

# --- WARNINGS ---
async def add_abuse_warn(chat_id, user_id):
    doc = await abuse_warns.find_one({"chat_id": chat_id, "user_id": user_id})
    new_count = (doc['count'] + 1) if doc else 1
    
    await abuse_warns.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": new_count}},
        upsert=True
    )
    return new_count

async def reset_abuse_warns(chat_id, user_id):
    await abuse_warns.delete_one({"chat_id": chat_id, "user_id": user_id})
