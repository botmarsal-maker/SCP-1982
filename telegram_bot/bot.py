import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database import db
from handlers import user, admin
from middlewares.throttling import ThrottlingMiddleware

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def main():
    await db.init_db()
    
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    # Global Error Handling (Prioritas 4)
    @dp.errors()
    async def global_error_handler(update, exception):
        logging.error(f"⚠️ Global exception handler terpicu dari update: {update}\nError: {exception}", exc_info=True)
        # Jangan throw exception keatas, bot harus tetap online
        return True
    
    # Daftarkan throttling middleware (Prioritas 2)
    user.router.message.middleware(ThrottlingMiddleware(rate_limit=3.0))
    
    dp.include_router(admin.router)
    dp.include_router(user.router)
    
    logging.info("Bot started!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
