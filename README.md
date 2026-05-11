# numberzero

Tool untuk memposting tweet yang sama dari banyak akun X sekaligus.
Cocok untuk share event.

---

## Cara Pakai (Ringkas)

```
python sessions.py                                    # login & simpan session
python toolsx.py --session -t "Event!" -m poster.jpg  # posting
```

---

## 1. Install

### Download ZIP (tanpa Git)

1. Buka https://github.com/ANOMP01/numberzero
2. Klik Code (hijau) → Download ZIP
3. Extract → masuk ke folder hasil extract

### Atau via Git

```
git clone https://github.com/ANOMP01/numberzero.git
cd numberzero
```

### Install dependensi

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
```

---

## 2. Isi daftar email

Buat file accounts.yaml dari template:

```
copy accounts.example.yaml accounts.yaml
```

Buka accounts.yaml, isi email dan password:

```yaml
default_password: "PasswordKamu123"

emails: "akun1@gmail.com, akun2@gmail.com, akun3@gmail.com"
```

---

## 3. Login & simpan session

```
python sessions.py
```

Tool akan:
1. Baca email dari accounts.yaml
2. Buka browser satu per satu
3. Otomatis isi email + password
4. Kalau ada captcha/verifikasi → selesaikan manual di browser
5. Setelah masuk Home → session tersimpan otomatis
6. Lanjut ke akun berikutnya

Contoh output:

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
  [akun1] Login otomatis...
  ✓ @akun1 berhasil!

[2/3] akun2@gmail.com
  ✓ @akun2 berhasil!

[3/3] akun3@gmail.com
  ✓ @akun3 berhasil!

  Selesai: 3 berhasil, 0 gagal
  Untuk posting: python toolsx.py --session
```

### Mode manual (tanpa file email)

```
python sessions.py --manual
```

### Berapa lama session bertahan?

Aktif dipakai: 1-3 bulan
Tidak dipakai: sekitar 30 hari
Expired: jalankan python sessions.py lagi

---

## 4. Posting

```
python toolsx.py --session
```

Atau mode cepat:

```
python toolsx.py --session -t "Event Sabtu 19.00!" -m media/images/poster.jpg
```

Contoh output:

```
========================================================
  Target : 3 akun → @akun1, @akun2, @akun3
  Mode   : SESSION (browser cookies)
  Media  : 1 file → poster.jpg
========================================================

[1/3] @akun1
   [BERHASIL]  tweet id: (via session)
[2/3] @akun2
   [BERHASIL]  tweet id: (via session)
[3/3] @akun3
   [BERHASIL]  tweet id: (via session)

  Ringkasan: 3 berhasil, 0 gagal
```

---

## 5. Taruh gambar/video

Copy file ke folder yang sesuai:

```
media/images/   ← .jpg .png .webp
media/videos/   ← .mp4 .mov .gif
```

---

## 6. Mode cepat (flag)

```
python toolsx.py --session -t "Meetup Sabtu 19.00!"
python toolsx.py --session -t "Poster" -m media/images/poster.jpg
python toolsx.py --session -t "Video" -m media/videos/event.mp4
python toolsx.py --session -t "Foto" -m media/images/1.jpg -m media/images/2.jpg
```

---

## 7. Troubleshooting

| Error | Solusi |
|---|---|
| ModuleNotFoundError: playwright | pip install -r requirements.txt |
| Executable doesn't exist chromium | python -m playwright install chromium |
| File accounts.yaml tidak ditemukan | copy accounts.example.yaml accounts.yaml |
| Belum ada session tersimpan | Jalankan python sessions.py dulu |
| Session expired | Jalankan python sessions.py ulang |
| Browser terbuka tapi tidak bisa login | Selesaikan captcha manual, tool lanjut otomatis |

---

## 8. Struktur project

```
numberzero/
├── sessions.py             ← LOGIN & simpan session
├── toolsx.py               ← POSTING
├── accounts.yaml           ← daftar email + password (RAHASIA)
├── accounts.example.yaml   ← template
├── sessions/               ← cookies tersimpan di sini
├── media/
│   ├── images/
│   └── videos/
├── requirements.txt
├── src/
│   ├── auth.py
│   ├── cli.py
│   ├── colors.py
│   ├── config.py
│   ├── interactive.py
│   └── poster.py
└── README.md
```

Hubungan:

```
accounts.yaml (email + password)
       ↓
sessions.py  →  sessions/*.json (cookies)
                       ↓
toolsx.py    →  baca cookies → posting ke X
```
