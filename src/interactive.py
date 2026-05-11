"""Interactive, menu-driven flow for composing and sending a tweet.

Kept deliberately simple: plain input() prompts with numbered choices.
No external TUI libraries, so it works anywhere Python runs.
"""

from __future__ import annotations

from pathlib import Path

from .config import Account, Config


# ---------- small display helpers ----------

def _hr(char: str = "-", width: int = 56) -> str:
    return char * width


def banner() -> None:
    print()
    print(_hr("="))
    print("  numberzero  |  multi-account X event poster")
    print(_hr("="))


def step(n: int, total: int, title: str) -> None:
    print()
    print(f"[Langkah {n}/{total}] {title}")
    print(_hr())


# ---------- prompt helpers ----------

def _ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    value = input(f"{prompt}{suffix}: ").strip()
    if not value and default is not None:
        return default
    return value


def _ask_int(prompt: str, default: int, minimum: int = 1, maximum: int | None = None) -> int:
    while True:
        raw = _ask(prompt, str(default))
        try:
            n = int(raw)
        except ValueError:
            print("  -> harus berupa angka. Coba lagi.")
            continue
        if n < minimum:
            print(f"  -> minimal {minimum}. Coba lagi.")
            continue
        if maximum is not None and n > maximum:
            print(f"  -> maksimal {maximum}. Coba lagi.")
            continue
        return n


def _ask_yes_no(prompt: str, default: bool = False) -> bool:
    default_str = "Y/n" if default else "y/N"
    while True:
        raw = input(f"{prompt} [{default_str}]: ").strip().lower()
        if not raw:
            return default
        if raw in ("y", "ya", "yes"):
            return True
        if raw in ("n", "no", "tidak"):
            return False
        print("  -> ketik 'y' atau 'n'.")


def _ask_choice(prompt: str, options: list[str], default: int = 1) -> int:
    """Show numbered menu; return the 1-based index the user picked."""
    for i, opt in enumerate(options, 1):
        marker = "*" if i == default else " "
        print(f"  {marker} {i}) {opt}")
    while True:
        raw = _ask(prompt, str(default))
        try:
            choice = int(raw)
        except ValueError:
            print("  -> ketik angka pilihan.")
            continue
        if 1 <= choice <= len(options):
            return choice
        print(f"  -> pilih antara 1 dan {len(options)}.")


# ---------- each step ----------

def ask_text() -> str:
    step(1, 4, "Tulis isi tweet")
    print("Ketik tweet lalu Enter. Maks 280 karakter.")
    print("Biarkan kosong kalau cuma mau posting media saja.")
    while True:
        text = input("Tweet : ").strip()
        if len(text) > 280:
            print(f"  -> kepanjangan ({len(text)}/280). Coba ringkas.")
            continue
        return text


def ask_media() -> list[Path]:
    step(2, 4, "Lampirkan media?")
    options = [
        "Tidak, teks saja",
        "Ya, 1 gambar",
        "Ya, beberapa gambar (maks 4)",
        "Ya, 1 video / GIF",
    ]
    choice = _ask_choice("Pilihan", options, default=1)

    if choice == 1:
        return []

    paths: list[Path] = []
    if choice == 3:
        n = _ask_int("Berapa gambar", default=2, minimum=1, maximum=4)
    else:
        n = 1

    for i in range(1, n + 1):
        while True:
            raw = _ask(f"  Path file #{i}")
            if not raw:
                print("  -> path tidak boleh kosong.")
                continue
            p = Path(raw).expanduser()
            if not p.exists():
                print(f"  -> file tidak ditemukan: {p}")
                continue
            paths.append(p)
            break
    return paths


def ask_accounts(config: Config) -> list[Account]:
    step(3, 4, "Pilih akun yang akan memposting")

    accounts = config.accounts
    print("Akun yang terdaftar di accounts.yaml:")
    for i, a in enumerate(accounts, 1):
        print(f"    {i}) @{a.name}")
    print()

    options = [
        f"Pakai default ({config.default_count} akun pertama)",
        "Pilih jumlah akun (ambil dari urutan teratas)",
        "Pilih akun spesifik (ketik nomor/nama)",
        "Semua akun",
    ]
    choice = _ask_choice("Pilihan", options, default=1)

    if choice == 1:
        n = min(config.default_count, len(accounts))
        return accounts[:n]

    if choice == 2:
        n = _ask_int("Berapa akun", default=config.default_count,
                     minimum=1, maximum=len(accounts))
        return accounts[:n]

    if choice == 4:
        return list(accounts)

    # choice == 3: specific accounts
    while True:
        raw = _ask("Ketik nomor/nama dipisah koma (contoh: 1,3 atau main,event)")
        picked = _resolve_account_tokens(raw, accounts)
        if picked:
            return picked
        print("  -> tidak ada akun yang cocok. Coba lagi.")


def _resolve_account_tokens(raw: str, accounts: list[Account]) -> list[Account]:
    tokens = [t.strip() for t in raw.split(",") if t.strip()]
    by_name = {a.name: a for a in accounts}
    picked: list[Account] = []
    seen: set[str] = set()
    for tok in tokens:
        account: Account | None = None
        if tok.isdigit():
            idx = int(tok)
            if 1 <= idx <= len(accounts):
                account = accounts[idx - 1]
        elif tok in by_name:
            account = by_name[tok]

        if account is None:
            print(f"  -> tidak dikenal: {tok!r} (lewati)")
            continue
        if account.name in seen:
            continue
        seen.add(account.name)
        picked.append(account)
    return picked


def confirm(text: str, media: list[Path], targets: list[Account]) -> bool:
    step(4, 4, "Konfirmasi sebelum posting")
    print("Ringkasan:")
    preview = text if text else "(tidak ada teks)"
    if len(preview) > 80:
        preview = preview[:77] + "..."
    print(f"  Teks   : {preview}")
    if media:
        print(f"  Media  : {len(media)} file")
        for p in media:
            print(f"           - {p}")
    else:
        print("  Media  : (tidak ada)")
    print(f"  Target : {len(targets)} akun -> "
          f"{', '.join('@' + a.name for a in targets)}")
    print()
    return _ask_yes_no("Lanjutkan posting sekarang?", default=True)
