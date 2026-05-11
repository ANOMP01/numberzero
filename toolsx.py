#!/usr/bin/env python3
"""toolsx - entry point for numberzero.

Usage:
    python toolsx.py                       # mode interaktif (menu step-by-step)
    python toolsx.py -t "Halo" -m foto.jpg # mode cepat (flag)
    python toolsx.py --help                # lihat semua opsi
"""

from src.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
