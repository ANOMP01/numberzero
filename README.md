# numberzero

Tool CLI untuk memposting tweet yang sama (teks + gambar/video) dari beberapa
akun X sekaligus. Cocok untuk share event.

---

## Cara Pakai (Ringkas)

Hanya 2 perintah:

```bash
python sessions.py                                    # login & simpan session
python toolsx.py --session -t "Event!" -m poster.jpg  # posting
```

---

## Daftar Isi

1. [Install](#1-install)
2. [Isi daftar email](#2-isi-daftar-email)
3. [Login & simpan session](#3-login--simpan-session)
4. [Posting](#4-posting)
5. [Taruh gambar/video](#5-taruh-gambarvideo)
6. [Mode cepat (flag)](#6-mode-cepat-flag)
7. [Troubleshooting](#7-troubleshooting)
8. [Struktur project](#8-struktur-project)

---

## 1. Install

### Download ZIP (tanpa Git)

1. Buka <https://github.com/ANOMP01/numberzero>
2. Klik **Code** (hijau) → **Download ZIP**
3. Extract → masuk ke folder hasil extract

### Atau via Git

```bash
git clone https://github.com/ANOMP01/numberzero.git
cd numberzero
```

### Install dependensi

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
python -m playwright install chromium
```

---

## 2. Isi daftar email

Buat file `accounts.yaml` dari template:

```bash
copy accounts.example.yaml accounts.yaml    # Windows
# cp accounts.example.yaml accounts.yaml   # Mac/Linux
```

Buka `accounts.yaml`, isi email + password:

```yaml
# Password default untuk semua akun
default_password: "PasswordKamu123"

# Daftar email akun X (satu baris = satu akun)
emails:
  - akun1@gmail.com
  - akun2@gmail.com
  - akun3@gmail.com

# Kalau ada akun yang password-nya beda:
# accounts_custom:
#   - email: akun3@gmail.com
#     password: "PasswordBeda456"
```

**Catatan:**
- Password default sama untuk semua akun (bisa diganti nanti per akun)
- File ini di-`.gitignore` — tidak akan ikut ke-commit
- Nama session otomatis diambil dari bagian sebelum `@` (misal `akun1@gmail.com` → `@akun1`)

---

## 3. Login & simpan session

Jalankan file **`sessions.py`**:

```bash
python sessions.py
```

Tool akan:
1. Baca email dari `accounts.yaml`
2. Buka browser satu per satu
3. Otomatis isi email + password
4. Kalau ada captcha/verifikasi email → selesaikan manual di browser
5. Setelah masuk Home → session tersimpan otomatis
6. Lanjut ke akun berikutnya

**Contoh output:**
```
  sessions.py  |  Login & Simpan Session X
========================================================

Ditemukan 3 email di accounts.yaml:

  • akun1@gmail.com → @akun1
  • akun2@gmail.com → @akun2
  • akun3@gmail.com → @akun3

Password default: ********

Login semua sekarang? [Y/n]: y

[1/3] akun1@gmail.com
  [akun1] Login otomatis: akun1@gmail.com
  Browser akan terbuka...
  [akun1] Session disimpan: sessions/akun1.json
  ✓ @akun1 berhasil!

[2/3] akun2@gmail.com
  ...
  ✓ @akun2 berhasil!

[3/3] akun3@gmail.com
  ...
  ✓ @akun3 berhasil!

--------------------------------------------------------
  Selesai: 3 berhasil, 0 gagal

  Total session tersimpan: 3
    @akun1 (aktif)
    @akun2 (aktif)
    @akun3 (aktif)

  Untuk posting, jalankan:
    python toolsx.py --session
```

### Mode manual (tanpa file email)

```bash
python sessions.py --manual
```
→ Login satu per satu lewat browser, ketik nama akun sendiri.

### Berapa lama session bertahan?

- Aktif dipakai: **1-3 bulan**
- Tidak dipakai: **~30 hari**
- Expired? → jalankan `python sessions.py` lagi

---

## 4. Posting

Jalankan file **`toolsx.py`**:

### Mode interaktif (dipandu menu)
```bash
python toolsx.py --session
```

### Mode cepat (satu baris)
```bash
python toolsx.py --session -t "Event Sabtu 19.00!" -m media/images/poster.jpg
```

### Contoh output
```
========================================================
  Target : 3 akun -> @akun1, @akun2, @akun3
  Mode   : SESSION (browser cookies)
  Media  : 1 file -> poster.jpg
========================================================

[1/3] @akun1
   [BERHASIL]  tweet id: (via session)
[2/3] @akun2
   [BERHASIL]  tweet id: (via session)
[3/3] @akun3
   [BERHASIL]  tweet id: (via session)

--------------------------------------------------------
  Ringkasan: 3 berhasil, 0 gagal (total 3)
--------------------------------------------------------
```

---

## 5. Taruh gambar/video

Sebelum posting dengan media, copy file ke folder yang sesuai:

```
numberzero/
├── media/
│   ├── images/   ← .jpg / .png / .webp
│   └── videos/   ← .mp4 / .mov / .gif
```

Saat mode interaktif, tool otomatis tampilkan isi folder sebagai menu pilihan.

---

## 6. Mode cepat (flag)

```bash
# Teks saja
python toolsx.py --session -t "Meetup Sabtu 19.00!"

# Teks + gambar
python toolsx.py --session -t "Poster event" -m media/images/poster.jpg

# Teks + video
python toolsx.py --session -t "Aftermovie" -m media/videos/event.mp4

# Teks + banyak gambar
python toolsx.py --session -t "Foto event" -m media/images/1.jpg -m media/images/2.jpg
```

### Semua opsi `toolsx.py`

```
--session        Posting via session (wajib kalau pakai session)
-t, --text       Teks tweet
-m, --media      Path media (ulangi untuk multi-gambar)
-d, --delay      Jeda antar akun dalam detik (default: 3)
--dry-run        Cek tanpa posting
-h, --help       Lihat help
```

### Opsi `sessions.py`

```
(tanpa flag)     Login otomatis dari email list di accounts.yaml
--manual         Login manual satu per satu lewat browser
```

---

## 7. Troubleshooting

| Error | Solusi |
|---|---|
| `ModuleNotFoundError: playwright` | `pip install -r requirements.txt` |
| `Executable doesn't exist... chromium` | `python -m playwright install chromium` |
| `File accounts.yaml tidak ditemukan` | `copy accounts.example.yaml accounts.yaml` lalu isi |
| `Belum ada session tersimpan` | Jalankan `python sessions.py` dulu |
| `Session expired` | Jalankan `python sessions.py` ulang |
| Browser terbuka tapi tidak bisa login | Selesaikan captcha/verifikasi manual, tool akan lanjut otomatis |
| `python: command not found` | Install Python dari [python.org](https://www.python.org/downloads/) |

---

## 8. Struktur project

```
numberzero/
├── sessions.py             ← PERINTAH 1: login & simpan session
├── toolsx.py               ← PERINTAH 2: posting
├── accounts.yaml           ← daftar email + password (RAHASIA, di-gitignore)
├── accounts.example.yaml   ← template accounts.yaml
├── sessions/               ← cookies tersimpan di sini (di-gitignore)
├── media/
│   ├── images/             ← taruh gambar
│   └── videos/             ← taruh video
├── requirements.txt
├── setup.sh
├── nz / nz.bat
├── src/
│   ├── auth.py             ← login browser + simpan cookies
│   ├── cli.py              ← logika CLI toolsx.py
│   ├── colors.py           ← warna log
│   ├── config.py           ← baca accounts.yaml
│   ├── interactive.py      ← menu step-by-step
│   └── poster.py           ← posting ke X
└── README.md
```

### Hubungan 2 file utama:

```
accounts.yaml (email + password)
       ↓
sessions.py  →  sessions/*.json (cookies)
                       ↓
toolsx.py   →  baca cookies → posting ke X
```

---

## Catatan penting

- Tool ini untuk share event ke akun-akun yang kamu kelola sendiri
- Jangan share file `sessions/` atau `accounts.yaml` ke orang lain
- Posting konten identik secara massal bisa menyebabkan akun di-suspend oleh X
- Session bertahan 1-3 bulan; kalau expired, jalankan `sessions.py` ulang
