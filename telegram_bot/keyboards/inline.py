from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def fs_keyboard(channel_link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Join Channel", url=channel_link)],
        [InlineKeyboardButton(text="Cek Keanggotaan", callback_data="check_fs")]
    ])

def admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🚀 Ubah Prefix", callback_data="admin_prefix")],
        [InlineKeyboardButton(text="🔒 Force Sub", callback_data="admin_fs")],
        [InlineKeyboardButton(text="⚙️ Pengaturan", callback_data="admin_settings")],
        [InlineKeyboardButton(text="📊 Statistik", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📝 10 Log Terakhir", callback_data="admin_logs")]
    ])

def fs_settings_keyboard(fs_status: str) -> InlineKeyboardMarkup:
    status_text = "🟢 Aktif" if fs_status == "1" else "🔴 Nonaktif"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Status: {status_text}", callback_data="toggle_fs")],
        [InlineKeyboardButton(text="Ubah Channel FS", callback_data="set_fs_channel")],
        [InlineKeyboardButton(text="🔙 Kembali", callback_data="admin_main")]
    ])

def general_settings_keyboard(maintenance: str) -> InlineKeyboardMarkup:
    mt_text = "🟢 Aktif" if maintenance == "1" else "🔴 Nonaktif"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Maintenance: {mt_text}", callback_data="toggle_mt")],
        [InlineKeyboardButton(text="Ubah Welcome Msg", callback_data="set_welcome")],
        [InlineKeyboardButton(text="Ubah Pesan FS", callback_data="set_fs_msg")],
        [InlineKeyboardButton(text="🗑 Hapus Menfess", callback_data="delete_menfess")],
        [InlineKeyboardButton(text="🔙 Kembali", callback_data="admin_main")]
    ])

def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Batal", callback_data="cancel_action")]
    ])
