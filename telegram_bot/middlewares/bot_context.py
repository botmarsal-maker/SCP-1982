from aiogram import BaseMiddleware
from globals import current_bot_id
import time
from database.clone_db import clone_db

class BotContextMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        bot = data["bot"]
        bot_id = str(bot.id)
        
        # Check if it's the main bot
        # Main bot ID is not strictly needed, but let's assume if it's not in clones, it's main.
        # Actually it's easier if we just know from config.BOT_TOKEN
        from config import BOT_TOKEN
        main_bot_id = BOT_TOKEN.split(':')[0]
        
        if bot_id == main_bot_id:
            token = current_bot_id.set("main")
        else:
            token = current_bot_id.set(bot_id)
            # CHECK EXPLIRATION HERE
            clone_info = await clone_db.get_clone(bot_id)
            if clone_info:
                if clone_info['status'] == 'suspended':
                    if hasattr(event, "message") and event.message:
                        await event.message.answer("❌ Bot ini sedang dinonaktifkan (Suspended).\n\nSilakan hubungi penyedia layanan.")
                    elif hasattr(event, "callback_query") and event.callback_query:
                        await event.callback_query.answer("❌ Bot sedang dinonaktifkan.", show_alert=True)
                    current_bot_id.reset(token)
                    return
                elif clone_info['expired_at'] < time.time():
                    # EXPIRED!
                    if hasattr(event, "message") and event.message:
                        await event.message.answer("❌ Masa aktif bot telah berakhir.\n\nSilakan hubungi penyedia layanan.")
                    elif hasattr(event, "callback_query") and event.callback_query:
                        await event.callback_query.answer("❌ Masa aktif bot telah berakhir.", show_alert=True)
                    current_bot_id.reset(token)
                    return # Stop execution
            else:
                # Ghost bot running? Maybe it was deleted.
                current_bot_id.reset(token)
                return 

        try:
            return await handler(event, data)
        finally:
            current_bot_id.reset(token)
