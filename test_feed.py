
import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, Update, User, Chat
import sys
import logging
from unittest.mock import AsyncMock

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

router = Router()
@router.message()
async def on_msg(message: Message):
    print(f"Message received in bot {message.bot.id}: {message.text}")

async def main():
    dp = Dispatcher()
    dp.include_router(router)

    bot1 = Bot("12345:AAGtest1")
    bot2 = Bot("67890:AAGtest2")

    user = User(id=1, is_bot=False, first_name="Test")
    chat = Chat(id=1, type="private")
    msg = Message(message_id=1, date=123, chat=chat, from_user=user, text="Hello")
    update = Update(update_id=1, message=msg)

    print("Feeding to bot1")
    await dp.feed_update(bot1, update)
    print("Feeding to bot2")
    await dp.feed_update(bot2, update)

asyncio.run(main())
