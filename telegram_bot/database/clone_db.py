import aiosqlite
import time

import os
data_dir = os.environ.get("DATA_DIR", ".")
DB_NAME = os.path.join(data_dir, "bot.db")

class CloneDB:
    async def init_db(self):
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS clones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_token TEXT UNIQUE,
                    bot_id TEXT UNIQUE,
                    bot_username TEXT,
                    owner_id INTEGER,
                    expired_at REAL,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def add_clone(self, bot_token: str, bot_id: str, bot_username: str, owner_id: int, duration_days: int):
        expired_at = time.time() + (duration_days * 86400)
        async with aiosqlite.connect(DB_NAME) as db:
            try:
                await db.execute("""
                    INSERT INTO clones (bot_token, bot_id, bot_username, owner_id, expired_at) 
                    VALUES (?, ?, ?, ?, ?)
                """, (bot_token, bot_id, bot_username, owner_id, expired_at))
                await db.commit()
                return True
            except aiosqlite.IntegrityError:
                return False

    async def get_clones(self):
        async with aiosqlite.connect(DB_NAME) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM clones") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_clone(self, bot_id: str):
        async with aiosqlite.connect(DB_NAME) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM clones WHERE bot_id=?", (bot_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def delete_clone(self, bot_id: str):
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("DELETE FROM clones WHERE bot_id=?", (bot_id,))
            await db.commit()

    async def extend_clone(self, bot_id: str, days: int):
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute("SELECT expired_at FROM clones WHERE bot_id=?", (bot_id,)) as cursor:
                row = await cursor.fetchone()
                if not row: return False
                
                # If already expired, start from now
                current_exp = row[0]
                if current_exp < time.time():
                    new_exp = time.time() + (days * 86400)
                else:
                    new_exp = current_exp + (days * 86400)
                    
            await db.execute("UPDATE clones SET expired_at=? WHERE bot_id=?", (new_exp, bot_id))
            await db.commit()
            return True

    async def update_status(self, bot_id: str, status: str):
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("UPDATE clones SET status=? WHERE bot_id=?", (status, bot_id))
            await db.commit()
            
clone_db = CloneDB()
