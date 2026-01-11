from database.client import db

async def set_abuse_filter(chat_id, status):
    await db.abuse.update_one({'_id': chat_id}, {'$set': {'status': status}}, upsert=True)

async def is_abuse_filter_enabled(chat_id):
    data = await db.abuse.find_one({'_id': chat_id})
    return data and data.get('status')

async def add_abuse_warn(chat_id, user_id):
    # Simple warning logic
    return 1 # (Simplify for demo, requires complex logic for full count)

async def reset_abuse_warns(chat_id, user_id):
    pass
