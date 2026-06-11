import time
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 3.0, cb_rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self.cb_rate_limit = cb_rate_limit
        self.users = {}
        self.cb_users = {}

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        
        user_id = event.from_user.id
        now = time.time()
        
        if hasattr(event, 'data') and hasattr(event, 'message'):
            # This is a CallbackQuery (or looks like one)
            last_time = self.cb_users.get(user_id, 0)
            if now - last_time < self.cb_rate_limit:
                try:
                    await event.answer("⚠️ Terlalu cepat mengklik tombol.")
                except:
                    pass
                return # Drop update
            self.cb_users[user_id] = now
            return await handler(event, data)
            
        elif hasattr(event, 'text'):
            # This is a Message
            # Ignore non-messages with no text/media
            if not getattr(event, 'text', None) and not getattr(event, 'photo', None) and not getattr(event, 'video', None) and not getattr(event, 'document', None):
                 return await handler(event, data)
                 
            # Do not throttle commands
            if getattr(event, 'text', None) and event.text.startswith('/'):
                return await handler(event, data)

            last_time = self.users.get(user_id, 0)
            if now - last_time < self.rate_limit:
                await event.answer("⚠️ Terlalu cepat mengirim pesan. Coba lagi beberapa detik.")
                return # Drop update
                
            self.users[user_id] = now
            return await handler(event, data)
            
        return await handler(event, data)
