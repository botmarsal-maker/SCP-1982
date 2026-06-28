from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated
from aiogram.filters import CommandStart
from aiogram.enums import ChatMemberStatus

from config import OWNER_IDS, CHANNEL_ID
from database import db
from keyboards import inline
from database.cache import fs_cache

router = Router()

import logging
import re
import time
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter

user_last_message = {}
last_spam_cleanup = time.time()

async def check_force_sub(user_id: int, bot, use_cache: bool = True) -> bool:
    fs_status = await db.get_setting("force_sub")
    if fs_status != "1":
        return True
    
    channels = await db.get_fs_channels()
    if not channels:
        return True
        
    # Gunakan cache memori untuk durasi 10 menit guna mengurangi rate limit Telegram (Prioritas 7)
    if use_cache and fs_cache.is_cached_valid(user_id):
        return True
        
    all_subbed = True
    for channel in channels:
        # Validasi dan formatting chat_id
        clean_chat_id = channel.strip()
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
            
            if member.status not in [
                ChatMemberStatus.CREATOR, 
                ChatMemberStatus.ADMINISTRATOR, 
                ChatMemberStatus.MEMBER
            ]:
                all_subbed = False
                break # Not subbed to at least one
        except TelegramBadRequest as e:
            logging.error(f"FS Check TelegramBadRequest for User {user_id} in {clean_chat_id}: {e}")
            all_subbed = False
            break
        except TelegramForbiddenError as e:
            logging.error(f"FS Check TelegramForbiddenError for User {user_id} in {clean_chat_id}: {e}")
            all_subbed = False
            break
        except Exception as e:
            # Jika bot bukan admin channel atau channel tidak ada.
            logging.error(f"FS Check Error in {clean_chat_id}: {e}")
            all_subbed = False
            break

    if all_subbed:
        fs_cache.set_valid(user_id)
        return True
    else:
        fs_cache.invalidate(user_id)
        return False

@router.chat_member()
async def on_user_leave_channel(chat_member_updated: ChatMemberUpdated):
    user_id = chat_member_updated.new_chat_member.user.id
    status = chat_member_updated.new_chat_member.status
    if status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED, ChatMemberStatus.RESTRICTED]:
        fs_cache.invalidate(user_id)
        logging.info(f"[FORCESUB CHECK]\nuser_id={user_id}\nchannel_id={chat_member_updated.chat.id}\nstatus={status}")
    else:
        logging.info(f"[FORCESUB CHECK]\nuser_id={user_id}\nchannel_id={chat_member_updated.chat.id}\nstatus={status}")
        
async def send_maintenance_message(message: Message, bot_name: str = "NAMA BOT"):
    end_time = await db.get_setting("maintenance_end_time")
    reason = await db.get_setting("maintenance_reason")
    
    if not reason:
        reason = "Pembaruan sistem"
        
    if end_time:
        import datetime
        try:
            dt = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
            time_str = f"{dt.day} {months[dt.month-1]} {dt.year} • {dt.strftime('%H:%M:%S')}"
        except:
            time_str = end_time
    else:
        time_str = "Belum ditentukan"
        
    try:
        b_name = (await message.bot.get_me()).first_name
        if b_name: bot_name = b_name.upper()
    except:
        pass
        
    msg = (
        f"╭─〔 🤖 {bot_name} 〕\n"
        f"│\n"
        f"├ 🚧 Status:\n"
        f"│   Maintenance\n"
        f"│\n"
        f"├ 🕒 Aktif kembali:\n"
        f"│   {time_str}\n"
        f"│\n"
        f"├ 📝 Alasan:\n"
        f"│   {reason}\n"
        f"│\n"
        f"╰ Mohon maaf atas ketidaknyamanannya."
    )
    await message.answer(msg)

@router.message(CommandStart(), F.chat.type == "private")
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)
    await db.add_user(user_id, username)
    
    maintenance = await db.get_setting("maintenance")
    if maintenance == "1" and user_id not in OWNER_IDS:
        await send_maintenance_message(message)
        return

    welcome_msg = await db.get_setting("welcome_msg")
    await message.answer(welcome_msg)

@router.callback_query(F.data == "check_fs")
async def verify_fs(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    maintenance = await db.get_setting("maintenance")
    if maintenance == "1" and user_id not in OWNER_IDS:
        await callback.answer("🚧 Bot sedang dalam masa perbaikan (maintenance).", show_alert=True)
        return
        
    fs_status = await db.get_setting("force_sub")
    channels = await db.get_fs_channels()

    if fs_status != "1" or not channels:
        try:
            await callback.message.delete()
        except:
            pass
        await callback.message.answer("✅ *Verifikasi berhasil!*\n\nAnda sekarang dapat menggunakan bot.", parse_mode="Markdown")
        return

    all_subbed = True
    status_text = ""
    buttons = []
    
    for idx, channel in enumerate(channels, 1):
        clean_chat_id = channel.strip()
        if "t.me/" in clean_chat_id:
            part = clean_chat_id.split("t.me/")[-1]
            if not part.startswith("+") and not part.startswith("joinchat/"):
                clean_chat_id = "@" + part
        elif not clean_chat_id.startswith("@") and not clean_chat_id.lstrip("-").isdigit():
            clean_chat_id = "@" + clean_chat_id

        is_subbed = False
        try:
            member = await callback.bot.get_chat_member(chat_id=clean_chat_id, user_id=user_id)
            if member.status in [ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
                is_subbed = True
        except Exception as e:
            logging.error(f"FS Check Error in {clean_chat_id} for user {user_id}: {e}")
            is_subbed = False
            
        if not is_subbed:
            all_subbed = False
        
        icon = "✅" if is_subbed else "❌"
        display_name = clean_chat_id if not clean_chat_id.startswith("-100") else f"Channel {idx}"
        status_text += f"📢 {display_name} {icon}\n"
        
        link = channel
        if channel.startswith("http"):
            pass
        elif not channel.lstrip("-").isdigit():
            link = f"https://t.me/{channel.replace('@', '')}"
        else:
            try:
                chat_info = await callback.bot.get_chat(channel.strip())
                link = chat_info.invite_link or (await callback.bot.create_chat_invite_link(channel.strip())).invite_link
            except Exception:
                link = "https://t.me"
                
        buttons.append([inline.InlineKeyboardButton(text=f"📢 Gabung Channel {idx}", url=link)])

    if all_subbed:
        fs_cache.set_valid(user_id)
        try:
            await callback.message.delete()
        except:
            pass
        await callback.message.answer("✅ *Verifikasi berhasil!*\n\nAnda sekarang dapat menggunakan bot.", parse_mode="Markdown")
    else:
        fs_cache.invalidate(user_id)
        custom_fs_msg = await db.get_setting("fs_msg")
        fs_msg = f"{custom_fs_msg}\n\n{status_text}"
        buttons.append([inline.InlineKeyboardButton(text="✅ Cek Keanggotaan", callback_data="check_fs")])
        keyboard = inline.InlineKeyboardMarkup(inline_keyboard=buttons)
        try:
            await callback.message.edit_text(fs_msg, reply_markup=keyboard)
        except Exception:
            pass
        await callback.answer("❌ Anda belum bergabung ke seluruh channel.", show_alert=True)

@router.callback_query(F.data == "verify_bot")
async def handle_verify_bot(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    maintenance = await db.get_setting("maintenance")
    if maintenance == "1" and user_id not in OWNER_IDS:
        await callback.answer("🚧 Bot sedang dalam masa perbaikan (maintenance).", show_alert=True)
        return
        
    verified_at = await db.get_bot_verification(user_id)
    
    fbot_duration_str = await db.get_setting("force_bot_duration")
    try:
        fbot_duration = int(fbot_duration_str)
    except:
        fbot_duration = 24
        
    duration_seconds = fbot_duration * 3600
    if verified_at > 0 and (time.time() - verified_at) < duration_seconds:
        try:
            await callback.message.delete()
        except:
            pass
        await callback.message.answer("✅ Verifikasi berhasil. Silakan gunakan bot kembali.")
    else:
        await callback.answer("❌ Anda belum terverifikasi di sistem kami. Silakan klik tombol Buka Bot Partner dan kirim /start di sana.", show_alert=True)

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
    if maintenance == "1" and user_id not in OWNER_IDS:
        await send_maintenance_message(message)
        return

    prefix_setting = await db.get_setting("prefix")
    prefixes = [p.strip().lower() for p in prefix_setting.split(",") if p.strip()]
    if not prefixes:
        prefixes = ["🚀"] # fallback
        
    content = ""
    msg_type = "text"
    
    # Validasi Prefix (Pesan harus diawali dengan prefix secara manual oleh pengguna)
    user_text = message.text or message.caption or ""
    
    starts_with_prefix = False
    for p in prefixes:
        if user_text.strip().lower().startswith(p):
            starts_with_prefix = True
            break
            
    if not starts_with_prefix:
        formatted_prefixes = " atau ".join([f"`{p}`" for p in prefixes])
        await message.answer(f"❌ *Pesan Ditolak!*\n\nPesan kamu harus diawali dengan prefix: {formatted_prefixes}", parse_mode="Markdown")
        return
        
    # --- VALIDASI ATURAN ---
    
    # 1. Anti Spam
    global last_spam_cleanup
    anti_spam_enabled = await db.get_setting("anti_spam_enabled")
    if anti_spam_enabled == "1":
        cooldown = int(await db.get_setting("anti_spam_cooldown") or "10")
        current_time = time.time()
        
        # Cleanup old entries to prevent memory leak
        if current_time - last_spam_cleanup > 3600:
            last_spam_cleanup = current_time
            to_delete = [uid for uid, t in user_last_message.items() if current_time - t > 3600]
            for uid in to_delete:
                del user_last_message[uid]

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
            
    # 6. Larangan Media
    anti_media_enabled = await db.get_setting("anti_media_enabled")
    if anti_media_enabled == "1":
        if message.photo or message.video or message.document or message.audio or message.voice or message.animation or message.sticker:
            await message.answer("❌ *Pesan Ditolak!*\n\nPengiriman media saat ini dilarang, silakan kirim pesan teks saja.", parse_mode="Markdown")
            return
            
    # 7. Limit Pesan Harian
    import datetime
    from config import OWNER_IDS
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    if user_id not in OWNER_IDS:
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
            
    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        try:
            if message.text:
                sent_msg = await message.bot.send_message(chat_id=CHANNEL_ID, text=message.text[:4093] + "..." if len(message.text) > 4096 else message.text)
            elif message.photo:
                sent_msg = await message.bot.send_photo(chat_id=CHANNEL_ID, photo=message.photo[-1].file_id, caption=prep_caption(message.caption))
            elif message.video:
                sent_msg = await message.bot.send_video(chat_id=CHANNEL_ID, video=message.video.file_id, caption=prep_caption(message.caption))
            elif message.document:
                sent_msg = await message.bot.send_document(chat_id=CHANNEL_ID, document=message.document.file_id, caption=prep_caption(message.caption))
            else:
                sent_msg = None
                
            if sent_msg:
                await db.log_message(user_id, username, msg_type, content, sent_msg.message_id)
                await db.add_menfess_post(user_id, sent_msg.message_id)
                await db.increment_daily_usage(user_id, today_str)
                post_url = get_message_url(CHANNEL_ID, sent_msg.message_id)
                await message.answer(
                    "✅ Pesan berhasil dikirim setelah menunggu delay! 🚀\n\nGunakan tombol di bawah untuk melihat postingan Anda.",
                    reply_markup=inline.see_post_keyboard(post_url)
                )
        except Exception as e2:
            await message.answer("❌ Gagal mengirim pesan ke channel meskipun telah dicoba ulang.")
            print(f"Error retry send menfess: {e2}")
    except Exception as e:
        await message.answer("❌ Gagal mengirim pesan ke channel. Pastikan bot adalah admin di channel tersebut.")
        print(f"Error send menfess: {e}")
