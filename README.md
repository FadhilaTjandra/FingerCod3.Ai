# 🎬 Framework Universal Niche V1.5 Bot
**Build by Fingercod3**

Bot Telegram & Discord untuk menjalankan Framework Universal Niche V1.5 —
generator prompt timelapse video/image profesional berbasis AI (Claude).

---

## 📁 Struktur Project

```
framework-bot/
├── main.py                  # Entry point — jalankan kedua bot sekaligus
├── requirements.txt         # Python dependencies
├── Procfile                 # Railway deployment
├── railway.json             # Railway config
├── .env.example             # Template environment variables
├── .gitignore
└── src/
    ├── system_prompt.py     # Framework V1.5 sebagai system prompt Claude
    ├── session.py           # Session manager (Redis / in-memory fallback)
    ├── ai_handler.py        # Claude API handler + rate limiter
    ├── telegram_bot.py      # Telegram bot
    └── discord_bot.py       # Discord bot
```

---

## ⚡ Quick Start

### 1. Clone & Install

```bash
git clone <your-repo>
cd framework-bot

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Konfigurasi .env

```bash
cp .env.example .env
```

Edit `.env` dan isi:

```env
TELEGRAM_TOKEN=your_telegram_bot_token
DISCORD_TOKEN=your_discord_bot_token
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 3. Jalankan

```bash
# Dari root folder project
python main.py
```

---

## 🔑 Cara Mendapatkan Token

### Telegram Bot Token
1. Buka Telegram, cari `@BotFather`
2. Ketik `/newbot`
3. Ikuti instruksi, salin token yang diberikan

### Discord Bot Token
1. Buka https://discord.com/developers/applications
2. Klik **New Application** → beri nama
3. Menu kiri: **Bot** → **Reset Token** → salin token
4. Di menu **Bot**: aktifkan **Message Content Intent**
5. Menu kiri: **OAuth2 → URL Generator**
   - Scopes: `bot`
   - Bot Permissions: `Send Messages`, `Read Message History`, `Read Messages/View Channels`
6. Salin URL yang dihasilkan → buka di browser → invite bot ke server

### Anthropic API Key
1. Buka https://console.anthropic.com
2. Menu **API Keys** → **Create Key**
3. Salin key (hanya tampil sekali)

---

## 🔒 Konfigurasi Akses (Komunitas Privat)

### Telegram — Whitelist Grup
```env
# Cara cek group ID:
# 1. Tambah @getidsbot ke grup kamu
# 2. Ketik /id — bot akan reply dengan group ID
# Format: -100XXXXXXXXXX (angka negatif)
ALLOWED_GROUP_IDS=-100123456789,-100987654321
```

### Discord — Whitelist Server
```env
# Cara cek Server ID:
# 1. Aktifkan Developer Mode: Settings > App Settings > Advanced > Developer Mode
# 2. Right-click nama server > Copy Server ID
ALLOWED_GUILD_IDS=1234567890123456789
```

> Kosongkan variabel akses untuk membuka bot ke semua chat/server.

---

## 🤖 Cara Pakai Bot

### Memulai Sesi
Ketik `START` atau `MULAI` di chat/server

### Perintah Iterasi (Dalam Sesi)
| Perintah | Fungsi |
|----------|--------|
| `REVISI STAGE [N]` | Generate ulang stage N |
| `GANTI ANGLE` | Ubah angle kamera |
| `GANTI STYLE` | Ubah style karakter |
| `GANTI LOKASI` | Ubah lokasi/setting |
| `TAMBAH STAGE` | Sisipkan stage baru |
| `HAPUS STAGE [N]` | Hapus stage N |
| `GANTI CINEMATIC` | Ubah pilihan cinematic A/B/C |
| `GANTI FORMAT` | Ubah TEXT/JSON output |
| `GANTI TIMELAPSE` | Ubah gaya timelapse |
| `AKTIFKAN LED` | Aktifkan LED mode |
| `NONAKTIFKAN LED` | Nonaktifkan LED mode |
| `ULANG SEMUA` | Generate ulang dari awal |

### Bot Commands
| Command | Telegram | Discord |
|---------|----------|---------|
| Start/info | `/start` | — |
| Reset sesi | `/reset` | `!reset` |
| Bantuan | `/help` | `!help` |
| Status sesi | `/status` | `!status` |

---

## ☁️ Deploy ke Railway (Rekomendasi)

### Cara Deploy
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Init project (dari folder framework-bot)
railway init

# Deploy
railway up
```

### Set Environment Variables di Railway
1. Buka dashboard Railway → project kamu
2. Tab **Variables**
3. Tambahkan semua variable dari `.env.example`
4. Tambahkan Redis: **+ New** → **Database** → **Redis**
5. Railway otomatis inject `REDIS_URL`

### Estimasi Biaya Railway
| Komponen | Biaya/bulan |
|----------|-------------|
| Worker (512MB RAM) | ~$5 |
| Redis Plugin | ~$0–3 |
| **Total hosting** | **~$5–8** |

> Biaya Claude API terpisah (~$5–15/bulan untuk komunitas kecil 500 msg/hari)

---

## 🔧 Konfigurasi Lanjutan

### Ganti Model Claude
```env
# Lebih hemat (lebih cepat, kualitas sedikit lebih rendah)
CLAUDE_MODEL=claude-haiku-4-5-20251001

# Default (kualitas terbaik)
CLAUDE_MODEL=claude-sonnet-4-6
```

### Rate Limiting
```env
# Minimum detik antara pesan per user (default: 3)
RATE_LIMIT_SEC=5
```

### Channel Restriction Discord
```env
# Batasi bot hanya aktif di channel tertentu
# Right-click channel > Copy Channel ID
ALLOWED_CHANNEL_IDS=1234567890,9876543210
```

---

## 🛠️ Troubleshooting

**Bot tidak merespons di Telegram**
- Pastikan `TELEGRAM_TOKEN` sudah benar
- Cek apakah `ALLOWED_GROUP_IDS` sudah include group ID yang benar
- Lihat log: `python main.py` dan perhatikan output

**Bot tidak merespons di Discord**
- Pastikan **Message Content Intent** sudah diaktifkan di Discord Developer Portal
- Pastikan bot sudah diinvite dengan permission yang benar
- Cek `ALLOWED_GUILD_IDS` sudah include server ID yang benar

**Error Redis**
- Bot akan otomatis fallback ke in-memory jika Redis tidak tersedia
- Data sesi tidak persistent jika menggunakan in-memory (reset saat bot restart)
- Install Redis lokal: `brew install redis` (Mac) atau `sudo apt install redis` (Linux)

**Response terpotong**
- Normal — pesan panjang dipecah otomatis dengan indicator [1/N], [2/N]
- Kurangi `MAX_TOKENS` jika ingin respons lebih pendek

---

## 📄 Lisensi
Framework Universal Niche V1.5 — Build by Fingercod3
Hak cipta dilindungi. Dilarang mendistribusikan ulang tanpa izin.
