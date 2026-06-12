import asyncio
import logging
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

clone_tasks = {}

async def start_clone(bot_token: str, bot_id: str, dispatcher):
    if bot_id in clone_tasks:
        logging.warning(f"Clone {bot_id} is already running.")
        return
        
    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # Clear any old webhooks
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logging.error(f"Failed to clear webhook for clone {bot_id}: {e}")
        
    # Initialize the specific database for this clone
    from globals import current_bot_id
    from database.db import init_db
    token = current_bot_id.set(bot_id)
    try:
        await init_db()
    except Exception as e:
        logging.error(f"Failed to initialize db for clone {bot_id}: {e}")
    finally:
        current_bot_id.reset(token)
        
    # Note: start_polling is an async blocking task
    task = asyncio.create_task(dispatcher.start_polling(bot))
    clone_tasks[bot_id] = task
    logging.info(f"Started clone {bot_id}")

async def stop_clone(bot_id: str):
    if bot_id in clone_tasks:
        clone_tasks[bot_id].cancel()
        del clone_tasks[bot_id]
        logging.info(f"Stopped clone {bot_id}")

def get_running_clones():
    return list(clone_tasks.keys())
