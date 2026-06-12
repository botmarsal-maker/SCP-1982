import time
import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from globals import current_bot_id
from database.clone_db import clone_db
from keyboards import inline
import clone_manager
from filters.is_owner import IsOwner
from middlewares.admin_session import AdminSessionMiddleware

router = Router()
router.message.filter(IsOwner())
router.callback_query.filter(IsOwner())
router.message.middleware(AdminSessionMiddleware())
router.callback_query.middleware(AdminSessionMiddleware())

class CloneState(StatesGroup):
    waiting_for_clone_data = State()
    waiting_for_clone_extend = State()
    waiting_for_clone_suspend = State()
    waiting_for_clone_delete = State()

@router.callback_query(F.data == "manage_clones")
async def manage_clones_menu(callback: CallbackQuery):
    if current_bot_id.get("main") != "main":
        await callback.answer("Hanya bisa diakses di bot utama", show_alert=True)
        return
        
    await callback.message.edit_text("👥 *Kelola Clone Bot*\n\nSilakan pilih menu di bawah ini:", reply_markup=inline.clone_manage_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "clone_create")
async def ask_clone_create(callback: CallbackQuery, state: FSMContext):
    text = (
        "➕ *Buat Clone Baru*\n\n"
        "Kirim detail clone dengan format:\n"
        "`<Bot Token>`\n"
        "`<Owner ID>`\n"
        "`<Durasi Hari>`\n\n"
        "Contoh:\n"
        "`123456:ABCDEF`\n"
        "`987654321`\n"
        "`30`"
    )
    await callback.message.edit_text(text, reply_markup=inline.cancel_keyboard(), parse_mode="Markdown")
    await state.set_state(CloneState.waiting_for_clone_data)

@router.message(CloneState.waiting_for_clone_data)
async def process_clone_create(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("❌ Harap kirimkan pesan teks.")
        return

    await state.clear()
    lines = message.text.strip().split('\n')
    if len(lines) != 3:
        await message.answer("❌ Format salah. Harap kirim 3 baris sesuai format.")
        return
        
    bot_token = lines[0].strip()
    owner_id_str = lines[1].strip()
    duration_str = lines[2].strip()
    
    if not owner_id_str.isdigit() or not duration_str.isdigit():
        await message.answer("❌ Owner ID dan Durasi harus berupa angka.")
        return
        
    owner_id = int(owner_id_str)
    duration_days = int(duration_str)
    bot_id = bot_token.split(':')[0]
    
    try:
        from aiogram import Bot
        test_bot = Bot(token=bot_token)
        me = await test_bot.get_me()
        bot_username = me.username
        await test_bot.session.close()
    except Exception as e:
        await message.answer(f"❌ Token bot tidak valid: {e}")
        return
        
    success = await clone_db.add_clone(bot_token, bot_id, bot_username, owner_id, duration_days)
    if success:
        from bot import dp
        await clone_manager.start_clone(bot_token, bot_id, dp)
        await message.answer(f"✅ Clone bot @{bot_username} berhasil dibuat dan diaktifkan untuk {duration_days} hari!\n\nOwner ID: {owner_id}")
    else:
        await message.answer("❌ Clone bot ini sudah terdaftar di sistem.")

@router.callback_query(F.data == "clone_list")
async def show_clone_list(callback: CallbackQuery):
    clones = await clone_db.get_clones()
    if not clones:
        await callback.message.edit_text("Tidak ada clone terdaftar.", reply_markup=inline.clone_manage_keyboard())
        return
        
    text = "📋 *Daftar Clone Bot*\n\n"
    for c in clones:
        exp_date = datetime.datetime.fromtimestamp(c['expired_at']).strftime('%d/%m/%Y %H:%M')
        text += (
            f"🤖 @{c['bot_username']} (`{c['bot_id']}`)\n"
            f"👤 Owner: `{c['owner_id']}`\n"
            f"📅 Expired: {exp_date}\n"
            f"✅ Status: {c['status']}\n\n"
        )
    
    text = limit_text(text)
    await callback.message.edit_text(text, reply_markup=inline.clone_manage_keyboard(), parse_mode="Markdown")

def limit_text(text, limit=4000):
   return text[:limit]

@router.callback_query(F.data == "clone_extend")
async def ask_clone_extend(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✏️ *Perpanjang Masa Aktif*\n\nKirim dengan format:\n`<Bot ID>`\n`<Jumlah Hari>`\n\nContoh:\n`123456789`\n`30`", reply_markup=inline.cancel_keyboard(), parse_mode="Markdown")
    await state.set_state(CloneState.waiting_for_clone_extend)

@router.message(CloneState.waiting_for_clone_extend)
async def do_clone_extend(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("❌ Harap kirimkan pesan teks.")
        return

    await state.clear()
    lines = message.text.strip().split('\n')
    if len(lines) != 2: return await message.answer("❌ Format salah.")
    bot_id = lines[0].strip()
    days = lines[1].strip()
    
    if not days.isdigit(): return await message.answer("❌ Durasi hari harus angka.")
    
    success = await clone_db.extend_clone(bot_id, int(days))
    if success:
        await message.answer(f"✅ Bot {bot_id} berhasil diperpanjang {days} hari!")
    else:
        await message.answer("❌ Bot tidak ditemukan.")

@router.callback_query(F.data == "clone_suspend")
async def ask_clone_suspend(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ *Suspend/Unsuspend Clone*\n\nKirimkan Bot ID untuk mengubah statusnya (active <-> suspended):", reply_markup=inline.cancel_keyboard(), parse_mode="Markdown")
    await state.set_state(CloneState.waiting_for_clone_suspend)

@router.message(CloneState.waiting_for_clone_suspend)
async def do_clone_suspend(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("❌ Harap kirimkan pesan teks.")
        return

    await state.clear()
    bot_id = message.text.strip()
    
    c = await clone_db.get_clone(bot_id)
    if not c: return await message.answer("❌ Bot tidak ditemukan.")
    
    new_status = 'suspended' if c['status'] == 'active' else 'active'
    await clone_db.update_status(bot_id, new_status)
    
    if new_status == 'suspended':
        await clone_manager.stop_clone(bot_id)
    else:
        from bot import dp
        await clone_manager.start_clone(c['bot_token'], bot_id, dp)
        
    await message.answer(f"✅ Status bot {bot_id} diubah menjadi {new_status}.")

@router.callback_query(F.data == "clone_delete")
async def ask_clone_delete(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🗑 *Hapus Clone*\n\nKirimkan Bot ID untuk Dihapus Secara Permanen (Data terhapus dan bot berhenti):", reply_markup=inline.cancel_keyboard(), parse_mode="Markdown")
    await state.set_state(CloneState.waiting_for_clone_delete)

@router.message(CloneState.waiting_for_clone_delete)
async def do_clone_delete(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("❌ Harap kirimkan pesan teks.")
        return

    await state.clear()
    bot_id = message.text.strip()
    
    c = await clone_db.get_clone(bot_id)
    if not c: return await message.answer("❌ Bot tidak ditemukan.")
    
    await clone_db.delete_clone(bot_id)
    await clone_manager.stop_clone(bot_id)
    import os
    data_dir = os.environ.get("DATA_DIR", ".")
    db_path = os.path.join(data_dir, f"clone_{bot_id}.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    await message.answer(f"✅ Bot {bot_id} berhasil dihapus permanen.")
