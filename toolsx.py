#!/usr/bin/env python3
"""toolsx.py - Posting ke X dari banyak akun sekaligus.

Jalankan file ini untuk posting. Session harus sudah tersimpan
(jalankan sessions.py dulu untuk login).

Usage:
    python toolsx.py                                    # mode interaktif
    python toolsx.py --session                          # posting via session
    python toolsx.py --session -t "Halo" -m poster.jpg  # mode cepat
    python toolsx.py --help                             # lihat semua opsi
"""

from src.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
