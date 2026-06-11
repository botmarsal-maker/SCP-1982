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
        [InlineKeyboardButton(text="📜 Kelola Aturan", callback_data="admin_rules")],
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

