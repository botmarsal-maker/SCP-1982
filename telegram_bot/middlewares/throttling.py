import time
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 3.0):
        self.rate_limit = rate_limit
        self.users = {}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        
        # Ignore non-messages somehow, but we only attach this to message handlers anyway
        if not event.text and not event.photo and not event.video and not event.document:
             return await handler(event, data)

        # Do not throttle commands
        if event.text and event.text.startswith('/'):
            return await handler(event, data)

        user_id = event.from_user.id
        now = time.time()
        
        last_time = self.users.get(user_id, 0)
        if now - last_time < self.rate_limit:
            await event.answer("⚠️ Terlalu cepat mengirim pesan. Coba lagi beberapa detik.")
            return # Drop update
            
        self.users[user_id] = now
        return await handler(event, data)
