from aiogram import Router, F
from aiogram.types import Message, MessageOriginChannel
from config import OWNER_IDS, CHANNEL_ID
from database import db
from keyboards import inline
import logging

router = Router()

def get_message_url(chat_id: str | int, message_id: int) -> str:
    chat_id_str = str(chat_id)
    if chat_id_str.startswith("@"):
        return f"https://t.me/{chat_id_str[1:]}/{message_id}"
    elif chat_id_str.startswith("-100"):
        return f"https://t.me/c/{chat_id_str[4:]}/{message_id}"
    else:
        return f"https://t.me/c/{chat_id_str.strip('-')}/{message_id}"

@router.message(F.chat.type.in_({"group", "supergroup"}))
async def handle_comment(message: Message):
    # Cek apakah message ini adalah sebuah balasan (komentar) ke pesan "linked channel"
    if not message.reply_to_message:
        return
        
    origin = message.reply_to_message.forward_origin
    if not origin or not isinstance(origin, MessageOriginChannel):
        # Bukan berasal dari forward channel (mungkin reply ke pesan komentar lain)
        return
        
    channel_msg_id = origin.message_id
    
    # Filter notifikasi (Fitur 5)
    if message.from_user and message.from_user.is_bot:
        return
        
    if message.from_user and message.from_user.id == 777000: # Anonymous Telegram system
        return
        
    menfess_owner_id = await db.get_menfess_owner(channel_msg_id)
    if not menfess_owner_id:
        return
        
    # Jangan kirim notif jika komentator adalah pemilik menfess itu sendiri
    if message.from_user and message.from_user.id == menfess_owner_id:
        return
        
    # Format notifikasi (Fitur 3 & 4)
    name = message.from_user.full_name if message.from_user else (message.sender_chat.title if message.sender_chat else "Anonim")
    comment_text = message.text or message.caption or "Media (Foto/Video/Dokumen/Stiker)"
    
    post_url = get_message_url(CHANNEL_ID, channel_msg_id)
    comment_url = get_message_url(message.chat.id, message.message_id)
    
    import html
    name_escaped = html.escape(name)
    comment_text_escaped = html.escape(comment_text)
    
    notif_text = (
        f"💬 <b>Menfess kamu mendapat komentar baru!</b>\n\n"
        f"👤 <b>Dari:</b>\n{name_escaped}\n\n"
        f"📝 <b>Komentar:</b>\n{comment_text_escaped}"
    )
    
    try:
        await message.bot.send_message(
            chat_id=menfess_owner_id,
            text=notif_text,
            reply_markup=inline.comment_notif_keyboard(post_url, comment_url),
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Gagal mengirim notif komentar ke {menfess_owner_id}: {e}")
