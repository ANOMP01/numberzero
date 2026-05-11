---
inclusion: always
---

# Aturan: README selalu sinkron dengan kode

Setiap kali ada perubahan di project ini, **README.md wajib di-update di
commit yang sama**. README adalah satu-satunya dokumentasi tutorial untuk
user, jadi harus selalu mencerminkan kondisi terkini.

## Kapan README harus di-update

Update README bila menyentuh hal-hal berikut:

- Nama/path entry point (contoh: `python toolsx.py`, `./nz`, `nz.bat`)
- Tambah/hapus CLI flag atau ubah default-nya
- Tambah/hapus/rename file atau folder (terutama yang user-facing)
- Ubah format `emails.txt` atau tambah setting baru
- Ubah struktur folder media (`media/images/`, `media/videos/`)
- Tambah fitur baru yang bisa dipakai user (misal mode, opsi, shortcut)
- Ubah alur mode interaktif (langkah/menu/pertanyaan)
- Troubleshooting baru yang ditemui & solusinya

## Bagian README yang harus dijaga tetap konsisten

1. **Daftar Isi** — update kalau nomor/nama section berubah.
2. **Contoh perintah** — harus bisa di-copy-paste dan langsung jalan.
3. **Bagian "Opsi lengkap"** — list flag harus match dengan `--help`.
4. **Struktur project** (section 12) — harus match dengan isi workspace.
5. **Troubleshooting** — tambahkan bila ada error baru yang pernah dihadapi
   user.

## Standar bahasa

- Gunakan Bahasa Indonesia santai (user berkomunikasi dalam Bahasa Indonesia).
- Istilah teknis boleh Inggris (CLI, flag, dry-run, dll).
- Contoh kode & output tetap dalam format aslinya (tidak diterjemahkan).

## Checklist sebelum commit

- [ ] Kode diubah → README.md ikut diubah (section yang relevan)?
- [ ] Perintah di README masih valid (coba copy-paste jalankan)?
- [ ] Struktur folder di section 12 match dengan kondisi repo?
- [ ] Commit message mencakup perubahan kode DAN update README.
