#!/usr/bin/env bash
# One-time setup for numberzero (macOS / Linux).
# Usage: bash setup.sh

set -e
cd "$(dirname "${BASH_SOURCE[0]}")"

echo "[1/2] Install dependensi Python..."
if command -v pip3 >/dev/null 2>&1; then
    pip3 install -r requirements.txt
else
    pip install -r requirements.txt
fi

echo "     -> Install browser untuk login..."
python3 -m playwright install chromium 2>/dev/null || python -m playwright install chromium 2>/dev/null || true

echo "[2/2] Cek emails.txt..."
if [ ! -f emails.txt ]; then
    echo "     -> emails.txt belum ada. Edit file emails.txt dan isi email + password."
else
    echo "     -> emails.txt sudah ada."
fi

echo
echo "Selesai!"
echo "Jalankan: python sessions.py"
