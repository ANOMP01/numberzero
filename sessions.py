#!/usr/bin/env python3
"""sessions.py - Login/daftar akun X dan simpan session.

Jalankan file ini untuk login ke semua akun yang terdaftar di accounts.yaml.
Session yang tersimpan akan dipakai oleh toolsx.py untuk posting.

Usage:
    python sessions.py           # login semua akun dari accounts.yaml
    python sessions.py --manual  # login manual satu per satu (tanpa file email)
"""

import sys
import time
from pathlib import Path

import yaml

from src.auth import (
    get_session_file,
    list_saved_sessions,
    login_auto,
    login_interactive,
)
from src import colors as c


def main() -> int:
    print()
    print(c.header("  sessions.py  |  Login & Simpan Session X"))
    print(c.muted("=" * 56))
    print()

    # Check for --manual flag
    manual_mode = "--manual" in sys.argv

    if manual_mode:
        return _manual_login()

    # Auto mode: read from accounts.yaml
    config_path = Path("accounts.yaml")
    if not config_path.exists():
        print(c.fail("File accounts.yaml tidak ditemukan."))
        print("Buat dulu dari template:")
        print("  cp accounts.example.yaml accounts.yaml")
        print("  lalu isi email dan password di dalamnya.")
        return 2

    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    emails = data.get("emails", []) or []
    default_password = str(data.get("default_password", ""))
    custom_accounts = data.get("accounts_custom", []) or []

    if not emails:
        print(c.warn("Tidak ada email di accounts.yaml."))
        print("Tambahkan daftar email seperti ini di accounts.yaml:\n")
        print("  emails:")
        print('    - akun1@gmail.com')
        print('    - akun2@gmail.com')
        print()
        print("Atau jalankan mode manual: python sessions.py --manual")
        return 2

    if not default_password:
        print(c.fail("default_password belum diisi di accounts.yaml."))
        print('Tambahkan: default_password: "PasswordKamu123"')
        return 2

    # Build login list
    custom_pw_map = {
        a["email"]: a["password"]
        for a in custom_accounts
        if isinstance(a, dict) and "email" in a and "password" in a
    }

    login_list: list[tuple[str, str, str]] = []
    for email in emails:
        pw = custom_pw_map.get(email, default_password)
        name = email.split("@")[0].replace(".", "_")
        login_list.append((email, pw, name))

    # Show existing sessions
    sessions = list_saved_sessions()
    if sessions:
        print(f"Session yang sudah ada: "
              + ", ".join(c.info(f"@{s.name}") for s in sessions))
        print()

    # Show what will be logged in
    print(f"Ditemukan {c.highlight(str(len(login_list)))} email di accounts.yaml:")
    print()
    for email, _, name in login_list:
        existing = get_session_file(name).exists()
        status = c.muted(" (sudah ada session)") if existing else ""
        print(f"  {c.highlight('•')} {email} → {c.info('@' + name)}{status}")
    print()
    print(f"Password default: {c.muted('*' * 8)}")
    print()

    # Confirm
    confirm = input("Login semua sekarang? [Y/n]: ").strip().lower()
    if confirm in ("n", "no", "tidak"):
        print(c.warn("Dibatalkan."))
        return 0

    # Login one by one
    print()
    success = 0
    failed = 0
    for i, (email, pw, name) in enumerate(login_list, 1):
        print(c.step_label(f"[{i}/{len(login_list)}]") + f" {email}")
        try:
            login_auto(email, pw, name)
            print(c.ok(f"  ✓ @{name} berhasil!\n"))
            success += 1
        except TimeoutError as e:
            print(c.fail(f"  ✗ {e}\n"))
            failed += 1
        except Exception as e:
            print(c.fail(f"  ✗ Error: {e}\n"))
            failed += 1

        # Delay between accounts
        if i < len(login_list):
            time.sleep(2)

    # Summary
    print()
    print(c.muted("-" * 56))
    print(f"  Selesai: {c.ok(str(success))} berhasil, {c.fail(str(failed))} gagal")
    print()

    sessions = list_saved_sessions()
    print(f"  Total session tersimpan: {c.highlight(str(len(sessions)))}")
    for s in sessions:
        status = c.ok("aktif") if s.has_session else c.fail("kosong")
        print(f"    @{s.name} ({status})")

    print()
    print(f"  Untuk posting, jalankan:")
    print(f"    {c.info('python toolsx.py --session')}")
    print()
    return 0


def _manual_login() -> int:
    """Login manual satu per satu tanpa file email."""
    print("Mode manual: login lewat browser satu per satu.\n")

    sessions = list_saved_sessions()
    if sessions:
        print(f"Session yang sudah ada: "
              + ", ".join(c.info(f"@{s.name}") for s in sessions))
        print()

    while True:
        name = input("Nama akun (label bebas, misal: main): ").strip()
        if not name:
            print(c.warn("Nama tidak boleh kosong."))
            continue

        try:
            login_interactive(name)
            print(c.ok(f"  ✓ @{name} berhasil & session tersimpan!\n"))
        except TimeoutError as e:
            print(c.fail(f"  ✗ {e}\n"))
        except Exception as e:
            print(c.fail(f"  ✗ Error: {e}\n"))

        lagi = input("Login akun lain? [y/N]: ").strip().lower()
        if lagi not in ("y", "ya", "yes"):
            break

    sessions = list_saved_sessions()
    print(f"\nTotal session: {c.highlight(str(len(sessions)))}")
    for s in sessions:
        status = c.ok("aktif") if s.has_session else c.fail("kosong")
        print(f"  @{s.name} ({status})")
    print(f"\nUntuk posting: {c.info('python toolsx.py --session')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
