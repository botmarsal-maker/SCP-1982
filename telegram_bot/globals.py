from contextvars import ContextVar

current_bot_id = ContextVar("current_bot_id", default="main")

async def get_bot_owner() -> int:
    bot_id = current_bot_id.get("main")
    from config import OWNER_ID
    if bot_id == "main" or not bot_id:
        return OWNER_ID
        
    from database.clone_db import clone_db
    c = await clone_db.get_clone(bot_id)
    if c:
        return int(c['owner_id'])
    return OWNER_ID
