import asyncio
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError, TelegramBadRequest, TelegramAPIError
import database.db as db

async def start_broadcast(bot: Bot, admin_id: int, message_to_copy_from_id: int, message_to_copy_chat_id: int):
    users = await db.get_all_users()
    success = 0
    failed = 0
    
    status_msg = await bot.send_message(admin_id, "🔄 Memulai broadcast secara asynchronous...")
    
    for uid in users:
        try:
            await bot.copy_message(chat_id=uid, from_chat_id=message_to_copy_chat_id, message_id=message_to_copy_from_id)
            success += 1
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            try:
                await bot.copy_message(chat_id=uid, from_chat_id=message_to_copy_chat_id, message_id=message_to_copy_from_id)
                success += 1
            except Exception:
                failed += 1
        except (TelegramForbiddenError, TelegramBadRequest):
            failed += 1
        except TelegramAPIError:
            failed += 1
        except Exception:
            failed += 1
            
        # Delay untuk menghindari limit rate Telegram (1 pesan ~0.05s setara dengan max 20 msgs per detik)
        await asyncio.sleep(0.05)
        
        # Update progress periodik
        if (success + failed) % 100 == 0:
            try:
                await bot.edit_message_text(f"🔄 Progress Broadcast: {success + failed}/{len(users)}", chat_id=admin_id, message_id=status_msg.message_id)
            except Exception:
                pass
                
    await bot.edit_message_text(f"✅ *Broadcast Selesai*\n\nBerhasil: `{success}`\nGagal: `{failed}`", chat_id=admin_id, message_id=status_msg.message_id, parse_mode="Markdown")
