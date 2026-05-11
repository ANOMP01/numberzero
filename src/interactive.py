"""Interactive, menu-driven flow for composing and sending a tweet.

Kept deliberately simple: plain input() prompts with numbered choices.
No external TUI libraries, so it works anywhere Python runs.
"""

from __future__ import annotations

from pathlib import Path

from . import colors as c
from .config import Account, Config


# File extensions we support, grouped by media folder.
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
VIDEO_EXTS = {".mp4", ".mov"}


# ---------- small display helpers ----------

def _hr(char: str = "-", width: int = 56) -> str:
    return c.muted(char * width)


def banner() -> None:
    line = "=" * 56
    print()
    print(c.muted(line))
    print(c.header("  numberzero  |  multi-account X event poster"))
    print(c.muted(line))


def step(n: int, total: int, title: str) -> None:
    print()
    print(c.step_label(f"[Langkah {n}/{total}]") + " " + c.paint(title, c.BOLD))
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
            print(c.warn("  -> harus berupa angka. Coba lagi."))
            continue
        if n < minimum:
            print(c.warn(f"  -> minimal {minimum}. Coba lagi."))
            continue
        if maximum is not None and n > maximum:
            print(c.warn(f"  -> maksimal {maximum}. Coba lagi."))
            continue
        return n


def _ask_yes_no(prompt: str, default: bool = False) -> bool:
    default_str = "Y/n" if default else "y/N"
    while True:
        raw = input(f"{prompt} [{c.highlight(default_str)}]: ").strip().lower()
        if not raw:
            return default
        if raw in ("y", "ya", "yes"):
            return True
        if raw in ("n", "no", "tidak"):
            return False
        print(c.warn("  -> ketik 'y' atau 'n'."))


def _ask_choice(prompt: str, options: list[str], default: int = 1) -> int:
    """Show numbered menu; return the 1-based index the user picked."""
    for i, opt in enumerate(options, 1):
        if i == default:
            marker = c.highlight("*")
            num = c.highlight(str(i))
        else:
            marker = " "
            num = str(i)
        print(f"  {marker} {num}) {opt}")
    while True:
        raw = _ask(prompt, str(default))
        try:
            choice = int(raw)
        except ValueError:
            print(c.warn("  -> ketik angka pilihan."))
            continue
        if 1 <= choice <= len(options):
            return choice
        print(c.warn(f"  -> pilih antara 1 dan {len(options)}."))


# ---------- each step ----------

def ask_text() -> str:
    step(1, 4, "Tulis isi tweet")
    print("Ketik tweet lalu Enter. Maks 280 karakter.")
    print("Biarkan kosong kalau cuma mau posting media saja.")
    while True:
        text = input("Tweet : ").strip()
        if len(text) > 280:
            print(c.fail(f"  -> kepanjangan ({len(text)}/280). Coba ringkas."))
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
    print(f"File tersedia di {c.info(str(folder) + '/')}:")
    if not files:
        print(c.muted("  (folder kosong)"))
        return
    for i, p in enumerate(files, 1):
        try:
            size = _human_size(p.stat().st_size)
        except OSError:
            size = "?"
        num = c.highlight(f"{i:>2}")
        print(f"  {num}) {p.name}  {c.muted('(' + size + ')')}")


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
                print(c.warn(f"  -> bukan angka: {tok!r}"))
                bad = True
                break
            idx = int(tok)
            if not (1 <= idx <= len(files)):
                print(c.warn(f"  -> {idx} di luar jangkauan 1..{len(files)}"))
                bad = True
                break
            if idx in seen:
                continue
            seen.add(idx)
            picked.append(files[idx - 1])

        if bad or not picked:
            continue
        if len(picked) > max_pick:
            print(c.warn(f"  -> maksimal {max_pick} file. Pilih lagi."))
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
            print(c.warn(f"Taruh gambar di {folder}/ lalu jalankan lagi."))
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
        print(c.warn(f"Taruh video/GIF di {folder}/ lalu jalankan lagi."))
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
        print(f"    {c.highlight(str(i))}) " + c.info(f"@{a.name}"))
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
        print(c.warn("  -> tidak ada akun yang cocok. Coba lagi."))


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
            print(c.warn(f"  -> tidak dikenal: {tok!r} (lewati)"))
            continue
        if account.name in seen:
            continue
        seen.add(account.name)
        picked.append(account)
    return picked


def confirm(text: str, media: list[Path], targets: list[Account]) -> bool:
    step(4, 4, "Konfirmasi sebelum posting")
    print(c.paint("Ringkasan:", c.BOLD))
    if text:
        preview = text if len(text) <= 80 else text[:77] + "..."
        print(f"  Teks   : {preview}")
    else:
        print("  Teks   : " + c.muted("(tidak ada teks)"))
    if media:
        print(f"  Media  : {c.highlight(str(len(media)))} file")
        for p in media:
            print(c.muted(f"           - {p}"))
    else:
        print("  Media  : " + c.muted("(tidak ada)"))
    targets_str = ", ".join(c.info("@" + a.name) for a in targets)
    print(f"  Target : {c.highlight(str(len(targets)))} akun -> {targets_str}")
    print()
    return _ask_yes_no("Lanjutkan posting sekarang?", default=True)
