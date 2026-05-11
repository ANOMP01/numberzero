# numberzero

CLI kecil untuk memposting tweet yang sama (teks + gambar/video) dari beberapa
akun X sekaligus. Cocok untuk share event ke beberapa akun (misal akun
pribadi + akun komunitas + akun event).

---

## Daftar Isi

1. [Persiapan awal](#1-persiapan-awal)
2. [Install project](#2-install-project)
3. [Dapatkan kredensial API X](#3-dapatkan-kredensial-api-x)
4. [Isi file `accounts.yaml`](#4-isi-file-accountsyaml)
5. [Taruh gambar/video ke folder media](#5-taruh-gambarvideo-ke-folder-media)
6. [Jalankan tool](#6-jalankan-tool)
7. [Mode cepat (flag)](#7-mode-cepat-flag)
8. [Menambah / menghapus akun](#8-menambah--menghapus-akun)
9. [Mengatur jumlah akun default](#9-mengatur-jumlah-akun-default)
10. [Aturan media X](#10-aturan-media-x)
11. [Troubleshooting](#11-troubleshooting)
12. [Struktur project](#12-struktur-project)
13. [Catatan penting](#13-catatan-penting)

---

## 1. Persiapan awal

### Yang perlu kamu punya

- **Python 3.8+** — cek dengan `python3 --version` (Mac/Linux) atau
  `python --version` (Windows). Kalau belum ada, download di
  <https://www.python.org/downloads/>. Saat install di Windows, **centang
  "Add Python to PATH"**.
- **Git** (opsional) — untuk clone repo. Kalau tidak ada, bisa download ZIP
  dari GitHub.
- **Akun X** yang kredensial API-nya sudah disiapkan (lihat
  [langkah 3](#3-dapatkan-kredensial-api-x)).

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

## 3. Dapatkan kredensial API X

Setiap akun X butuh kredensial API sendiri dari
<https://developer.x.com/>. Ulangi langkah ini untuk **setiap** akun yang mau
kamu pakai.

1. **Login ke x.com pakai akun yang mau ditambah**, lalu buka
   <https://developer.x.com/>.
2. Buat **Project** + **App** (tier gratis cukup).
3. Di App → **User authentication settings** → pilih **Read and Write** →
   save.
4. Buka tab **Keys and Tokens**, catat **4 nilai** berikut:
   - `API Key` (consumer key)
   - `API Key Secret` (consumer secret)
   - `Access Token`
   - `Access Token Secret`

> **Catatan:** tier gratis X API membatasi ~500 post per bulan per app. Untuk
> share event ini lebih dari cukup.

---

## 4. Isi file `accounts.yaml`

### 4.1 Buat file dari template

```bash
cp accounts.example.yaml accounts.yaml        # macOS / Linux
# copy accounts.example.yaml accounts.yaml    # Windows
```

`accounts.yaml` sudah di-`.gitignore`, jadi kredensial tidak akan ikut
ter-commit ke GitHub.

### 4.2 Edit isinya

Buka `accounts.yaml` di editor apapun (Notepad, TextEdit, VS Code). Isinya
seperti ini:

```yaml
# Jumlah akun yang dipakai secara default (bisa diubah kapan saja).
default_count: 2

# Folder tempat menaruh media. Ubah kalau mau lokasi lain.
images_dir: media/images
videos_dir: media/videos

accounts:
  - name: main
    api_key: "GANTI_DENGAN_API_KEY_KAMU"
    api_secret: "GANTI_DENGAN_API_SECRET_KAMU"
    access_token: "GANTI_DENGAN_ACCESS_TOKEN_KAMU"
    access_token_secret: "GANTI_DENGAN_ACCESS_TOKEN_SECRET_KAMU"

  - name: backup
    api_key: "..."
    api_secret: "..."
    access_token: "..."
    access_token_secret: "..."
```

**Ganti nilai `YOUR_...` dengan 4 kredensial dari langkah 3.** `name` bebas,
dipakai sebagai label di CLI (contoh: `--accounts main,backup`).

### 4.3 Aturan format YAML

- Indentasi pakai **spasi**, bukan tab (2 spasi konsisten).
- Tanda `-` harus diikuti **spasi**: `- name: main` ✅ ; `-name: main` ❌
- Nilai sebaiknya dibungkus tanda kutip: `api_key: "abc123"`.
- `name` tiap akun harus **unik**.

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

## 8. Menambah / menghapus akun

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

## 9. Mengatur jumlah akun default

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

## 10. Aturan media X

| Tipe | Format | Batas per tweet |
|---|---|---|
| Gambar | `.jpg`, `.jpeg`, `.png`, `.webp` | maks **4** |
| GIF | `.gif` | maks **1** |
| Video | `.mp4`, `.mov` | maks **1** (maks 2 menit 20 detik, 512 MB) |

Tidak boleh mencampur video/GIF dengan gambar lain dalam satu tweet.

---

## 11. Troubleshooting

| Error | Penyebab & solusi |
|---|---|
| `./nz: Permission denied` | Jalankan `chmod +x nz` sekali saja |
| `python: command not found` | Install Python dari [python.org](https://www.python.org/downloads/) |
| `ModuleNotFoundError: No module named 'tweepy'` | Jalankan `pip install -r requirements.txt` |
| `Accounts file not found: accounts.yaml` | File config belum dibuat → `cp accounts.example.yaml accounts.yaml` |
| `Config error: Account X is missing required fields` | Ada field kredensial kelupaan/salah ketik di `accounts.yaml` |
| `401 Unauthorized` saat post | Kredensial salah, atau App belum di-set "Read and Write" di developer portal |
| `403 Forbidden` saat post | Akun tidak punya permission posting (cek ulang setting app) |
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

## 12. Struktur project

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
│   ├── config.py           # load & validasi accounts.yaml
│   ├── interactive.py      # menu step-by-step
│   └── poster.py           # upload media + create tweet ke X
└── README.md
```

### Apa isi tiap file

- **`toolsx.py`** — entry point, yang dipanggil saat `python toolsx.py`.
- **`src/cli.py`** — parse argumen command-line, atur alur mode interaktif vs
  mode flag, format log hasil posting.
- **`src/config.py`** — baca `accounts.yaml`, validasi format, cegah duplikat
  nama akun.
- **`src/interactive.py`** — semua menu step-by-step (tulis teks, pilih
  media, pilih akun, konfirmasi).
- **`src/poster.py`** — upload media (images via v1.1 upload API, video
  chunked) + create tweet (v2 API).

---

## 13. Catatan penting

Alat ini dimaksudkan untuk penggunaan sah — misal share informasi event ke
akun-akun yang kamu kelola sendiri (akun pribadi + akun komunitas + akun
event). Memposting konten identik secara massal dari banyak akun untuk
manipulasi platform melanggar [X Rules][rules] dan dapat menyebabkan akun
di-suspend.

[rules]: https://help.x.com/en/rules-and-policies/x-rules
