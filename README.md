# numberzero

CLI kecil untuk memposting tweet yang sama (teks + gambar/video) dari beberapa
akun X sekaligus. Cocok untuk share event ke beberapa akun (misal akun
pribadi + akun komunitas + akun event).

## Cara pakai tercepat (TL;DR)

Sekali setup, lalu tinggal satu perintah:

```bash
# --- Sekali saja (setup) ---
bash setup.sh            # macOS / Linux
# Windows: jalankan dulu "pip install -r requirements.txt"
#          lalu "copy accounts.example.yaml accounts.yaml"
# lalu edit accounts.yaml, isi kredensial akun X kamu.

# --- Sehari-hari ---
python toolsx.py         # jalan di semua OS (Mac/Linux/Windows)
# atau shortcut yang lebih pendek:
./nz                     # macOS / Linux
nz                       # Windows
```

Itu saja. Semua langkah (tulis teks → pilih gambar/video → pilih akun → konfirmasi)
dipandu lewat menu pilihan.

Kalau mau satu-baris (tanpa menu):
```bash
python toolsx.py -t "Event Sabtu 19.00!" -m ./media/images/poster.jpg
```

## Fitur

- Post teks dari banyak akun sekaligus
- Lampirkan hingga 4 gambar, atau 1 GIF, atau 1 video per tweet
- Pilih subset akun via `--accounts main,backup`
- Delay antar-post (default 2 detik) untuk menghindari rate limit
- Mode `--dry-run` untuk cek konfigurasi tanpa benar-benar memposting
- Log hasil per akun (sukses + tweet id, atau pesan error)

## Persyaratan

Setiap akun X yang dipakai butuh kredensial API sendiri dari
<https://developer.x.com/>:

1. Masuk ke Developer Portal → buat Project + App.
2. Di App → **User authentication settings**, pilih **Read and Write**.
3. Di tab **Keys and Tokens**, catat:
   - API Key & API Key Secret (consumer key/secret)
   - Access Token & Access Token Secret (untuk user context)
4. Ulangi untuk setiap akun X yang ingin dipakai (login ke developer portal
   dengan akun X yang bersangkutan).

> Catatan: tier gratis X API membatasi ~500 post per bulan per app. Untuk
> share event ini lebih dari cukup.

## Setup

```bash
# 1. Clone repo & masuk ke folder
git clone https://github.com/ANOMP01/numberzero.git
cd numberzero

# 2. (Opsional) buat virtualenv
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
# .venv\Scripts\activate     # Windows

# 3. Install dependensi
pip install -r requirements.txt

# 4. Siapkan file kredensial akun
cp accounts.example.yaml accounts.yaml
# lalu edit accounts.yaml dan isi key/token setiap akun
```

`accounts.yaml` sudah otomatis di-`.gitignore`, jadi kredensial tidak akan
ikut ke-commit.

## Penggunaan

### Siapkan folder media

Sebelum posting, taruh file di folder yang sesuai:

```
numberzero/
├── media/
│   ├── images/   ← taruh .jpg / .png / .webp di sini
│   └── videos/   ← taruh .mp4 / .mov / .gif di sini
```

Saat mode interaktif, tool akan otomatis membaca isi kedua folder itu dan
menampilkannya sebagai menu bernomor — tinggal pilih angka, tidak perlu
ketik path.

Kalau mau pakai folder lain, ubah di `accounts.yaml`:

```yaml
images_dir: /Users/kamu/Pictures/event
videos_dir: /Users/kamu/Movies/event
```

### Mode interaktif (paling mudah)

Jalankan tanpa argumen, tool akan pandu kamu langkah-demi-langkah dengan menu
pilihan (tulis teks, pilih media, pilih akun, konfirmasi):

```bash
python toolsx.py
```

Atau pakai shortcut:
```bash
./nz              # macOS / Linux
nz                # Windows
```

Contoh tampilan langkah pilih media:

```
[Langkah 2/4] Lampirkan media?
--------------------------------------------------------
  * 1) Tidak, teks saja
    2) Gambar (dari folder gambar)
    3) Video / GIF (dari folder video)
Pilihan [1]: 3

File tersedia di media/videos/:
   1) aftermovie.mp4         (48.2 MB)
   2) teaser-10detik.mp4     (3.1 MB)
   3) behindthescene.mov     (120.4 MB)

Ketik nomor video/GIF (hanya 1 file): 1
```

### Mode cepat (flag)

Kalau sudah hafal, tinggal pakai flag:

### Post teks saja ke semua akun

```bash
python toolsx.py --text "Jangan lupa datang ke Meetup Komunitas X, Sabtu jam 19.00!"
```

### Post teks + 1 gambar

```bash
python toolsx.py \
  --text "Poster event minggu ini." \
  --media ./media/images/poster.jpg
```

### Post teks + beberapa gambar (maks 4)

```bash
python toolsx.py \
  -t "Throwback event kemarin." \
  -m ./media/images/img1.jpg -m ./media/images/img2.jpg
```

### Post video

```bash
python toolsx.py -t "Aftermovie event" -m ./media/videos/aftermovie.mp4
```

### Pilih akun tertentu saja

```bash
python toolsx.py -t "Halo" --accounts main,backup
```

### Atur berapa akun yang dipakai

Defaultnya ambil dari `default_count` di `accounts.yaml` (template: `2`). Ubah
nilainya di file itu untuk mengubah default secara permanen. Untuk override
sekali jalan:

```bash
python toolsx.py -t "Halo" --count 3       # pakai 3 akun pertama
python toolsx.py -t "Halo" -n 1            # pakai 1 akun pertama
```

Catatan: kalau `--accounts` diberikan, `--count` akan diabaikan (nama akun
lebih spesifik).

### Dry run (cek dulu tanpa post)

```bash
python toolsx.py -t "Halo" --media ./media/images/poster.jpg --dry-run
```

### Opsi lengkap

```
-t, --text       Teks tweet (boleh kosong kalau ada media)
-m, --media      Path ke file gambar/video (ulangi untuk multi-gambar)
-c, --config     Path ke accounts.yaml (default: accounts.yaml)
-a, --accounts   Filter akun, koma-separated (override --count)
-n, --count      Jumlah akun yang dipakai (default: default_count di config, fallback 2)
-d, --delay      Detik jeda antar akun (default: 2.0)
    --dry-run    Validasi & list target, tanpa posting
```

## Aturan media X

- Gambar: `.jpg`, `.jpeg`, `.png`, `.webp` — maks 4 per tweet
- GIF: `.gif` — maks 1 per tweet
- Video: `.mp4`, `.mov` — maks 1 per tweet
- Tidak boleh mencampur video/gif dengan gambar lain

## Struktur

```
numberzero/
├── toolsx.py               # entry point utama (python toolsx.py)
├── nz                      # shortcut CLI (macOS/Linux)
├── nz.bat                  # shortcut CLI (Windows)
├── setup.sh                # installer sekali jalan (macOS/Linux)
├── accounts.example.yaml   # template kredensial + setting folder media
├── requirements.txt
├── media/
│   ├── images/             # taruh gambar di sini
│   └── videos/             # taruh video/GIF di sini
├── src/
│   ├── __init__.py
│   ├── cli.py              # logika CLI + formatter log
│   ├── config.py           # load & validasi accounts.yaml
│   ├── interactive.py      # menu step-by-step
│   └── poster.py           # upload media + create tweet
└── README.md
```

## Catatan penting

Alat ini dimaksudkan untuk penggunaan sah (misal: share informasi event ke
akun-akun yang kamu kelola sendiri). Memposting konten identik secara massal
dari banyak akun untuk manipulasi platform melanggar [X Rules][rules] dan
dapat menyebabkan akun di-suspend.

[rules]: https://help.x.com/en/rules-and-policies/x-rules
