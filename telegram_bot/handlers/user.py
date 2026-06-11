from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.enums import ChatMemberStatus

from config import OWNER_ID, CHANNEL_ID
from database import db
from keyboards import inline
from database.cache import fs_cache

router = Router()

import logging
import re
import time
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

user_last_message = {}

async def check_force_sub(user_id: int, bot, use_cache: bool = True) -> bool:
    fs_status = await db.get_setting("force_sub")
    if fs_status != "1":
        return True
    
    fs_channel = await db.get_setting("fs_channel")
    if not fs_channel:
        return True
        
    # Gunakan cache memori untuk durasi 10 menit guna mengurangi rate limit Telegram (Prioritas 7)
    if use_cache and fs_cache.is_cached_valid(user_id):
        return True
        
    # Validasi dan formatting chat_id
    clean_chat_id = fs_channel.strip()
    if "t.me/" in clean_chat_id:
        part = clean_chat_id.split("t.me/")[-1]
        if not part.startswith("+") and not part.startswith("joinchat/"):
            clean_chat_id = "@" + part
    elif not clean_chat_id.startswith("@") and not clean_chat_id.lstrip("-").isdigit():
        clean_chat_id = "@" + clean_chat_id

    try:
        # Check membership uses channel ID or username
        member = await bot.get_chat_member(chat_id=clean_chat_id, user_id=user_id)
        logging.info(f"FS Check: User {user_id} in {clean_chat_id} status is {member.status}")
        
        if member.status in [
            ChatMemberStatus.CREATOR, 
            ChatMemberStatus.ADMINISTRATOR, 
            ChatMemberStatus.MEMBER
        ]:
            fs_cache.set_valid(user_id) # Simpan dalam cache
            return True
        fs_cache.invalidate(user_id)
        return False
    except TelegramBadRequest as e:
        logging.error(f"FS Check TelegramBadRequest for User {user_id} in {clean_chat_id}: {e}")
        return False
    except TelegramForbiddenError as e:
        logging.error(f"FS Check TelegramForbiddenError for User {user_id} in {clean_chat_id}: {e}")
        return False
    except Exception as e:
        # Jika bot bukan admin channel atau channel tidak ada.
        logging.error(f"FS Check Error in {clean_chat_id}: {e}")
        return False

@router.message(CommandStart(), F.chat.type == "private")
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)
    await db.add_user(user_id, username)
    
    maintenance = await db.get_setting("maintenance")
    if maintenance == "1" and user_id != OWNER_ID:
        await message.answer("🚧 Bot sedang dalam masa perbaikan (maintenance). Silakan coba lagi nanti.")
        return

    welcome_msg = await db.get_setting("welcome_msg")
    await message.answer(welcome_msg)

@router.callback_query(F.data == "check_fs")
async def verify_fs(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_subbed = await check_force_sub(user_id, callback.bot, use_cache=False)
    
    if is_subbed:
        try:
            await callback.message.delete()
        except:
            pass
        await callback.message.answer("✅ *Verifikasi berhasil!*\n\nAnda sudah bergabung ke channel dan sekarang dapat menggunakan bot.", parse_mode="Markdown")
    else:
        await callback.answer("❌ Anda belum bergabung ke channel. Silakan join terlebih dahulu.", show_alert=True)

def get_message_url(chat_id: str | int, message_id: int) -> str:
    chat_id_str = str(chat_id)
    if chat_id_str.startswith("@"):
        return f"https://t.me/{chat_id_str[1:]}/{message_id}"
    elif chat_id_str.startswith("-100"):
        return f"https://t.me/c/{chat_id_str[4:]}/{message_id}"
    else:
        return f"https://t.me/c/{chat_id_str.strip('-')}/{message_id}"

@router.message(F.chat.type == "private")
async def process_menfess(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)
    
    if message.text and message.text.startswith('/'):
        return # Ignore other commands
        
    maintenance = await db.get_setting("maintenance")
    if maintenance == "1" and user_id != OWNER_ID:
        await message.answer("🚧 Bot sedang dalam masa perbaikan (maintenance).")
        return

    prefix = await db.get_setting("prefix")
    content = ""
    msg_type = "text"
    
    # Validasi Prefix (Pesan harus diawali dengan prefix secara manual oleh pengguna)
    user_text = message.text or message.caption or ""
    if not user_text.strip().lower().startswith(prefix.lower()):
        await message.answer(f"❌ *Pesan Ditolak!*\n\nPesan kamu harus diawali dengan prefix: `{prefix}`", parse_mode="Markdown")
        return
        
    # --- VALIDASI ATURAN ---
    
    # 1. Anti Spam
    anti_spam_enabled = await db.get_setting("anti_spam_enabled")
    if anti_spam_enabled == "1":
        cooldown = int(await db.get_setting("anti_spam_cooldown") or "10")
        current_time = time.time()
        last_time = user_last_message.get(user_id, 0)
        if current_time - last_time < cooldown:
            wait_time = int(cooldown - (current_time - last_time))
            await message.answer(f"❌ *Pesan Ditolak!*\n\nHarap tunggu {wait_time} detik sebelum mengirim pesan lagi.", parse_mode="Markdown")
            return
        user_last_message[user_id] = current_time
        
    # 2. Maksimal Karakter
    max_chars_enabled = await db.get_setting("max_chars_enabled")
    if max_chars_enabled == "1":
        limit = int(await db.get_setting("max_chars_limit"))
        if len(user_text) > limit:
            await message.answer(f"❌ *Pesan Ditolak!*\n\nPesan kamu melebihi batas karakter ({len(user_text)}/{limit} karakter).", parse_mode="Markdown")
            return
            
    # 3. Filter Kata Kasar
    badwords_enabled = await db.get_setting("badwords_enabled")
    if badwords_enabled == "1":
        badwords = await db.get_all_badwords()
        lower_text = user_text.lower()
        if any(word in lower_text for word in badwords):
            await message.answer("❌ *Pesan Ditolak!*\n\nPesan kamu mengandung kata-kata yang dilarang.", parse_mode="Markdown")
            return
            
    # 4. Larangan Link
    anti_link_enabled = await db.get_setting("anti_link_enabled")
    if anti_link_enabled == "1":
        if re.search(r'(http://|https://|t\.me/|telegram\.me/|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', user_text, re.IGNORECASE):
            await message.answer("❌ *Pesan Ditolak!*\n\nPesan kamu mengandung tautan/link yang dilarang.", parse_mode="Markdown")
            return
            
    # 5. Larangan Username
    anti_username_enabled = await db.get_setting("anti_username_enabled")
    if anti_username_enabled == "1":
        if re.search(r'@[a-zA-Z0-9_]+', user_text):
            await message.answer("❌ *Pesan Ditolak!*\n\nPesan kamu mengandung mention/username yang dilarang.", parse_mode="Markdown")
            return
            
    # 6. Limit Pesan Harian
    import datetime
    from config import OWNER_ID
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    if user_id != OWNER_ID:
        daily_limit_enabled = await db.get_setting("daily_limit_enabled")
        if daily_limit_enabled == "1":
            limit = int(await db.get_setting("daily_limit_count") or "5")
            usage_count = await db.get_daily_usage(user_id, today_str)
            if usage_count >= limit:
                await message.answer(f"❌ *Pesan Ditolak!*\n\nAnda telah mencapai batas pengiriman harian.\nLimit Harian: `{limit} Pesan`\n\nSilakan coba lagi besok.", parse_mode="Markdown")
                return

    # --- END VALIDASI ---
    
    # Helper fungsion untuk membatasi panjang caption dengan aman untuk limit Telegram (Prioritas 3)
    def prep_caption(cap):
        full_cap = cap if cap else ""
        if len(full_cap) > 1024:
             return full_cap[:1021] + "..."
        return full_cap
    
    try:
        sent_msg = None
        if message.text:
            text = message.text
            # Telegram text limit is 4096
            if len(text) > 4096:
                text = text[:4093] + "..."
            sent_msg = await message.bot.send_message(chat_id=CHANNEL_ID, text=text)
            content = message.text
        elif message.photo:
            caption = prep_caption(message.caption)
            sent_msg = await message.bot.send_photo(chat_id=CHANNEL_ID, photo=message.photo[-1].file_id, caption=caption)
            content = message.caption or "Photo"
            msg_type = "photo"
        elif message.video:
            caption = prep_caption(message.caption)
            sent_msg = await message.bot.send_video(chat_id=CHANNEL_ID, video=message.video.file_id, caption=caption)
            content = message.caption or "Video"
            msg_type = "video"
        elif message.document:
            caption = prep_caption(message.caption)
            sent_msg = await message.bot.send_document(chat_id=CHANNEL_ID, document=message.document.file_id, caption=caption)
            content = message.caption or "Document"
            msg_type = "document"
        else:
            await message.answer("Tipe pesan ini belum didukung.")
            return
            
        if sent_msg:
            await db.log_message(user_id, username, msg_type, content, sent_msg.message_id)
            await db.add_menfess_post(user_id, sent_msg.message_id)
            await db.increment_daily_usage(user_id, today_str)
            post_url = get_message_url(CHANNEL_ID, sent_msg.message_id)
            await message.answer(
                "✅ Pesan berhasil dikirim! 🚀\n\nGunakan tombol di bawah untuk melihat postingan Anda.",
                reply_markup=inline.see_post_keyboard(post_url)
            )
            
    except Exception as e:
        await message.answer("❌ Gagal mengirim pesan ke channel. Pastikan bot adalah admin di channel tersebut.")
        print(f"Error send menfess: {e}")
