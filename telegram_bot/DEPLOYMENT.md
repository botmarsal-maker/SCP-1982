# Panduan Deploy Bot Menfess ke VPS (Ubuntu/Debian)

## 1. Persiapan VPS
Update paket OS dan install dependensi:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv npm sqlite3 -y
```

Install PM2 secara global:
```bash
sudo npm install -g pm2
```

## 2. Setup Project
Upload semua file di dalam folder ini (`telegram_bot`) ke VPS Anda. Misal Anda unggah ke folder `/root/menfess_bot`.

Masuk ke folder project di VPS:
```bash
cd /root/menfess_bot
```

Buat dan aktifkan virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install requirements:
```bash
pip install -r requirements.txt
```

## 3. Konfigurasi
Copy file `.env.example` ke `.env` dan isi datanya:
```bash
cp .env.example .env
nano .env
```
Isi variabel:
- `BOT_TOKEN`: Token dari BotFather.
- `OWNER_ID`: ID Telegram Owner (Bisa didapat dari @userinfobot, harus berupa angka, contoh: `123456789`).
- `CHANNEL_ID`: ID atau Username Channel Tujuan Menfess (contoh: `@channel_menfessku` atau `-100123456789`).

> **PENTING:** Pastikan Bot sudah di-invite ke Channel Anda dan dijadikan **Admin** dengan hak penuh (bisa kirim pesan, hapus pesan, dan tambah user).

## 4. Menjalankan Bot dengan PM2
Buat sebuah file script bash bernama `start.sh` di dalam folder project:
```bash
cat << 'EOF' > start.sh
#!/bin/bash
source venv/bin/activate
python bot.py
EOF
```
Beri izin eksekusi script:
```bash
chmod +x start.sh
```

Mulai bot menggunakan PM2:
```bash
pm2 start start.sh --name "menfess-bot"
```

Simpan konfigurasi PM2 agar bot otomatis nyala kembali saat server restart/reboot:
```bash
pm2 save
pm2 startup
```

## 5. Perintah Berguna PM2
Melihat log bot:
```bash
pm2 logs menfess-bot
```

Melihat status bot:
```bash
pm2 status
```

Merestart bot:
```bash
pm2 restart menfess-bot
```

Menghentikan bot:
```bash
pm2 stop menfess-bot
```
