import motor.motor_asyncio
import pymongo
from pymongo.errors import DuplicateKeyError
import time
from datetime import datetime, timedelta
from database.cache import settings_cache

# Using local MongoDB
MONGO_URI = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client.telegram_bot_db

async def init_db():
    # Setup indexes
    await db.logs.create_index("user_id")
    await db.logs.create_index("sent_at")
    await db.users.create_index("user_id", unique=True)
    await db.menfess_posts.create_index("channel_message_id")
    await db.badwords.create_index("word", unique=True)
    await db.force_sub_channels.create_index("channel_id", unique=True)
    await db.bot_verifications.create_index("user_id", unique=True)
    await db.admin_sessions.create_index("user_id", unique=True)

    # Setup daily_limit_usage composite index (unique)
    await db.daily_limit_usage.create_index([("user_id", 1), ("usage_date", 1)], unique=True)

    # Default settings
    defaults = {
        'prefix': '🚀',
        'force_sub': '0',
        'fs_channel': '',
        'welcome_msg': 'Halo! Kirim pesanmu kesini dan akan otomatis diteruskan ke channel.',
        'fs_msg': '❌ Anda harus bergabung ke channel terlebih dahulu untuk menggunakan bot ini.',
        'maintenance': '0',
        # Pengaturan Aturan Baru
        'max_chars_enabled': '0',
        'max_chars_limit': '250',
        'badwords_enabled': '0',
        'anti_link_enabled': '0',
        'anti_username_enabled': '0',
        'anti_spam_enabled': '0',
        'anti_spam_cooldown': '10',
        'daily_limit_enabled': '0',
        'daily_limit_count': '5',
        'force_bot_enabled': '0',
        'force_bot_username': 'BeliTonBot',
        'force_bot_duration': '24'
    }
    for k, v in defaults.items():
        existing = await db.settings.find_one({"key": k})
        if not existing:
            await db.settings.insert_one({"key": k, "value": v})
            
    await _load_settings_to_cache()
    await cleanup_old_logs()

async def _load_settings_to_cache():
    settings_dict = {}
    async for row in db.settings.find():
        settings_dict[row["key"]] = row["value"]
    settings_cache.load_all(settings_dict)

async def cleanup_old_logs():
    """Menghapus log yang lebih tua dari 30 hari (Housekeeping)"""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    await db.logs.delete_many({"sent_at": {"$lte": thirty_days_ago}})

async def get_setting(key: str) -> str:
    # Memeriksa cache terlebih dahulu (Prioritas 6)
    val = settings_cache.get(key)
    if val is not None:
        return val
        
    row = await db.settings.find_one({"key": key})
    val = row["value"] if row else None
    if val is not None:
        settings_cache.set(key, val)
    return val

async def set_setting(key: str, value: str):
    await db.settings.update_one({"key": key}, {"$set": {"value": value}}, upsert=True)
    # Update cache agar query berikut mendapatkan nilai baru
    settings_cache.set(key, value)

async def add_user(user_id: int, username: str):
    await db.users.update_one(
        {"user_id": user_id},
        {"$setOnInsert": {"user_id": user_id, "username": username, "joined_at": datetime.utcnow()}},
        upsert=True
    )

async def get_all_users():
    users = []
    async for row in db.users.find({}, {"user_id": 1}):
        users.append(row["user_id"])
    return users

async def log_message(user_id: int, username: str, msg_type: str, content: str, msg_id: int = 0):
    await db.logs.insert_one({
        "user_id": user_id,
        "username": username,
        "message_type": msg_type,
        "message_content": content,
        "message_id": msg_id,
        "sent_at": datetime.utcnow()
    })

async def get_recent_logs(limit=10):
    logs = []
    async for row in db.logs.find().sort("_id", -1).limit(limit):
        sent_at_val = row["sent_at"]
        sent_at_str = sent_at_val.strftime("%Y-%m-%d %H:%M:%S") if isinstance(sent_at_val, datetime) else str(sent_at_val)
        logs.append((row["user_id"], row["username"], row["message_type"], sent_at_str))
    return logs

async def get_stats():
    users_count = await db.users.count_documents({})
    logs_count = await db.logs.count_documents({})
    return users_count, logs_count

async def add_menfess_post(user_id: int, channel_message_id: int):
    await db.menfess_posts.insert_one({
        "user_id": user_id,
        "channel_message_id": channel_message_id,
        "created_at": datetime.utcnow()
    })

async def get_menfess_owner(channel_message_id: int):
    row = await db.menfess_posts.find_one({"channel_message_id": channel_message_id})
    return row["user_id"] if row else None

async def add_badword(word: str):
    try:
        await db.badwords.insert_one({"word": word.lower()})
        return True
    except DuplicateKeyError:
        return False

async def remove_badword(word: str):
    await db.badwords.delete_many({"word": word.lower()})

async def get_all_badwords():
    badwords = []
    async for row in db.badwords.find({}, {"word": 1}):
        badwords.append(row["word"])
    return badwords

async def get_daily_usage(user_id: int, date_str: str) -> int:
    row = await db.daily_limit_usage.find_one({"user_id": user_id, "usage_date": date_str})
    return row["message_count"] if row else 0

async def increment_daily_usage(user_id: int, date_str: str):
    await db.daily_limit_usage.update_one(
        {"user_id": user_id, "usage_date": date_str},
        {"$inc": {"message_count": 1}},
        upsert=True
    )

async def get_daily_stats(date_str: str):
    pipeline = [
        {"$match": {"usage_date": date_str}},
        {"$group": {
            "_id": None,
            "total_users": {"$sum": 1},
            "total_messages": {"$sum": "$message_count"}
        }}
    ]
    cursor = db.daily_limit_usage.aggregate(pipeline)
    total_stats = None
    async for doc in cursor:
        total_stats = doc
        break
        
    total_users = total_stats["total_users"] if total_stats else 0
    total_messages = total_stats["total_messages"] if total_stats else 0
    
    pipeline_top = [
        {"$match": {"usage_date": date_str}},
        {"$sort": {"message_count": -1}},
        {"$limit": 5},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "user_info"
        }},
        {"$unwind": {"path": "$user_info", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "user_id": 1,
            "username": "$user_info.username",
            "message_count": 1
        }}
    ]
    top_users_cursor = db.daily_limit_usage.aggregate(pipeline_top)
    top_users = []
    async for doc in top_users_cursor:
        top_users.append((doc.get("user_id"), doc.get("username"), doc.get("message_count")))
        
    return total_users, total_messages, top_users

async def get_bot_verification(user_id: int) -> float:
    row = await db.bot_verifications.find_one({"user_id": user_id})
    return row["verified_at"] if row else 0.0

async def set_bot_verification(user_id: int):
    now = time.time()
    await db.bot_verifications.update_one(
        {"user_id": user_id},
        {"$set": {"verified_at": now}},
        upsert=True
    )

async def get_fs_channels() -> list:
    channels = []
    async for row in db.force_sub_channels.find({}, {"channel_id": 1}):
        channels.append(row["channel_id"])
    return channels

async def add_fs_channel(channel_id: str) -> bool:
    try:
        await db.force_sub_channels.insert_one({"channel_id": channel_id})
        return True
    except DuplicateKeyError:
        return False

async def remove_fs_channel(channel_id: str):
    await db.force_sub_channels.delete_many({"channel_id": channel_id})

async def get_admin_session(user_id: int) -> float:
    row = await db.admin_sessions.find_one({"user_id": user_id})
    return row["expired_at"] if row else 0.0

async def set_admin_session(user_id: int, duration_seconds: int = 1200):
    now = time.time()
    expired_at = now + duration_seconds
    await db.admin_sessions.update_one(
        {"user_id": user_id},
        {"$set": {"login_at": now, "expired_at": expired_at}},
        upsert=True
    )

async def delete_admin_session(user_id: int):
    await db.admin_sessions.delete_many({"user_id": user_id})

