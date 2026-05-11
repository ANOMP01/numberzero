# numberzero

CLI kecil untuk memposting tweet yang sama (teks + gambar/video) dari beberapa
akun X sekaligus. Cocok untuk share event ke beberapa akun (misal akun
pribadi + akun komunitas + akun event).

---

## Daftar Isi

1. [Persiapan awal](#1-persiapan-awal)
2. [Install project](#2-install-project)
3. [Login & simpan session (CARA MUDAH)](#3-login--simpan-session-cara-mudah)
4. [Posting via session](#4-posting-via-session)
5. [Taruh gambar/video ke folder media](#5-taruh-gambarvideo-ke-folder-media)
6. [Jalankan tool](#6-jalankan-tool)
7. [Mode cepat (flag)](#7-mode-cepat-flag)
8. [Cara alternatif: API resmi (opsional)](#8-cara-alternatif-api-resmi-opsional)
9. [Menambah / menghapus akun](#9-menambah--menghapus-akun)
10. [Mengatur jumlah akun default](#10-mengatur-jumlah-akun-default)
11. [Aturan media X](#11-aturan-media-x)
12. [Troubleshooting](#12-troubleshooting)
13. [Struktur project](#13-struktur-project)
14. [Catatan penting](#14-catatan-penting)

---

## 1. Persiapan awal

### Yang perlu kamu punya

- **Python 3.8+** — cek dengan `python3 --version` (Mac/Linux) atau
  `python --version` (Windows). Kalau belum ada, download di
  <https://www.python.org/downloads/>. Saat install di Windows, **centang
  "Add Python to PATH"**.
- **Git** (opsional) — untuk clone repo. Kalau tidak ada, bisa download ZIP
  dari GitHub.
- **Akun X** yang mau dipakai (lihat
  [langkah 3](#3-login--simpan-session-cara-mudah) untuk cara login).

---

## 2. Install project

Buka **Terminal** (Mac/Linux) atau **PowerShell/Command Prompt** (Windows),
lalu:

```bash
# 1. Clone repo
git clone https://github.com/ANOMP01/numberzero.git
cd numberzero

# 2. (Opsional tapi disarankan) buat virtual environment
python -m venv .venv
source .venv/bin/activate    # macOS / Linux
# .venv\Scripts\activate     # Windows

# 3. Install dependensi Python
pip install -r requirements.txt
```

**Cara singkat untuk Mac/Linux**: langkah 2 & 3 di atas bisa digantikan dengan
```bash
bash setup.sh
```
yang akan menginstall dependensi dan menyiapkan file config sekaligus.

---

## 3. Login & simpan session (CARA MUDAH)

Cara ini **tidak perlu daftar developer**, tidak perlu API key. Cukup
email + password akun X yang mau dipakai.

### 3.1 Install browser otomatis (sekali saja)

Setelah install dependensi di langkah 2, jalankan:

```bash
python -m playwright install chromium
```

Ini download Chromium (~110 MB) yang dipakai untuk login. Cuma perlu sekali.

**Windows:** kalau muncul error, coba jalankan PowerShell sebagai Administrator.

### 3.2 Login akun satu per satu

```bash
python toolsx.py --login
```

Tool akan:
1. Tanya nama akun (label bebas, misal: `main`, `event`, `backup`)
2. Buka browser otomatis → halaman login X
3. Kamu **login manual** di browser (ketik email + password + 2FA kalau ada)
4. Setelah masuk Home, browser otomatis tutup
5. Session tersimpan di `sessions/main.json`
6. Tanya "Login akun lain?" → ketik `y` untuk lanjut ke akun berikutnya

**Contoh alur:**
```
  Login & Simpan Session
========================================================

Kamu akan login ke akun X satu per satu lewat browser.
Setelah login berhasil, session disimpan otomatis.

Nama akun (ketik nama bebas, misal: main): main
  Membuka browser untuk login akun: @main
  Login secara manual (email + password).
  Menunggu kamu login...
  Session disimpan: sessions/main.json
  Login @main berhasil & session tersimpan!

Login akun lain? [y/N]: y
Nama akun: event
  Membuka browser...
  ...
  Login @event berhasil & session tersimpan!

Login akun lain? [y/N]: n

Total session tersimpan: 2
  - @main (aktif)
  - @event (aktif)
```

### 3.3 Berapa lama session bertahan?

- Aktif dipakai (posting seminggu sekali): **1-3 bulan**
- Tidak dipakai sama sekali: **~30 hari**
- Kalau expired: jalankan `python toolsx.py --login` lagi

### 3.4 Keamanan session

Session disimpan di folder `sessions/` (otomatis di-`.gitignore`). File ini
berisi cookies yang setara dengan "sudah login" — **jangan share ke orang
lain**. Kalau file ini bocor, orang lain bisa posting dari akun kamu.

---

## 4. Posting via session

Setelah punya session tersimpan (langkah 3), posting seperti ini:

### Mode interaktif
```bash
python toolsx.py --session
```

Tool akan tanya teks, media, pilih akun dari session yang tersimpan → posting.

### Mode cepat (satu baris)
```bash
python toolsx.py --session -t "Event Sabtu 19.00!" -m media/images/poster.jpg
```

### Contoh output
```
========================================================
  Target : 2 akun -> @main, @event
  Mode   : SESSION (browser cookies)
  Media  : 1 file -> poster.jpg
========================================================

[1/2] @main
   [BERHASIL]  tweet id: (via session)
[2/2] @event
   [BERHASIL]  tweet id: (via session)

--------------------------------------------------------
  Ringkasan: 2 berhasil, 0 gagal (total 2)
--------------------------------------------------------
```

## 8. Cara alternatif: API resmi (opsional)

Kalau kamu lebih suka cara resmi (lebih stabil, tidak tergantung session),
bisa daftar developer di X. Ini **opsional** — kalau sudah pakai session
(langkah 3-4), bagian ini bisa dilewati.

### 8.1 Daftar sebagai developer (sekali saja per akun)

1. Buka <https://developer.x.com/> → klik **Sign up** atau **Developer Portal**.
2. Login dengan akun X yang mau didaftarkan.
3. Pilih tier gratis: **Free** (sudah cukup untuk share event — 500 post/bulan).
4. Isi form singkat:
   - **Use case**: pilih yang paling relevan (misal "Making a bot" atau
     "Publishing content"). Tidak usah ribet — X cukup longgar untuk tier Free.
   - **Describe your use case**: tulis singkat, contoh:
     > "Automating event announcements across my own managed X accounts for
     > community events."
   - Centang semua persetujuan ToS → **Submit**.
5. Tunggu email verifikasi (biasanya langsung dapat akses).

### 8.2 Buat Project + App

Setelah masuk ke **Developer Portal** (<https://developer.x.com/en/portal/dashboard>):

1. Klik **Projects & Apps** di sidebar kiri → **Add project**.
2. Isi:
   - **Project name**: bebas, misal `numberzero-main`
   - **Use case**: pilih yang sama dengan langkah sebelumnya
   - **Project description**: singkat, misal `Event poster for my accounts`
3. **Create new App in this project** (atau pilih App yang sudah ada):
   - **App name**: harus unik global di X, misal `numberzero-main-2026`
4. Setelah App dibuat, X akan menampilkan kredensial pertama — **tunggu dulu,
   jangan dicatat di sini** karena kita butuh regenerate lagi setelah setting
   permission. Klik **Skip / Dashboard**.

### 8.3 Set permission "Read and Write" (WAJIB)

Default-nya App cuma bisa baca. Kita perlu ubah supaya bisa posting.

1. Di dashboard App, cari section **User authentication settings** → klik
   **Set up** (atau **Edit** kalau sudah pernah).
2. Isi form:
   - **App permissions**: pilih **Read and write**
     (kalau mau bisa DM juga, pilih **Read and write and Direct message** —
     untuk event sharing cukup Read and write).
   - **Type of App**: pilih **Web App, Automated App or Bot**
   - **App info** → isi yang required:
     - **Callback URI / Redirect URL**: isi apa saja yang valid, misal
       `https://localhost/` atau `https://example.com/callback`
       (kita tidak pakai OAuth redirect, ini cuma formality)
     - **Website URL**: bisa isi `https://x.com` atau URL project kamu
3. Klik **Save**.

### 8.4 Ambil 4 kredensial

Sekarang buka tab **Keys and Tokens** di dashboard App. Ada 4 nilai yang
perlu dicatat:

| No | Label di X | Nama di `accounts.yaml` | Cara dapat |
|---|---|---|---|
| 1 | **API Key** | `api_key` | Tab Keys and Tokens → section *Consumer Keys* → **View Keys** atau **Regenerate** |
| 2 | **API Key Secret** | `api_secret` | (sama, muncul bareng API Key) |
| 3 | **Access Token** | `access_token` | Section *Authentication Tokens* → **Access Token and Secret** → **Generate** |
| 4 | **Access Token Secret** | `access_token_secret` | (sama, muncul bareng Access Token) |

**Cara detailnya:**

1. **API Key & Secret** (Consumer Keys):
   - Di section **Consumer Keys**, klik **Regenerate** (atau **View Keys** kalau
     baru pertama kali).
   - X akan menampilkan 2 nilai **hanya sekali** — segera salin ke tempat aman:
     ```
     API Key:         abc123xyz...
     API Key Secret:  def456uvw...
     ```
   - Kalau ke-close atau lupa, tinggal klik **Regenerate** lagi (tapi ini akan
     invalidate yang lama).

2. **Access Token & Secret** (Authentication Tokens):
   - Di section **Authentication Tokens** → **Access Token and Secret** →
     klik **Generate**.
   - **PENTING:** pastikan tulisannya `Created with Read and Write permissions`.
     Kalau masih `Read only`, kamu lupa simpan permission di langkah 8.3 →
     balik, save lagi, baru **Regenerate** Access Token.
   - Lagi-lagi, ini muncul **hanya sekali** — segera salin:
     ```
     Access Token:         1234567890-ghi789...
     Access Token Secret:  jkl012mno...
     ```

### 8.5 Checklist sebelum lanjut

Sebelum lanjut ke langkah 4, pastikan kamu sudah punya 4 nilai ini:

- [ ] API Key (dimulai huruf acak, ~25 karakter)
- [ ] API Key Secret (~50 karakter)
- [ ] Access Token (biasanya format: `ANGKA-hurufhuruf`, ~50 karakter)
- [ ] Access Token Secret (~45 karakter)
- [ ] Di section Access Token ada tulisan **"Read and Write"**

Kalau ada yang kurang, balik ke langkah terkait. Kalau kredensial hilang
(belum sempat disalin), tinggal klik **Regenerate** — aman saja.

### 8.6 Ulangi untuk akun lain

Untuk akun X ke-2, ke-3, dst:

1. **Log out** dari x.com.
2. **Login dengan akun berikutnya**.
3. Ulangi langkah 8.1–3.4.

Hasilnya: tiap akun X akan punya 4 kredensial sendiri yang beda-beda.

> **Catatan:** tier gratis X API membatasi ~500 post per bulan per app. Untuk
> share event ini lebih dari cukup.

> **Keamanan:** 4 kredensial ini ibarat username + password. Jangan share di
> publik, jangan commit ke git. File `accounts.yaml` sudah masuk
> `.gitignore` jadi aman dari commit tidak sengaja.

---

## 5. Taruh gambar/video ke folder media

Tool sudah menyiapkan 2 folder khusus:

```
numberzero/
├── media/
│   ├── images/   ← taruh .jpg / .jpeg / .png / .webp di sini
│   └── videos/   ← taruh .mp4 / .mov / .gif di sini
```

Copy file event (poster, foto, video teaser, aftermovie, dll) ke folder yang
sesuai. Saat mode interaktif, tool akan membaca isi folder ini dan
menampilkannya sebagai menu pilihan bernomor — kamu tinggal pilih angkanya,
tidak perlu ketik path.

Kalau mau pakai lokasi lain (misal folder Downloads), ubah `accounts.yaml`:
```yaml
images_dir: /Users/kamu/Pictures/event
videos_dir: /Users/kamu/Movies/event
```

---

## 6. Jalankan tool

### Perintah utama (semua OS)

```bash
python toolsx.py
```

### Shortcut (lebih pendek)

```bash
./nz              # macOS / Linux  (chmod +x nz sekali kalau belum executable)
nz                # Windows
```

Ketiganya identik — `nz`/`nz.bat` hanya wrapper yang memanggil
`python toolsx.py` di belakang layar.

### Alur mode interaktif

Jalankan tanpa argumen → tool akan pandu kamu 4 langkah:

```
========================================================
  numberzero  |  multi-account X event poster
========================================================

[Langkah 1/4] Tulis isi tweet
--------------------------------------------------------
Tweet : Meetup Komunitas X, Sabtu jam 19.00!

[Langkah 2/4] Lampirkan media?
--------------------------------------------------------
  * 1) Tidak, teks saja
    2) Gambar (dari folder gambar)
    3) Video / GIF (dari folder video)
Pilihan [1]: 2

File tersedia di media/images/:
   1) poster.jpg   (1.2 MB)
   2) banner.png   (450 KB)

Ketik nomor gambar (boleh lebih dari satu, dipisah koma; maks 4): 1

[Langkah 3/4] Pilih akun yang akan memposting
--------------------------------------------------------
Akun yang terdaftar di accounts.yaml:
    1) @main
    2) @backup

  * 1) Pakai default (2 akun pertama)
    2) Pilih jumlah akun (ambil dari urutan teratas)
    3) Pilih akun spesifik (ketik nomor/nama)
    4) Semua akun
Pilihan [1]:

[Langkah 4/4] Konfirmasi sebelum posting
--------------------------------------------------------
Ringkasan:
  Teks   : Meetup Komunitas X, Sabtu jam 19.00!
  Media  : 1 file
           - media/images/poster.jpg
  Target : 2 akun -> @main, @backup

Lanjutkan posting sekarang? [Y/n]: y
```

Lalu tool akan proses tiap akun satu per satu:

```
[1/2] @main
   [BERHASIL]  tweet id: 1789...
[2/2] @backup
   [BERHASIL]  tweet id: 1790...

--------------------------------------------------------
  Ringkasan: 2 berhasil, 0 gagal (total 2)
  Berhasil : @main, @backup
--------------------------------------------------------
```

### Tes dulu tanpa posting beneran

Tambah flag `--dry-run` untuk lihat alurnya tanpa ngirim ke X:

```bash
python toolsx.py --dry-run
```

---

## 7. Mode cepat (flag)

Kalau sudah hafal dan mau skip menu, pakai flag langsung:

### Post teks saja ke semua akun default
```bash
python toolsx.py -t "Meetup Sabtu 19.00, RSVP di bio!"
```

### Post teks + 1 gambar
```bash
python toolsx.py -t "Poster event" -m media/images/poster.jpg
```

### Post teks + beberapa gambar (maks 4)
```bash
python toolsx.py -t "Throwback event" \
  -m media/images/img1.jpg \
  -m media/images/img2.jpg \
  -m media/images/img3.jpg
```

### Post video
```bash
python toolsx.py -t "Aftermovie event" -m media/videos/aftermovie.mp4
```

### Pilih akun spesifik
```bash
python toolsx.py -t "Halo" --accounts main,backup
```

### Override jumlah akun sekali jalan
```bash
python toolsx.py -t "Halo" --count 3
python toolsx.py -t "Halo" -n 1
```

### Dry run (cek tanpa post)
```bash
python toolsx.py -t "Halo" -m media/images/poster.jpg --dry-run
```

### Semua opsi lengkap

```
-t, --text       Teks tweet (boleh kosong kalau ada media)
-m, --media      Path ke file gambar/video (ulangi untuk multi-gambar)
-c, --config     Path ke accounts.yaml (default: accounts.yaml)
-a, --accounts   Filter akun, koma-separated (override --count)
-n, --count      Jumlah akun yang dipakai (default: default_count di config)
-d, --delay      Detik jeda antar akun (default: 2.0)
    --dry-run    Validasi & list target, tanpa posting
-i, --interactive  Paksa mode interaktif walau pakai flag
-h, --help       Lihat help lengkap
```

---

## 9. Menambah / menghapus akun

### Menambah akun

1. Daftar kredensial API untuk akun baru ([langkah 3](#3-dapatkan-kredensial-api-x)).
2. Buka `accounts.yaml`, tambahkan blok baru di bawah akun terakhir:

```yaml
accounts:
  - name: main
    api_key: "..."
    api_secret: "..."
    access_token: "..."
    access_token_secret: "..."

  - name: backup
    api_key: "..."
    api_secret: "..."
    access_token: "..."
    access_token_secret: "..."

  - name: event              # <- akun baru
    api_key: "..."
    api_secret: "..."
    access_token: "..."
    access_token_secret: "..."
```

3. Simpan file. Langsung bisa dipakai — tidak perlu restart apapun.

### Verifikasi akun baru terdaftar

```bash
python toolsx.py -t "tes" -n 3 --dry-run
# Output: Target : 3 akun -> @main, @backup, @event
```

### Menghapus akun

Cukup hapus blok `- name: xxx` beserta 4 kredensialnya dari `accounts.yaml`,
atau tambahkan `#` di awal tiap baris untuk komentari.

---

## 10. Mengatur jumlah akun default

Edit `default_count` di `accounts.yaml`:

```yaml
default_count: 2   # ubah sesuai kebutuhan (misal 3, 5)
```

Ini dipakai kalau kamu jalankan tanpa `--accounts` atau `--count`. Untuk
override sekali jalan, pakai `-n`:

```bash
python toolsx.py -t "Halo" -n 3   # pakai 3 akun pertama sekali ini saja
```

**Urutan prioritas pemilihan akun:**
1. `--accounts main,event` (nama spesifik) → paling prioritas
2. `-n 3` / `--count 3` (jumlah) → kedua
3. `default_count` di `accounts.yaml` → default
4. Fallback ke `2` kalau `default_count` tidak ada

---

## 11. Aturan media X

| Tipe | Format | Batas per tweet |
|---|---|---|
| Gambar | `.jpg`, `.jpeg`, `.png`, `.webp` | maks **4** |
| GIF | `.gif` | maks **1** |
| Video | `.mp4`, `.mov` | maks **1** (maks 2 menit 20 detik, 512 MB) |

Tidak boleh mencampur video/GIF dengan gambar lain dalam satu tweet.

---

## 12. Troubleshooting

| Error | Penyebab & solusi |
|---|---|
| `./nz: Permission denied` | Jalankan `chmod +x nz` sekali saja |
| `python: command not found` | Install Python dari [python.org](https://www.python.org/downloads/) |
| `ModuleNotFoundError: No module named 'tweepy'` | Jalankan `pip install -r requirements.txt` |
| `Accounts file not found: accounts.yaml` | File config belum dibuat → `cp accounts.example.yaml accounts.yaml` |
| `Config error: Account X is missing required fields` | Ada field kredensial kelupaan/salah ketik di `accounts.yaml` |
| `401 Unauthorized` saat post | Kredensial salah, atau App belum di-set "Read and Write" di developer portal (lihat langkah 8.3) |
| `403 Forbidden` saat post | Akun tidak punya permission posting. Cek di developer portal: permission App harus **Read and Write**, dan Access Token harus di-**Regenerate** setelah permission diubah (langkah 8.4) |
| Access Token tulisannya `Read only` padahal sudah set Read and Write | Setelah ubah permission App, **wajib regenerate Access Token**. Permission lama akan terbawa di Access Token lama |
| Nama App ditolak saat dibuat | Nama App harus unik di seluruh X. Tambah angka/tahun, misal `numberzero-main-2026` |
| `Media file not found` | Path media salah. Kalau pakai flag, cek ulang lokasi file |
| `Unsupported media type` | Format file tidak didukung. Convert ke mp4/jpg/png dulu |
| Upload video lama sekali | Wajar — video di-upload chunked. Video 100 MB biasanya butuh 1–3 menit |

### Cek config tanpa posting

```bash
python toolsx.py -t "tes" --dry-run
```

Kalau OK, akan muncul daftar akun tujuan. Kalau ada masalah config, pesan
error akan muncul di sini.

---

## 13. Struktur project

```
numberzero/
├── toolsx.py               # entry point utama (python toolsx.py)
├── nz                      # shortcut CLI (macOS/Linux)
├── nz.bat                  # shortcut CLI (Windows)
├── setup.sh                # installer sekali jalan (macOS/Linux)
├── requirements.txt        # daftar dependensi Python
├── accounts.example.yaml   # template kredensial + setting folder media
├── accounts.yaml           # file kredensial kamu (tidak di-commit)
├── media/
│   ├── images/             # taruh gambar di sini
│   └── videos/             # taruh video/GIF di sini
├── src/
│   ├── __init__.py
│   ├── cli.py              # logika CLI + formatter log
│   ├── colors.py           # helper warna ANSI untuk log
│   ├── config.py           # load & validasi accounts.yaml
│   ├── interactive.py      # menu step-by-step
│   └── poster.py           # upload media + create tweet ke X
└── README.md
```

### Apa isi tiap file

- **`toolsx.py`** — entry point, yang dipanggil saat `python toolsx.py`.
- **`src/cli.py`** — parse argumen command-line, atur alur mode interaktif vs
  mode flag, format log hasil posting.
- **`src/colors.py`** — helper pewarnaan ANSI. Auto-detect TTY; bisa di-force
  dengan `FORCE_COLOR=1` atau dimatikan dengan `NO_COLOR=1`.
- **`src/config.py`** — baca `accounts.yaml`, validasi format, cegah duplikat
  nama akun.
- **`src/interactive.py`** — semua menu step-by-step (tulis teks, pilih
  media, pilih akun, konfirmasi).
- **`src/poster.py`** — upload media (images via v1.1 upload API, video
  chunked) + create tweet (v2 API).

---

## 14. Catatan penting

Alat ini dimaksudkan untuk penggunaan sah — misal share informasi event ke
akun-akun yang kamu kelola sendiri (akun pribadi + akun komunitas + akun
event). Memposting konten identik secara massal dari banyak akun untuk
manipulasi platform melanggar [X Rules][rules] dan dapat menyebabkan akun
di-suspend.

[rules]: https://help.x.com/en/rules-and-policies/x-rules
