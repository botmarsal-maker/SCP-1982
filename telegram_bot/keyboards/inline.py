from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def fs_keyboard(channel_link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Gabung Channel", url=channel_link)],
        [InlineKeyboardButton(text="✅ Cek Keanggotaan", callback_data="check_fs")]
    ])

def admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🚀 Ubah Prefix", callback_data="admin_prefix")],
        [InlineKeyboardButton(text="🔒 Force Sub", callback_data="admin_fs")],
        [InlineKeyboardButton(text="🤖 Force Bot", callback_data="admin_fbot")],
        [InlineKeyboardButton(text="📜 Kelola Aturan", callback_data="admin_rules")],
        [InlineKeyboardButton(text="⚙️ Pengaturan", callback_data="admin_settings")],
        [InlineKeyboardButton(text="📊 Statistik", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📝 10 Log Terakhir", callback_data="admin_logs")],
        [InlineKeyboardButton(text="🔒 Logout Admin", callback_data="admin_logout")]
    ])

def fs_settings_keyboard(fs_status: str) -> InlineKeyboardMarkup:
    status_text = "🟢 Aktif" if fs_status == "1" else "🔴 Nonaktif"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Status: {status_text}", callback_data="toggle_fs")],
        [InlineKeyboardButton(text="📢 Kelola Force Subscribe", callback_data="manage_fs")],
        [InlineKeyboardButton(text="🔙 Kembali", callback_data="admin_main")]
    ])

def manage_fs_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Tambah FS", callback_data="add_fs")],
        [InlineKeyboardButton(text="➖ Hapus FS", callback_data="del_fs")],
        [InlineKeyboardButton(text="📋 Daftar FS", callback_data="list_fs")],
        [InlineKeyboardButton(text="🔙 Kembali", callback_data="admin_fs")]
    ])

def delete_fs_keyboard(channels: list) -> InlineKeyboardMarkup:
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(text=f"❌ {ch}", callback_data=f"del_fs_{ch}")])
    buttons.append([InlineKeyboardButton(text="🔙 Kembali", callback_data="manage_fs")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


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

def confirm_broadcast_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Konfirmasi Broadcast", callback_data="confirm_broadcast")],
        [InlineKeyboardButton(text="❌ Batal Broadcast", callback_data="cancel_action")]
    ])

def see_post_keyboard(post_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Lihat Postingan", url=post_url)]
    ])

def comment_notif_keyboard(post_url: str, comment_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Lihat Komentar", url=comment_url)],
        [InlineKeyboardButton(text="🔗 Lihat Postingan", url=post_url)]
    ])

def rules_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📏 Maksimal Karakter", callback_data="rule_max_chars")],
        [InlineKeyboardButton(text="🚫 Filter Kata Kasar", callback_data="rule_badwords")],
        [InlineKeyboardButton(text="🔗 Larangan Link", callback_data="rule_antilink")],
        [InlineKeyboardButton(text="👤 Larangan Username", callback_data="rule_antiusername")],
        [InlineKeyboardButton(text="🚨 Anti Spam", callback_data="rule_antispam")],
        [InlineKeyboardButton(text="📨 Limit Pesan Harian", callback_data="rule_dailylimit")],
        [InlineKeyboardButton(text="🔙 Kembali", callback_data="admin_main")]
    ])

def rule_max_chars_keyboard(enabled: str) -> InlineKeyboardMarkup:
    status = "✅ Aktif" if enabled == "1" else "❌ Nonaktif"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Ubah Batas Karakter", callback_data="set_max_chars")],
        [InlineKeyboardButton(text=status, callback_data="toggle_max_chars")],
        [InlineKeyboardButton(text="🔙 Kembali", callback_data="admin_rules")]
    ])

def rule_badwords_keyboard(enabled: str) -> InlineKeyboardMarkup:
    status = "✅ Aktif" if enabled == "1" else "❌ Nonaktif"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Tambah Kata", callback_data="add_badword"), InlineKeyboardButton(text="➖ Hapus Kata", callback_data="del_badword")],
        [InlineKeyboardButton(text="📋 Lihat Daftar", callback_data="list_badwords")],
        [InlineKeyboardButton(text=status, callback_data="toggle_badwords")],
        [InlineKeyboardButton(text="🔙 Kembali", callback_data="admin_rules")]
    ])

def rule_antilink_keyboard(enabled: str) -> InlineKeyboardMarkup:
    status = "✅ Aktif" if enabled == "1" else "❌ Nonaktif"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=status, callback_data="toggle_antilink")],
        [InlineKeyboardButton(text="🔙 Kembali", callback_data="admin_rules")]
    ])

def rule_antiusername_keyboard(enabled: str) -> InlineKeyboardMarkup:
    status = "✅ Aktif" if enabled == "1" else "❌ Nonaktif"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=status, callback_data="toggle_antiusername")],
        [InlineKeyboardButton(text="🔙 Kembali", callback_data="admin_rules")]
    ])

def rule_antispam_keyboard(enabled: str) -> InlineKeyboardMarkup:
    status = "✅ Aktif" if enabled == "1" else "❌ Nonaktif"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Ubah Cooldown", callback_data="set_antispam_cooldown")],
        [InlineKeyboardButton(text=status, callback_data="toggle_antispam")],
        [InlineKeyboardButton(text="🔙 Kembali", callback_data="admin_rules")]
    ])

def rule_dailylimit_keyboard(enabled: str) -> InlineKeyboardMarkup:
    status = "✅ Aktif" if enabled == "1" else "❌ Nonaktif"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Ubah Limit", callback_data="set_dailylimit")],
        [InlineKeyboardButton(text=status, callback_data="toggle_dailylimit")],
        [InlineKeyboardButton(text="📊 Statistik Penggunaan", callback_data="stats_dailylimit")],
        [InlineKeyboardButton(text="🔙 Kembali", callback_data="admin_rules")]
    ])

def admin_fbot_keyboard(enabled: str) -> InlineKeyboardMarkup:
    status = "✅ Aktif" if enabled == "1" else "❌ Nonaktif"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Ubah Username Bot", callback_data="set_fbot_username")],
        [InlineKeyboardButton(text="✏️ Ubah Durasi Verifikasi", callback_data="set_fbot_duration")],
        [InlineKeyboardButton(text=status, callback_data="toggle_fbot")],
        [InlineKeyboardButton(text="⬅️ Kembali", callback_data="admin_main")]
    ])

