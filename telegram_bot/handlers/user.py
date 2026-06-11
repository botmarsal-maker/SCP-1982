from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.enums import ChatMemberStatus

from config import OWNER_ID, CHANNEL_ID
from database import db
from keyboards import inline
from database.cache import fs_cache

router = Router()

async def check_force_sub(user_id: int, bot) -> bool:
    fs_status = await db.get_setting("force_sub")
    if fs_status != "1":
        return True
    
    fs_channel = await db.get_setting("fs_channel")
    if not fs_channel:
        return True
        
    # Gunakan cache memori untuk durasi 10 menit guna mengurangi rate limit Telegram (Prioritas 7)
    if fs_cache.is_cached_valid(user_id):
        return True
        
    try:
        # Check membership uses channel ID or username
        member = await bot.get_chat_member(chat_id=fs_channel, user_id=user_id)
        if member.status in [ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED]:
            fs_cache.set_valid(user_id) # Simpan dalam cache
            return True
        return False
    except Exception as e:
        # Jika bot bukan admin channel atau channel tidak ada.
        print(f"FS Check Error: {e}")
        return False

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)
    await db.add_user(user_id, username)
    
    maintenance = await db.get_setting("maintenance")
    if maintenance == "1" and user_id != OWNER_ID:
        await message.answer("🚧 Bot sedang dalam masa perbaikan (maintenance). Silakan coba lagi nanti.")
        return

    is_subbed = await check_force_sub(user_id, message.bot)
    if not is_subbed:
        fs_channel = await db.get_setting("fs_channel")
        fs_msg = await db.get_setting("fs_msg")
        link = fs_channel if fs_channel.startswith("http") else f"https://t.me/{fs_channel.replace('@', '')}"
        await message.answer(fs_msg, reply_markup=inline.fs_keyboard(link))
        return

    welcome_msg = await db.get_setting("welcome_msg")
    await message.answer(welcome_msg)

@router.callback_query(F.data == "check_fs")
async def verify_fs(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_subbed = await check_force_sub(user_id, callback.bot)
    
    if is_subbed:
        await callback.message.delete()
        welcome_msg = await db.get_setting("welcome_msg")
        await callback.message.answer(f"✅ Terima kasih telah join channel!\n\n{welcome_msg}")
    else:
        await callback.answer("❌ Anda belum join channel. Silakan join terlebih dahulu.", show_alert=True)

@router.message()
async def process_menfess(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)
    
    if message.text and message.text.startswith('/'):
        return # Ignore other commands
        
    maintenance = await db.get_setting("maintenance")
    if maintenance == "1" and user_id != OWNER_ID:
        await message.answer("🚧 Bot sedang dalam masa perbaikan (maintenance).")
        return

    is_subbed = await check_force_sub(user_id, message.bot)
    if not is_subbed:
        fs_channel = await db.get_setting("fs_channel")
        fs_msg = await db.get_setting("fs_msg")
        link = fs_channel if fs_channel.startswith("http") else f"https://t.me/{fs_channel.replace('@', '')}"
        await message.answer(fs_msg, reply_markup=inline.fs_keyboard(link))
        return
        
    prefix = await db.get_setting("prefix")
    content = ""
    msg_type = "text"
    
    # Validasi Prefix (Pesan harus diawali dengan prefix secara manual oleh pengguna)
    user_text = message.text or message.caption or ""
    if not user_text.strip().lower().startswith(prefix.lower()):
        await message.answer(f"❌ *Pesan Ditolak!*\n\nPesan kamu harus diawali dengan prefix: `{prefix}`", parse_mode="Markdown")
        return
    
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
            await message.answer("✅ Menfess berhasil dikirim ke channel!")
            
    except Exception as e:
        await message.answer("❌ Gagal mengirim pesan ke channel. Pastikan bot adalah admin di channel tersebut.")
        print(f"Error send menfess: {e}")
