import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database import db
from handlers import user, admin, group
from middlewares.throttling import ThrottlingMiddleware
from middlewares.answer_callback import AnswerCallbackMiddleware
from middlewares.force_sub import ForceSubscribeMiddleware
from middlewares.force_bot import ForceBotMiddleware

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def main():
    await db.init_db()
    
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    # Global Error Handling (Prioritas 4)
    from aiogram.types.error_event import ErrorEvent
    @dp.errors()
    async def global_error_handler(event: ErrorEvent):
        logging.error(f"⚠️ Global exception handler terpicu dari update: {event.update}\nError: {event.exception}", exc_info=True)
        # Jangan throw exception keatas, bot harus tetap online
        return True
    
    # Daftarkan throttling middleware (Prioritas 2)
    throttling_mw = ThrottlingMiddleware(rate_limit=3.0, cb_rate_limit=1.0)
    dp.message.middleware(throttling_mw)
    dp.callback_query.middleware(throttling_mw)
    
    # Daftarkan ForceSubscribeMiddleware agar berjalan di semua request user
    user.router.message.middleware(ForceSubscribeMiddleware())
    user.router.callback_query.middleware(ForceSubscribeMiddleware())

    # Daftarkan ForceBotMiddleware
    user.router.message.middleware(ForceBotMiddleware())
    user.router.callback_query.middleware(ForceBotMiddleware())
    
    # Daftarkan middleware callback
    dp.callback_query.middleware(AnswerCallbackMiddleware())
    
    dp.include_router(admin.router)
    dp.include_router(user.router)
    dp.include_router(group.router)
    
    logging.info("Bot started!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
