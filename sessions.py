#!/usr/bin/env python3
"""sessions.py - Login/daftar akun X dan simpan session.

Baca email dari emails.txt (satu email per baris).
Baris pertama yang dimulai dengan "password:" adalah password default.

Usage:
    python sessions.py           # login semua akun dari emails.txt
    python sessions.py --manual  # login manual satu per satu
"""

import sys
import time
from pathlib import Path

from src.auth import (
    get_session_file,
    list_saved_sessions,
    login_auto,
    login_interactive,
)
from src import colors as c


EMAILS_FILE = Path("emails.txt")


def _read_emails_file() -> tuple[str, list[str]]:
    """Read emails.txt. Returns (password, list_of_emails).
    
    Format file:
        password: xxx
        email1@domain.com
        email2@domain.com
    """
    if not EMAILS_FILE.exists():
        return "", []

    password = ""
    emails = []

    with EMAILS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Line starts with "password:" -> extract password
            if line.lower().startswith("password:"):
                password = line.split(":", 1)[1].strip().strip('"').strip("'")
            elif "@" in line:
                emails.append(line)

    return password, emails


def main() -> int:
    print()
    print(c.header("  sessions.py  |  Login & Simpan Session X"))
    print(c.muted("=" * 56))
    print()

    # Check for --manual flag
    if "--manual" in sys.argv:
        return _manual_login()

    # Read emails.txt
    if not EMAILS_FILE.exists():
        print(c.fail(f"File emails.txt tidak ditemukan."))
        print()
        print("Buat file emails.txt dengan isi seperti ini:")
        print()
        print("  password: PasswordKamu123")
        print("  akun1@gmail.com")
        print("  akun2@gmail.com")
        print("  akun3@gmail.com")
        return 2

    password, emails = _read_emails_file()

    if not emails:
        print(c.fail("Tidak ada email di emails.txt."))
        print("Isi file emails.txt dengan email (satu per baris).")
        return 2

    if not password:
        print(c.fail("Password belum diisi di emails.txt."))
        print("Tambahkan baris pertama: password: PasswordKamu123")
        return 2

    # Show existing sessions
    sessions = list_saved_sessions()
    if sessions:
        print(f"Session yang sudah ada: "
              + ", ".join(c.info(f"@{s.name}") for s in sessions))
        print()

    # Show what will be logged in
    print(f"Ditemukan {c.highlight(str(len(emails)))} email di emails.txt:")
    print()
    for email in emails:
        name = email.split("@")[0].replace(".", "_")
        existing = get_session_file(name).exists()
        status = c.muted(" (sudah ada session)") if existing else ""
        print(f"  {c.highlight('•')} {email} → {c.info('@' + name)}{status}")
    print()
    print(f"Password: {c.muted('*' * 8)}")
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
    for i, email in enumerate(emails, 1):
        name = email.split("@")[0].replace(".", "_")
        print(c.step_label(f"[{i}/{len(emails)}]") + f" {email}")
        try:
            login_auto(email, password, name)
            print(c.ok(f"  ✓ @{name} berhasil!\n"))
            success += 1
        except TimeoutError as e:
            print(c.fail(f"  ✗ {e}\n"))
            failed += 1
        except Exception as e:
            print(c.fail(f"  ✗ Error: {e}\n"))
            failed += 1

        if i < len(emails):
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
