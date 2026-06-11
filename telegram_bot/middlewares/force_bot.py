from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject, InlineKeyboardMarkup, InlineKeyboardButton
from typing import Callable, Dict, Any, Awaitable
from database import db
from config import OWNER_ID
import time
import datetime

class ForceBotMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, data)
            
        user = event.from_user
        if not user:
            return await handler(event, data)
            
        user_id = user.id
        
        # Admin bypass
        if user_id == OWNER_ID:
            return await handler(event, data)
            
        # Ignore checks if it's the verify_bot callback itself or check_fs
        if isinstance(event, CallbackQuery) and event.data in ["verify_bot", "check_fs"]:
            return await handler(event, data)

        fbot_enabled = await db.get_setting("force_bot_enabled")
        if fbot_enabled != "1":
            return await handler(event, data)
            
        fbot_duration_str = await db.get_setting("force_bot_duration")
        try:
            fbot_duration = int(fbot_duration_str)
        except:
            fbot_duration = 24
            
        fbot_username = await db.get_setting("force_bot_username")
        if not fbot_username:
            return await handler(event, data)
            
        # Check verification time
        verified_at = await db.get_bot_verification(user_id)
        current_time = time.time()
        
        is_verified = False
        duration_seconds = fbot_duration * 3600
        if verified_at > 0 and (current_time - verified_at) < duration_seconds:
            is_verified = True
            
        if not is_verified:
            clean_username = fbot_username.strip().replace('@', '')
            link = f"https://t.me/{clean_username}?start=verify"
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🤖 Buka Bot Partner", url=link)],
                [InlineKeyboardButton(text="✅ Saya Sudah Verifikasi", callback_data="verify_bot")]
            ])
            
            if verified_at == 0.0:
                text = "🤖 *Verifikasi Bot Partner*\n\nAkun kamu belum pernah melakukan verifikasi.\n\nSilakan lakukan verifikasi untuk melanjutkan."
            else:
                WIB = datetime.timezone(datetime.timedelta(hours=7))
                dt = datetime.datetime.fromtimestamp(verified_at, WIB)
                dt_string = dt.strftime('%d/%m/%Y %H:%M:%S WIB')
                text = f"🤖 *Verifikasi Bot Partner*\n\nAkun kamu terakhir kirim /start:\n{dt_string}\n\nSilakan lakukan verifikasi ulang untuk melanjutkan."
            
            if isinstance(event, Message):
                await event.answer(text, reply_markup=keyboard, parse_mode="Markdown")
            elif isinstance(event, CallbackQuery):
                await event.message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
                await event.answer("Anda harus verifikasi bot partner.", show_alert=True)
            return # Stop processing
            
        return await handler(event, data)
