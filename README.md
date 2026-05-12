# Wisma Bot - WhatsApp Booking Bot

WhatsApp bot untuk mengelola pemesanan kamar wisma/losmen. Tamu bisa cek ketersediaan, booking, dan lihat harga langsung via chat WhatsApp.

---

## Fitur

- Cek ketersediaan kamar secara real-time
- Pemesanan kamar (booking) dengan form sederhana
- Daftar harga kamar (AC & Non-AC)
- Notifikasi ke pemilik saat ada booking baru
- Konfirmasi/tolak booking oleh pemilik
- Format tanggal Indonesia (DD/MM/YYYY)
- Simpan data booking di SQLite database

---

## Persyaratan

- Python 3.10 atau lebih tinggi
- Termux (versi dari F-Droid - BUKAN dari Play Store)
- WhatsApp (untuk berkomunikasi dengan bot)

---

## Setup Termux (HP Android)

### Langkah 1: Install Termux dari F-Droid

**PENTING:** Download Termux HANYA dari F-Droid, bukan dari Play Store.

Alasan: Play Store versi sudah tidak diperbarui dan bisa menyebabkan masalah kompatibilitas.

1. Buka browser di HP
2. Kunjungi: https://f-droid.org
3. Download aplikasi F-Droid
4. Install F-Droid
5. Buka F-Droid, search "Termux"
6. Install Termux

### Langkah 2: Update Package

Buka Termux, lalu ketik:

```bash
pkg update && pkg upgrade -y
```

Tunggu sampai selesai (bisa beberapa menit).

### Langkah 3: Install Python & Git

```bash
pkg install python git -y
```

### Langkah 4: Clone/Copy Project Files

**Opsi A - Clone dari Git (jika ada repository):**
```bash
git clone https://github.com/username/wisma-bot.git
cd wisma-bot
```

**Opsi B - Copy manual:**
- Jika file ada di HP, copy folder `wisma-bot` ke penyimpanan internal
- Buka Termux, navigasi ke folder tersebut:
  ```bash
  cd /sdcard/wisma-bot
  ```

### Langkah 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Langkah 6: Edit Konfigurasi

Buka file `config.py` untuk mengatur nomor pemilik:

```bash
nano config.py
```

Ubah baris `OWNER_NUMBER` dengan nomor WA kamu:

```python
OWNER_NUMBER = "6281234567890"  # Ganti dengan nomor kamu (format: 62xxx tanpa +)
```

Format nomor: **62** followed by nomor HP (tanpa tanda +)

Contoh:
- Nomor: +62 812 3456 7890
- Isi: 6281234567890

### Langkah 7: Test Bot

```bash
cd wisma-bot  # atau folder tempat file berada
python main.py --test
```

Jika berhasil, akan muncul:

```
==================================================
Wisma Bot - WhatsApp Booking System
==================================================
Mode: TEST (tanpa WhatsApp)
Owner: 6281234567890

Ketik pesan untuk test bot.
Ketik 'menu' untuk lihat menu utama.
Ketik 'exit' untuk keluar.
==================================================
```

---

## Konfigurasi

### File: `config.py`

| Setting | Keterangan | Default |
|---------|------------|---------|
| `OWNER_NUMBER` | Nomor WhatsApp pemilik (format: 62xxx tanpa +) | "6281234567890" |
| `ROOMS` | Daftar kamar (code, type, price) | 6 kamar |
| `DB_NAME` | Nama file database | "wisma.db" |

### Menambah/Mengubah Kamar

Edit bagian `ROOMS` di `config.py`:

```python
ROOMS = [
    {"code": "1A", "type": "AC", "price": 300000},
    {"code": "1", "type": "AC", "price": 300000},
    {"code": "1B", "type": "AC", "price": 250000},
    # Tambah kamar baru di sini
]
```

---

## Cara Pakai untuk Tamu

Tamu bisa mengirim pesan ke nomor bot:

### Menu Utama

Ketik `MENU` atau `1` untuk melihat menu.

### Cek Ketersediaan

Ketik: `1` atau `CEK`

```
Bot akan menampilkan kamar yang tersedia hari ini & besok.
```

### Lihat Harga

Ketik: `3` atau `HARGA`

```
Bot menampilkan daftar harga semua kamar:
❄️ Kamar 1A: Rp300.000/malam
❄️ Kamar 1: Rp300.000/malam
...
```

### Booking Kamar

Ketik: `2` atau `BOOKING`

Ikuti langkah:
1. Masukkan nama lengkap
2. Masukkan tanggal check-in (format: DD/MM/YYYY)
3. Masukkan jumlah malam
4. Pilih kamar

Contoh input:
```
Nama: Budi Santoso
Tanggal: 15/05/2026
Lama: 2
Kamar: 1A
```

Bot akan memberikan konfirmasi dan status "Menunggu konfirmasi pemilik".

### Batalkan Booking

Ketik: `BATAL` kapan saja selama proses booking.

---

## Cara Pakai untuk Pemilik

Pemilik akan mendapat notifikasi WhatsApp setiap ada booking baru.

### Lihat Booking Baru

Booking baru masuk dengan format:
```
📋 BOOKING BARU

ID: #1
Tamu: Budi Santoso
❄️ Kamar 1A (AC)
Check-in: 2026-05-15
Check-out: 2026-05-17
Lama: 2 malam

Estimasi: Rp600.000

Action:
✅ /approve 1 - Terima
❌ /cancel 1 - Tolak
```

### Konfirmasi Booking

Ketik: `/approve [ID/Nama]`

Contoh:
- `/approve 1` - Konfirmasi booking ID #1
- `/approve Budi` - Konfirmasi booking atas nama Budi

Bot akan mengirim notifikasi ke tamu bahwa booking diterima.

### Tolak Booking

Ketik: `/cancel [ID/Nama]`

Contoh:
- `/cancel 1` - Tolak booking ID #1
- `/cancel Budi` - Tolak booking atas nama Budi

Bot akan mengirim notifikasi ke tamu bahwa booking dibatalkan.

---

## Test Mode

### Cara Aktivasi

**Opsi 1 - Command line flag:**
```bash
python main.py --test
```

**Opsi 2 - Environment variable:**
```bash
TEST_MODE=1 python main.py
```

### Cara Pakai Test Mode

1. Bot akan menampilkan prompt interaktif
2. Ketik pesan untuk simulate pesan WhatsApp
3. Bot akan memberikan response seperti biasa

Commands khusus di test mode:
- `menu` - Tampilkan menu utama
- `book` - Langsung mulai proses booking
- `clear` - Bersihkan layar
- `exit` - Keluar dari bot

### Contoh Session

```
==================================================
🧪 TEST MODE - Interactive Message Tester
==================================================
Type your messages below to test the bot.

Commands:
  exit  - Quit the bot
  clear - Clear the screen
  menu  - Show main menu
  book  - Start booking flow
--------------------------------------------------

You: 1
Bot: *KAMAR TERSEDIA*

❄️ *AC Rooms:*
   1, 1A, 1B

🌬️ *Non-AC Rooms:*
   1C, 1D, 1E

_Untuk booking, ketik *BOOKING*_

You: 3
Bot: *DAFTAR HARGA KAMAR*

❄️ *AC Rooms:*
   Kamar 1A: Rp300.000/malam
   Kamar 1: Rp300.000/malam
   Kamar 1B: Rp250.000/malam
...

You:
```

---

## Troubleshooting

### Termux Close - Bot Mati

**Masalah:** Bot berhenti ketika Termux di-close atau HP sleep.

**Solusi:**
- Install Termux:Boot dari F-Droid
- Buat file startup script:
  ```bash
  cd ~/.termux
  nano boot
  ```
- Isi dengan:
  ```bash
  cd ~/wisma-bot
  python main.py --test
  ```
- Restart HP, bot akan otomatis jalan

### Import Error

**Masalah:** Error seperti `ModuleNotFoundError`

**Solusi:**
1. Pastikan semua file ada di folder yang sama
2. Install ulang dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Python Version Error

**Masalah:** `Python 3.10+ required`

**Solusi:**
```bash
# Cek versi Python
python --version

# Upgrade Python di Termux
pkg update
pkg install python -y
```

### Bot Tidak Merespons Pesan

**Masalah:** Kirim pesan tapi tidak ada balasan.

**Solusi:**
1. Pastikan bot sedang running di Termux
2. Cek logs untuk error
3. Restart bot:
   ```bash
   # Tekan Ctrl+C untuk stop
   python main.py --test
   ```

### Session Disconnect

**Masalah:** WhatsApp session expired.

**Solusi:**
- Untuk development: gunakan test mode
- Untuk production: perlu implementasi WhatsApp library (wa-js, etc.)

---

## Struktur File

```
wisma-bot/
├── config.py          # Konfigurasi (nomor pemilik, daftar kamar)
├── db.py              # Database operations (SQLite)
├── templates.py       # Template pesan WhatsApp
├── handlers.py        # Logic penanganan pesan
├── main.py            # Entry point, bot initialization
├── requirements.txt   # Python dependencies
└── wisma.db           # Database file (dibuat otomatis)
```

### Penjelasan File

| File | Fungsi |
|------|--------|
| `config.py` | Menyimpan konfigurasi bot: nomor pemilik, daftar kamar, nama database |
| `db.py` | Operasi database: init, check availability, add/confirm/cancel booking |
| `templates.py` | Template pesan balasan WhatsApp (menu, konfirmasi, notifikasi) |
| `handlers.py` | Logic utama: proses pesan, validasi input, multi-step booking flow |
| `main.py` | Inisialisasi bot, main loop, test mode interface |
| `requirements.txt` | Daftar Python packages yang dibutuhkan |
| `wisma.db` | File SQLite database (dibuat otomatis saat pertama run) |

---

## WhatsApp Integration

### Status Saat Ini

Versi ini **belum terhubung ke WhatsApp**. Tersedia dua opsi:

### Opsi 1: Test Mode (Recommended untuk Development)

```bash
python main.py --test
```

Tidak perlu koneksi WhatsApp. Cocok untuk testing dan development.

### Opsi 2: Full WhatsApp Integration (Butuh Setup Tambahan)

Untuk production, perlu integrate dengan WhatsApp library. Contoh library yang bisa digunakan:

- **wa-js** (JavaScript) - https://github.com/pedroslopez/whatsapp-web.js
- **yowsup** (Python) - https://github.com/nocancode/yowsup
- **Venom Bot** - https://github.com/orkestral/venom

Setup untuk production memerlukan:
1. WhatsApp Web session management
2. QR code scanning untuk authenticate
3. Message webhook handler
4. Production-grade hosting

---

## Tips & Best Practices

1. **Backup Database:**定期 backup file `wisma.db` untuk keamanan data
2. **Update Regular:** Pastikan Termux dan Python selalu update
3. **Monitoring:** Cek logs secara berkala untuk memastikan bot berjalan normal
4. **Owner Number:** Pastikan nomor di config.py sudah benar formatnya

---

## Lisensi

Project ini bebas digunakan dan dimodifikasi.