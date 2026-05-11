"""Interactive, menu-driven flow for composing and sending a tweet.

Kept deliberately simple: plain input() prompts with numbered choices.
No external TUI libraries, so it works anywhere Python runs.
"""

from __future__ import annotations

from pathlib import Path

from .config import Account, Config


# File extensions we support, grouped by media folder.
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
VIDEO_EXTS = {".mp4", ".mov"}


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


def _human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def _list_media_files(folder: Path, allowed_exts: set[str]) -> list[Path]:
    """Return supported media files inside `folder`, sorted by name."""
    if not folder.exists() or not folder.is_dir():
        return []
    files = [
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in allowed_exts
    ]
    return sorted(files, key=lambda p: p.name.lower())


def _show_file_menu(files: list[Path], folder: Path) -> None:
    print(f"File tersedia di {folder}/:")
    if not files:
        print("  (folder kosong)")
        return
    for i, p in enumerate(files, 1):
        try:
            size = _human_size(p.stat().st_size)
        except OSError:
            size = "?"
        print(f"  {i:>2}) {p.name}  ({size})")


def _pick_files(files: list[Path], prompt: str, max_pick: int) -> list[Path]:
    """Ask user for numbers (comma-separated) and return the chosen files."""
    while True:
        raw = _ask(prompt)
        if not raw:
            print("  -> minimal pilih satu file.")
            continue

        tokens = [t.strip() for t in raw.split(",") if t.strip()]
        picked: list[Path] = []
        seen: set[int] = set()
        bad = False
        for tok in tokens:
            if not tok.isdigit():
                print(f"  -> bukan angka: {tok!r}")
                bad = True
                break
            idx = int(tok)
            if not (1 <= idx <= len(files)):
                print(f"  -> {idx} di luar jangkauan 1..{len(files)}")
                bad = True
                break
            if idx in seen:
                continue
            seen.add(idx)
            picked.append(files[idx - 1])

        if bad or not picked:
            continue
        if len(picked) > max_pick:
            print(f"  -> maksimal {max_pick} file. Pilih lagi.")
            continue
        return picked


def ask_media(config: Config) -> list[Path]:
    step(2, 4, "Lampirkan media?")
    options = [
        "Tidak, teks saja",
        "Gambar (dari folder gambar)",
        "Video / GIF (dari folder video)",
    ]
    choice = _ask_choice("Pilihan", options, default=1)

    if choice == 1:
        return []

    if choice == 2:
        folder = config.images_dir
        files = _list_media_files(folder, IMAGE_EXTS)
        print()
        _show_file_menu(files, folder)
        if not files:
            print(f"Taruh gambar di {folder}/ lalu jalankan lagi.")
            return []
        print()
        return _pick_files(
            files,
            "Ketik nomor gambar (boleh lebih dari satu, dipisah koma; maks 4)",
            max_pick=4,
        )

    # choice == 3: video / GIF
    folder = config.videos_dir
    files = _list_media_files(folder, VIDEO_EXTS | {".gif"})
    print()
    _show_file_menu(files, folder)
    if not files:
        print(f"Taruh video/GIF di {folder}/ lalu jalankan lagi.")
        return []
    print()
    return _pick_files(
        files,
        "Ketik nomor video/GIF (hanya 1 file)",
        max_pick=1,
    )


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
