import aiosqlite
from database.cache import settings_cache

DB_NAME = "bot.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                message_type TEXT,
                message_content TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_id INTEGER
            )
        """)
        
        # Tambahkan index untuk optimasi query (Prioritas 5)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_logs_user_id ON logs(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_logs_sent_at ON logs(sent_at)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id)")
        
        # Tabel relasi untuk notifikasi komentar (Fitur 2)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS menfess_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                channel_message_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_menfess_posts_msg_id ON menfess_posts(channel_message_id)")

        # Tabel badwords (Fitur Filter Kata Kasar)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS badwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE
            )
        """)
        
        # Default settings
        defaults = {
            'prefix': '🚀',
            'force_sub': '0',
            'fs_channel': '',
            'welcome_msg': 'Halo! Kirim pesanmu kesini dan akan otomatis diteruskan ke channel.',
            'fs_msg': 'Silakan join channel terlebih dahulu untuk menggunakan bot.',
            'maintenance': '0',
            # Pengaturan Aturan Baru
            'max_chars_enabled': '0',
            'max_chars_limit': '250',
            'badwords_enabled': '0',
            'anti_link_enabled': '0',
            'anti_username_enabled': '0',
            'anti_spam_enabled': '0',
            'anti_spam_cooldown': '10'
        }
        for k, v in defaults.items():
            await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
            
        await db.commit()
    
    await _load_settings_to_cache()
    await cleanup_old_logs()

async def _load_settings_to_cache():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT key, value FROM settings") as cursor:
            rows = await cursor.fetchall()
            settings_dict = {row[0]: row[1] for row in rows}
            settings_cache.load_all(settings_dict)

async def cleanup_old_logs():
    """Menghapus log yang lebih tua dari 30 hari (Housekeeping)"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM logs WHERE sent_at <= datetime('now', '-30 days')")
        await db.commit()

async def get_setting(key: str) -> str:
    # Memeriksa cache terlebih dahulu (Prioritas 6)
    val = settings_cache.get(key)
    if val is not None:
        return val
        
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT value FROM settings WHERE key=?", (key,)) as cursor:
            row = await cursor.fetchone()
            val = row[0] if row else None
            if val is not None:
                settings_cache.set(key, val)
            return val

async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        await db.commit()
    # Update cache agar query berikut mendapatkan nilai baru
    settings_cache.set(key, value)

async def add_user(user_id: int, username: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

async def log_message(user_id: int, username: str, msg_type: str, content: str, msg_id: int = 0):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO logs (user_id, username, message_type, message_content, message_id) VALUES (?, ?, ?, ?, ?)", (user_id, username, msg_type, content, msg_id))
        await db.commit()

async def get_recent_logs(limit=10):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id, username, message_type, sent_at FROM logs ORDER BY id DESC LIMIT ?", (limit,)) as cursor:
            return await cursor.fetchall()

async def get_stats():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            users_count = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM logs") as cursor:
            logs_count = (await cursor.fetchone())[0]
        return users_count, logs_count

async def add_menfess_post(user_id: int, channel_message_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO menfess_posts (user_id, channel_message_id) VALUES (?, ?)", (user_id, channel_message_id))
        await db.commit()

async def get_menfess_owner(channel_message_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM menfess_posts WHERE channel_message_id=?", (channel_message_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def add_badword(word: str):
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            await db.execute("INSERT INTO badwords (word) VALUES (?)", (word.lower(),))
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

async def remove_badword(word: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM badwords WHERE word=?", (word.lower(),))
        await db.commit()

async def get_all_badwords():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT word FROM badwords") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

