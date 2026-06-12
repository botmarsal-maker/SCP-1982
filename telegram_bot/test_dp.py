
import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message

router = Router()
@router.message()
async def msg(message: Message):
    pass

async def main():
    dp1 = Dispatcher()
    dp1.include_router(router)
    dp2 = Dispatcher()
    dp2.include_router(router)
    print("Success")

asyncio.run(main())
