
import asyncio
import logging
from aiogram import Bot, Dispatcher
logging.basicConfig(level=logging.INFO)
dp = Dispatcher()

async def main():
    bot1 = Bot("123:abc")
    bot2 = Bot("456:def")
    t1 = asyncio.create_task(dp.start_polling(bot1))
    await asyncio.sleep(1)
    t2 = asyncio.create_task(dp.start_polling(bot2))
    await asyncio.sleep(2)
    print("Done")

asyncio.run(main())
