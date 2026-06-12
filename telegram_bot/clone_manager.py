import asyncio
import logging
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

clone_tasks = {}

async def poll_clone(bot: Bot, dispatcher, bot_id: str):
    offset = None
    logging.info(f"[CLONE] polling_started=True for {bot_id}")
    while True:
        try:
            updates = await bot.get_updates(offset=offset, timeout=30, allowed_updates=dispatcher.resolve_used_update_types())
            for update in updates:
                offset = update.update_id + 1
                asyncio.create_task(dispatcher.feed_update(bot, update))
        except asyncio.CancelledError:
            logging.info(f"[CLONE] polling_stopped=True for {bot_id}")
            await bot.session.close()
            break
        except Exception as e:
            logging.error(f"[CLONE] polling error for {bot_id}: {e}")
            await asyncio.sleep(5)

async def start_clone(bot_token: str, bot_id: str, dispatcher):
    if bot_id in clone_tasks:
        logging.warning(f"[CLONE] {bot_id} is already running.")
        return
        
    logging.info(f"[CLONE] starting=@{bot_id}")
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
        logging.error(f"[CLONE] Failed to initialize db for clone {bot_id}: {e}")
    finally:
        current_bot_id.reset(token)
        
    logging.info(f"[CLONE] router_registered=True")
    logging.info(f"[CLONE] clone_ready=True")
    
    # Run manual polling loop
    task = asyncio.create_task(poll_clone(bot, dispatcher, bot_id))
    clone_tasks[bot_id] = task
    logging.info(f"[CLONE] Started clone {bot_id}")

async def stop_clone(bot_id: str):
    if bot_id in clone_tasks:
        clone_tasks[bot_id].cancel()
        del clone_tasks[bot_id]
        logging.info(f"Stopped clone {bot_id}")

def get_running_clones():
    return list(clone_tasks.keys())
