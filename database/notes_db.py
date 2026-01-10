from database.client import db

notes_col = db.notes

async def save_note(chat_id, name, content):
    await notes_col.update_one(
        {"chat_id": chat_id, "name": name},
        {"$set": {"content": content}},
        upsert=True
    )

async def get_note(chat_id, name):
    doc = await notes_col.find_one({"chat_id": chat_id, "name": name})
    return doc['content'] if doc else None

async def delete_note(chat_id, name):
    await notes_col.delete_one({"chat_id": chat_id, "name": name})