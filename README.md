# numberzero

CLI kecil untuk memposting tweet yang sama (teks + gambar/video) dari beberapa
akun X sekaligus. Cocok untuk share event ke beberapa akun (misal akun
pribadi + akun komunitas + akun event).

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

### Post teks saja ke semua akun

```bash
python -m src.cli --text "Jangan lupa datang ke Meetup Komunitas X, Sabtu jam 19.00!"
```

### Post teks + 1 gambar

```bash
python -m src.cli \
  --text "Poster event minggu ini." \
  --media ./poster.jpg
```

### Post teks + beberapa gambar (maks 4)

```bash
python -m src.cli \
  -t "Throwback event kemarin." \
  -m ./img1.jpg -m ./img2.jpg -m ./img3.jpg
```

### Post video

```bash
python -m src.cli -t "Aftermovie event" -m ./aftermovie.mp4
```

### Pilih akun tertentu saja

```bash
python -m src.cli -t "Halo" --accounts main,backup
```

### Dry run (cek dulu tanpa post)

```bash
python -m src.cli -t "Halo" --media ./poster.jpg --dry-run
```

### Opsi lengkap

```
-t, --text       Teks tweet (boleh kosong kalau ada media)
-m, --media      Path ke file gambar/video (ulangi untuk multi-gambar)
-c, --config     Path ke accounts.yaml (default: accounts.yaml)
-a, --accounts   Filter akun, koma-separated (default: semua)
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
├── accounts.example.yaml   # template kredensial
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── cli.py              # entry point CLI
│   ├── config.py           # load & validasi accounts.yaml
│   └── poster.py           # upload media + create tweet
└── README.md
```

## Catatan penting

Alat ini dimaksudkan untuk penggunaan sah (misal: share informasi event ke
akun-akun yang kamu kelola sendiri). Memposting konten identik secara massal
dari banyak akun untuk manipulasi platform melanggar [X Rules][rules] dan
dapat menyebabkan akun di-suspend.

[rules]: https://help.x.com/en/rules-and-policies/x-rules
