from database.client import db

filters_col = db.filters

# Placeholder for future filter logic
async def add_filter(chat_id, trigger, reply):
    await filters_col.update_one(
        {"chat_id": chat_id, "trigger": trigger},
        {"$set": {"reply": reply}},
        upsert=True
    )