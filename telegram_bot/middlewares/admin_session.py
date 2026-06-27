from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.fsm.context import FSMContext
from typing import Callable, Dict, Any, Awaitable
from database import db
from config import OWNER_ID
import time

class AdminSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Pengecualian untuk state login pin, sehingga admin bisa input pin
        state: FSMContext = data.get("state")
        if state:
            current_state = await state.get_state()
            if current_state == "AdminState:waiting_for_admin_pin":
                return await handler(event, data)
                
        user_id = event.from_user.id
        
        # Only process for OWNER_ID (though IsOwner also filters it)
        if user_id != OWNER_ID:
            return await handler(event, data)
            
        expired_at = await db.get_admin_session(user_id)
        
        # Jika bukan pesan command /admin dan bukan admin_main, cek session
        if isinstance(event, Message):
            if event.text and event.text.startswith("/admin"):
                # Kita akan biarkan handler admin_panel utama yang mengatur pin prompt
                return await handler(event, data)
                
        if isinstance(event, CallbackQuery):
            if event.data == "admin_main":
                # Kita biarkan handler admin_main utama yang mengatur pin prompt
                return await handler(event, data)
                
        # Untuk semua admin action lainnya, block jika expired
        if expired_at <= time.time():
            if isinstance(event, CallbackQuery):
                await event.answer("Sesi login admin telah habis. Silakan ketik /admin", show_alert=True)
            elif isinstance(event, Message):
                await event.answer("Sesi login admin telah habis. Silakan ketik /admin")
            return # Block update
            
        return await handler(event, data)
