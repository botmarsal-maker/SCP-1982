from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatMemberStatus
from typing import Callable, Dict, Any, Awaitable
from database import db
from database.cache import fs_cache
import logging
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

class ForceSubscribeMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        # Only process Message and CallbackQuery from private chats (for standard user)
        # We skip if it's an admin command or group message where not applicable
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, data)
            
        user = event.from_user
        if not user:
            return await handler(event, data)
            
        user_id = user.id
        bot = data["bot"]
        
        # Selalu tambahkan user ke DB setiap kali interaksi jika memungkinkan
        username = user.username or str(user_id)
        await db.add_user(user_id, username)
        
        # If admin, just let it pass
        from config import OWNER_ID
        if user_id == OWNER_ID:
            return await handler(event, data)
            
        # Ignore checks if it's the check_fs callback itself
        if isinstance(event, CallbackQuery) and event.data == "check_fs":
            return await handler(event, data)

        fs_status = await db.get_setting("force_sub")
        if fs_status != "1":
            return await handler(event, data)
            
        fs_channel = await db.get_setting("fs_channel")
        if not fs_channel:
            return await handler(event, data)

        if fs_cache.is_cached_valid(user_id):
            return await handler(event, data)

        clean_chat_id = fs_channel.strip()
        if "t.me/" in clean_chat_id:
            part = clean_chat_id.split("t.me/")[-1]
            if not part.startswith("+") and not part.startswith("joinchat/"):
                clean_chat_id = "@" + part
        elif not clean_chat_id.startswith("@") and not clean_chat_id.lstrip("-").isdigit():
            clean_chat_id = "@" + clean_chat_id

        is_subbed = False
        try:
            member = await bot.get_chat_member(chat_id=clean_chat_id, user_id=user_id)
            if member.status in [ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
                fs_cache.set_valid(user_id)
                is_subbed = True
            else:
                fs_cache.invalidate(user_id)
        except Exception as e:
            logging.error(f"FS Check Middleware Error in {clean_chat_id} for user {user_id}: {e}")
            is_subbed = False

        if not is_subbed:
            fs_msg = await db.get_setting("fs_msg") or "❌ Anda harus bergabung ke channel terlebih dahulu untuk menggunakan bot ini."
            link = fs_channel if fs_channel.startswith("http") else f"https://t.me/{fs_channel.replace('@', '')}"
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📢 Gabung Channel", url=link)],
                [InlineKeyboardButton(text="✅ Cek Keanggotaan", callback_data="check_fs")]
            ])
            
            if isinstance(event, Message):
                await event.answer(fs_msg, reply_markup=keyboard)
            elif isinstance(event, CallbackQuery):
                await event.message.answer(fs_msg, reply_markup=keyboard)
                await event.answer("Anda harus bergabung ke channel.", show_alert=True)
            return # Stop processing
            
        return await handler(event, data)
