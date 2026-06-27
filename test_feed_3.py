
import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, Update
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import sys
import logging
from unittest.mock import AsyncMock

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

router = Router()

@router.message()
async def msg(message: Message):
    print(f"[{message.bot.id}] Got message: {message.text}")
    await message.answer(f"Reply from {message.bot.id}")

dp = Dispatcher()
dp.include_router(router)

async def poll_clone(bot, dp, bot_id):
    offset = None
    print(f"[{bot_id}] Polling manually started")
    # Just to mock updates since we can't actually poll Telegram without token
    # Oh wait, we CAN poll telegram if we have a token.
    # But I will just mock it.
    pass

async def test():
    # Simulate feeding update
    from aiogram.types import User, Chat
    bot1 = Bot("123:abc")
    bot2 = Bot("456:def")
    
    user = User(id=1, is_bot=False, first_name="Test")
    chat = Chat(id=1, type="private")
    msg1 = Message(message_id=1, date=123, chat=chat, from_user=user, text="Hello 1")
    update1 = Update(update_id=1, message=msg1)
    
    msg2 = Message(message_id=2, date=124, chat=chat, from_user=user, text="Hello 2")
    update2 = Update(update_id=2, message=msg2)
    
    print("Feeding update 1 to bot 1")
    await dp.feed_update(bot1, update1)
    
    print("Feeding update 2 to bot 2")
    await dp.feed_update(bot2, update2)

asyncio.run(test())
