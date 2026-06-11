import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import OWNER_ID, CHANNEL_ID
from database import db
from keyboards import inline
from filters.is_owner import IsOwner
from services.broadcast import start_broadcast

router = Router()
# Menerapkan IsOwner filter pada skala router (Prioritas 8)
router.message.filter(IsOwner())
router.callback_query.filter(IsOwner())

class AdminState(StatesGroup):
    waiting_for_prefix = State()
    waiting_for_broadcast = State()
    waiting_for_fs_channel = State()
    waiting_for_welcome = State()
    waiting_for_fs_msg = State()
    waiting_for_delete_msg_id = State()
    waiting_for_max_chars = State()
    waiting_for_add_badword = State()
    waiting_for_del_badword = State()
    waiting_for_antispam_cooldown = State()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    await message.answer("🛠 *Admin Panel*", reply_markup=inline.admin_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "admin_main")
async def back_to_admin(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("🛠 *Admin Panel*", reply_markup=inline.admin_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    users_count, logs_count = await db.get_stats()
    prefix = await db.get_setting("prefix")
    fs_status = await db.get_setting("force_sub")
    fs_text = "Aktif" if fs_status == "1" else "Nonaktif"
    
    text = (
        f"📊 *Statistik Bot*\n\n"
        f"👥 Total User: `{users_count}`\n"
        f"💌 Total Menfess: `{logs_count}`\n"
        f"🔒 Force Sub: `{fs_text}`\n"
        f"🚀 Prefix: `{prefix}`\n"
    )
    await callback.message.edit_text(text, reply_markup=inline.cancel_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "admin_logs")
async def admin_logs_view(callback: CallbackQuery):
    logs = await db.get_recent_logs(10)
    if not logs:
        text = "Belum ada log."
    else:
        text = "📝 *10 Menfess Terakhir*\n\n"
        for uid, uname, mtype, sat in logs:
            text += f"- [{uid}] @{uname} : {mtype} ({sat})\n"
    await callback.message.edit_text(text, reply_markup=inline.cancel_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "admin_fs")
async def admin_fs_menu(callback: CallbackQuery):
    fs_status = await db.get_setting("force_sub")
    fs_channel = await db.get_setting("fs_channel")
    text = f"🔒 *Force Subscribe Manager*\n\nChannel saat ini: `{fs_channel or 'Belum diset'}`"
    await callback.message.edit_text(text, reply_markup=inline.fs_settings_keyboard(fs_status), parse_mode="Markdown")

@router.callback_query(F.data == "toggle_fs")
async def toggle_fs(callback: CallbackQuery):
    fs_status = await db.get_setting("force_sub")
    new_status = "0" if fs_status == "1" else "1"
    await db.set_setting("force_sub", new_status)
    await admin_fs_menu(callback)

@router.callback_query(F.data == "admin_settings")
async def admin_settings_menu(callback: CallbackQuery):
    mt_status = await db.get_setting("maintenance")
    await callback.message.edit_text("⚙️ *Pengaturan Umum*", reply_markup=inline.general_settings_keyboard(mt_status), parse_mode="Markdown")

@router.callback_query(F.data == "toggle_mt")
async def toggle_mt(callback: CallbackQuery):
    mt_status = await db.get_setting("maintenance")
    new_status = "0" if mt_status == "1" else "1"
    await db.set_setting("maintenance", new_status)
    await admin_settings_menu(callback)

@router.callback_query(F.data == "admin_prefix")
async def ask_prefix(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Kirimkan teks/emoji untuk prefix baru:", reply_markup=inline.cancel_keyboard())
    await state.set_state(AdminState.waiting_for_prefix)

@router.message(AdminState.waiting_for_prefix)
async def set_prefix(message: Message, state: FSMContext):
    await db.set_setting("prefix", message.text)
    await state.clear()
    await message.answer("✅ Prefix berhasil diubah!", reply_markup=inline.InlineKeyboardMarkup(inline_keyboard=[[inline.InlineKeyboardButton(text="🔙 Kembali", callback_data="admin_main")]]))

@router.callback_query(F.data == "set_fs_channel")
async def ask_fs_channel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Kirimkan username/link channel untuk Force Subscribe (contoh: @mychannel atau https://t.me/mychannel):", reply_markup=inline.cancel_keyboard())
    await state.set_state(AdminState.waiting_for_fs_channel)

@router.message(AdminState.waiting_for_fs_channel)
async def set_fs_channel(message: Message, state: FSMContext):
    await db.set_setting("fs_channel", message.text)
    await state.clear()
    await message.answer("✅ Channel Force Subscribe berhasil diubah!", reply_markup=inline.InlineKeyboardMarkup(inline_keyboard=[[inline.InlineKeyboardButton(text="🔙 Kembali", callback_data="admin_main")]]))

@router.callback_query(F.data == "set_welcome")
async def ask_welcome(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Kirimkan pesan welcome yang baru:", reply_markup=inline.cancel_keyboard())
    await state.set_state(AdminState.waiting_for_welcome)

@router.message(AdminState.waiting_for_welcome)
async def set_welcome(message: Message, state: FSMContext):
    await db.set_setting("welcome_msg", message.text)
    await state.clear()
    await message.answer("✅ Pesan welcome berhasil diubah!", reply_markup=inline.InlineKeyboardMarkup(inline_keyboard=[[inline.InlineKeyboardButton(text="🔙 Kembali", callback_data="admin_main")]]))

@router.callback_query(F.data == "set_fs_msg")
async def ask_fs_msg(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Kirimkan pesan Force Subscribe yang baru:", reply_markup=inline.cancel_keyboard())
    await state.set_state(AdminState.waiting_for_fs_msg)

@router.message(AdminState.waiting_for_fs_msg)
async def set_fs_msg(message: Message, state: FSMContext):
    await db.set_setting("fs_msg", message.text)
    await state.clear()
    await message.answer("✅ Pesan Force Subscribe berhasil diubah!", reply_markup=inline.InlineKeyboardMarkup(inline_keyboard=[[inline.InlineKeyboardButton(text="🔙 Kembali", callback_data="admin_main")]]))

@router.callback_query(F.data == "cancel_action")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Aksi dibatalkan.", reply_markup=inline.InlineKeyboardMarkup(inline_keyboard=[[inline.InlineKeyboardButton(text="🔙 Kembali", callback_data="admin_main")]]))

@router.callback_query(F.data == "admin_broadcast")
async def ask_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Kirimkan pesan broadcast (Text/Foto/Video/Dokumen):", reply_markup=inline.cancel_keyboard())
    await state.set_state(AdminState.waiting_for_broadcast)

@router.message(AdminState.waiting_for_broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    await state.clear()
    # Mengirim broadcast ke background task agar tidak stall proses utama (Prioritas 1)
    asyncio.create_task(start_broadcast(message.bot, message.from_user.id, message.message_id, message.chat.id))

@router.callback_query(F.data == "delete_menfess")
async def ask_delete_msg(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Kirimkan Message ID dari pesan di channel yang ingin dihapus:", reply_markup=inline.cancel_keyboard())
    await state.set_state(AdminState.waiting_for_delete_msg_id)

@router.message(AdminState.waiting_for_delete_msg_id)
async def do_delete_msg(message: Message, state: FSMContext):
    await state.clear()
    try:
        msg_id = int(message.text)
        await message.bot.delete_message(chat_id=CHANNEL_ID, message_id=msg_id)
        await message.answer("✅ Pesan berhasil dihapus dari channel!", reply_markup=inline.InlineKeyboardMarkup(inline_keyboard=[[inline.InlineKeyboardButton(text="🔙 Kembali", callback_data="admin_main")]]))
    except ValueError:
        await message.answer("❌ Message ID harus berupa angka.")
    except Exception as e:
        await message.answer(f"❌ Gagal menghapus pesan. Error: {e}")

# ================= KELOLA ATURAN =================

@router.callback_query(F.data == "admin_rules")
async def admin_rules_menu(callback: CallbackQuery):
    await callback.message.edit_text("📜 *Kelola Aturan*", reply_markup=inline.rules_menu_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "rule_max_chars")
async def rule_max_chars_menu(callback: CallbackQuery):
    enabled = await db.get_setting("max_chars_enabled")
    limit = await db.get_setting("max_chars_limit")
    text = f"📏 *Maksimal Karakter*\n\nStatus saat ini:\nMaksimal Karakter: `{limit}`"
    await callback.message.edit_text(text, reply_markup=inline.rule_max_chars_keyboard(enabled), parse_mode="Markdown")

@router.callback_query(F.data == "toggle_max_chars")
async def toggle_max_chars(callback: CallbackQuery):
    enabled = await db.get_setting("max_chars_enabled")
    new_val = "0" if enabled == "1" else "1"
    await db.set_setting("max_chars_enabled", new_val)
    await rule_max_chars_menu(callback)

@router.callback_query(F.data == "set_max_chars")
async def ask_max_chars(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Kirimkan batas maksimal karakter baru (angka):", reply_markup=inline.cancel_keyboard())
    await state.set_state(AdminState.waiting_for_max_chars)

@router.message(AdminState.waiting_for_max_chars)
async def do_set_max_chars(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Harap masukkan angka yang valid.")
        return
    await db.set_setting("max_chars_limit", message.text)
    await state.clear()
    await message.answer("✅ Batas karakter berhasil diubah!", reply_markup=inline.InlineKeyboardMarkup(inline_keyboard=[[inline.InlineKeyboardButton(text="🔙 Kembali", callback_data="rule_max_chars")]]))

@router.callback_query(F.data == "rule_badwords")
async def rule_badwords_menu(callback: CallbackQuery):
    enabled = await db.get_setting("badwords_enabled")
    status_text = "Aktif" if enabled == "1" else "Nonaktif"
    text = f"🚫 *Filter Kata Kasar*\n\nFilter Kata Kasar: `{status_text}`"
    await callback.message.edit_text(text, reply_markup=inline.rule_badwords_keyboard(enabled), parse_mode="Markdown")

@router.callback_query(F.data == "toggle_badwords")
async def toggle_badwords(callback: CallbackQuery):
    enabled = await db.get_setting("badwords_enabled")
    new_val = "0" if enabled == "1" else "1"
    await db.set_setting("badwords_enabled", new_val)
    await rule_badwords_menu(callback)

@router.callback_query(F.data == "add_badword")
async def ask_add_badword(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Kirimkan kata kasar yang ingin ditambahkan:", reply_markup=inline.cancel_keyboard())
    await state.set_state(AdminState.waiting_for_add_badword)

@router.message(AdminState.waiting_for_add_badword)
async def do_add_badword(message: Message, state: FSMContext):
    word = message.text.strip().lower()
    success = await db.add_badword(word)
    await state.clear()
    if success:
        await message.answer("✅ Kata berhasil ditambahkan!", reply_markup=inline.InlineKeyboardMarkup(inline_keyboard=[[inline.InlineKeyboardButton(text="🔙 Kembali", callback_data="rule_badwords")]]))
    else:
        await message.answer("❌ Kata sudah ada di daftar.", reply_markup=inline.InlineKeyboardMarkup(inline_keyboard=[[inline.InlineKeyboardButton(text="🔙 Kembali", callback_data="rule_badwords")]]))

@router.callback_query(F.data == "del_badword")
async def ask_del_badword(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Kirimkan kata kasar yang ingin dihapus:", reply_markup=inline.cancel_keyboard())
    await state.set_state(AdminState.waiting_for_del_badword)

@router.message(AdminState.waiting_for_del_badword)
async def do_del_badword(message: Message, state: FSMContext):
    word = message.text.strip().lower()
    await db.remove_badword(word)
    await state.clear()
    await message.answer("✅ Kata berhasil dihapus (jika ada).", reply_markup=inline.InlineKeyboardMarkup(inline_keyboard=[[inline.InlineKeyboardButton(text="🔙 Kembali", callback_data="rule_badwords")]]))

@router.callback_query(F.data == "list_badwords")
async def list_badwords(callback: CallbackQuery):
    words = await db.get_all_badwords()
    if not words:
        text = "Daftar kata kasar kosong."
    else:
        text = "📋 *Daftar Kata Kasar:*\n\n" + ", ".join(words)
    await callback.message.edit_text(text, reply_markup=inline.InlineKeyboardMarkup(inline_keyboard=[[inline.InlineKeyboardButton(text="🔙 Kembali", callback_data="rule_badwords")]]), parse_mode="Markdown")

@router.callback_query(F.data == "rule_antilink")
async def rule_antilink_menu(callback: CallbackQuery):
    enabled = await db.get_setting("anti_link_enabled")
    status = "Aktif" if enabled == "1" else "Nonaktif"
    text = f"🔗 *Larangan Link*\n\nLarangan Link: `{status}`"
    await callback.message.edit_text(text, reply_markup=inline.rule_antilink_keyboard(enabled), parse_mode="Markdown")

@router.callback_query(F.data == "toggle_antilink")
async def toggle_antilink(callback: CallbackQuery):
    enabled = await db.get_setting("anti_link_enabled")
    new_val = "0" if enabled == "1" else "1"
    await db.set_setting("anti_link_enabled", new_val)
    await rule_antilink_menu(callback)

@router.callback_query(F.data == "rule_antiusername")
async def rule_antiusername_menu(callback: CallbackQuery):
    enabled = await db.get_setting("anti_username_enabled")
    status = "Aktif" if enabled == "1" else "Nonaktif"
    text = f"👤 *Larangan Username*\n\nLarangan @Username: `{status}`"
    await callback.message.edit_text(text, reply_markup=inline.rule_antiusername_keyboard(enabled), parse_mode="Markdown")

@router.callback_query(F.data == "toggle_antiusername")
async def toggle_antiusername(callback: CallbackQuery):
    enabled = await db.get_setting("anti_username_enabled")
    new_val = "0" if enabled == "1" else "1"
    await db.set_setting("anti_username_enabled", new_val)
    await rule_antiusername_menu(callback)

@router.callback_query(F.data == "rule_antispam")
async def rule_antispam_menu(callback: CallbackQuery):
    enabled = await db.get_setting("anti_spam_enabled")
    cooldown = await db.get_setting("anti_spam_cooldown")
    status = "Aktif" if enabled == "1" else "Nonaktif"
    text = f"🚨 *Anti Spam*\n\nAnti Spam: `{status}`\nCooldown: `{cooldown} detik`"
    await callback.message.edit_text(text, reply_markup=inline.rule_antispam_keyboard(enabled), parse_mode="Markdown")

@router.callback_query(F.data == "toggle_antispam")
async def toggle_antispam(callback: CallbackQuery):
    enabled = await db.get_setting("anti_spam_enabled")
    new_val = "0" if enabled == "1" else "1"
    await db.set_setting("anti_spam_enabled", new_val)
    await rule_antispam_menu(callback)

@router.callback_query(F.data == "set_antispam_cooldown")
async def ask_antispam_cooldown(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Kirimkan waktu cooldown baru (dalam detik, misal 10):", reply_markup=inline.cancel_keyboard())
    await state.set_state(AdminState.waiting_for_antispam_cooldown)

@router.message(AdminState.waiting_for_antispam_cooldown)
async def do_set_antispam_cooldown(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Harap masukkan angka yang valid.")
        return
    await db.set_setting("anti_spam_cooldown", message.text)
    await state.clear()
    await message.answer("✅ Cooldown berhasil diubah!", reply_markup=inline.InlineKeyboardMarkup(inline_keyboard=[[inline.InlineKeyboardButton(text="🔙 Kembali", callback_data="rule_antispam")]]))
