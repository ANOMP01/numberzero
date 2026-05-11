#!/usr/bin/env bash
# One-time setup for numberzero (macOS / Linux).
# Usage: bash setup.sh

set -e
cd "$(dirname "${BASH_SOURCE[0]}")"

echo "[1/3] Install dependensi Python..."
if command -v pip3 >/dev/null 2>&1; then
    pip3 install -r requirements.txt
else
    pip install -r requirements.txt
fi

echo "     -> Install browser untuk login..."
python3 -m playwright install chromium 2>/dev/null || python -m playwright install chromium 2>/dev/null || true

echo "[2/3] Buat accounts.yaml kalau belum ada..."
if [ ! -f accounts.yaml ]; then
    cp accounts.example.yaml accounts.yaml
    echo "     -> accounts.yaml dibuat. Edit file itu & isi kredensialnya."
else
    echo "     -> accounts.yaml sudah ada, dilewati."
fi

echo "[3/3] Bikin 'nz' bisa langsung dijalankan..."
chmod +x nz

echo
echo "Selesai!"
echo "Sekarang tinggal ketik:  ./nz"
