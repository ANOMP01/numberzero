"""Command-line entry point for numberzero."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from .config import Account, ConfigError, filter_accounts, load_config
from . import colors as c
from .auth import (
    get_session_file,
    list_saved_sessions,
    login_interactive,
    SessionAccount,
)
from .interactive import (
    ask_accounts,
    ask_media,
    ask_text,
    banner,
    confirm,
)
from .poster import PostResult, post_tweet, post_tweet_session


TWEET_MAX_CHARS = 280


# ---------- argparse ----------

def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="numberzero",
        description=(
            "Post the same tweet (with optional images/video) "
            "from multiple X accounts. Run with no arguments for interactive mode."
        ),
    )
    parser.add_argument("-t", "--text", default=None,
                        help="Tweet text (can be empty if media is provided).")
    parser.add_argument("-m", "--media", action="append", default=[],
                        help="Path to a media file. Repeat for multiple images.")
    parser.add_argument("-c", "--config", default="accounts.yaml",
                        help="Path to accounts YAML (default: accounts.yaml).")
    parser.add_argument("-a", "--accounts", default="",
                        help="Comma-separated account names (overrides --count).")
    parser.add_argument("-n", "--count", type=int, default=None,
                        help="How many accounts to post from "
                             "(default: default_count in config).")
    parser.add_argument("-d", "--delay", type=float, default=2.0,
                        help="Seconds between accounts (default: 2.0).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate and list targets without posting.")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Force interactive mode even if flags are given.")
    parser.add_argument("--login", action="store_true",
                        help="(Gunakan sessions.py) Login & simpan session.")
    parser.add_argument("--session", action="store_true",
                        help="Post using saved sessions instead of API keys.")
    return parser.parse_args(argv)


# ---------- log formatting ----------

def _fmt_header(selected: list[Account], media: list[Path], dry_run: bool) -> str:
    names = ", ".join(c.info(f"@{a.name}") for a in selected)
    bar = c.muted("=" * 56)
    lines = ["", bar, f"  Target : {c.highlight(str(len(selected)))} akun -> {names}"]
    if media:
        media_names = ", ".join(c.info(p.name) for p in media)
        lines.append(f"  Media  : {c.highlight(str(len(media)))} file -> {media_names}")
    if dry_run:
        lines.append("  Mode   : " + c.warn("DRY RUN (tidak benar-benar diposting)"))
    lines.append(bar)
    return "\n".join(lines)


def _fmt_progress(i: int, total: int, account: Account) -> str:
    label = c.step_label(f"[{i}/{total}]")
    return f"\n{label} {c.info('@' + account.name)}"


def _fmt_result(result: PostResult) -> str:
    if result.ok:
        badge = c.ok("[BERHASIL]")
        return f"   {badge}  tweet id: {c.muted(str(result.tweet_id))}"
    badge = c.fail("[GAGAL]   ")
    return f"   {badge}  {c.fail(result.error or '')}"


def _fmt_summary(results: list[PostResult]) -> str:
    ok_list = [r for r in results if r.ok]
    fail_list = [r for r in results if not r.ok]
    bar = c.muted("-" * 56)

    ok_count = c.ok(str(len(ok_list))) if ok_list else str(len(ok_list))
    fail_count = c.fail(str(len(fail_list))) if fail_list else str(len(fail_list))
    total = len(results)

    lines = [
        "",
        bar,
        f"  Ringkasan: {ok_count} berhasil, {fail_count} gagal (total {total})",
    ]
    if ok_list:
        names = ", ".join(c.info(f"@{r.account}") for r in ok_list)
        lines.append(f"  {c.ok('Berhasil')} : {names}")
    if fail_list:
        names = ", ".join(c.info(f"@{r.account}") for r in fail_list)
        lines.append(f"  {c.fail('Gagal')}    : {names}")
    lines.append(bar)
    return "\n".join(lines)


# ---------- login & session helpers ----------

def _handle_login() -> int:
    """Interactive login flow: add sessions one by one."""
    import yaml
    from .auth import login_auto, login_interactive

    print()
    print(c.header("  Login & Simpan Session"))
    print(c.muted("=" * 56))
    print()

    # Try to load email list from accounts.yaml
    config_path = Path("accounts.yaml")
    emails: list[str] = []
    default_password = ""
    custom_accounts: list[dict] = []

    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        emails_raw = data.get("emails", []) or []
        # Support both list format and comma-separated string
        if isinstance(emails_raw, str):
            emails = [e.strip() for e in emails_raw.split(",") if e.strip()]
        else:
            emails = list(emails_raw)
        default_password = str(data.get("default_password", ""))
        custom_accounts = data.get("accounts_custom", []) or []

    sessions = list_saved_sessions()
    if sessions:
        print(f"Session yang sudah tersimpan: "
              + ", ".join(c.info(f"@{s.name}") for s in sessions))
        print()

    # If emails found in config, offer auto-login
    if emails and default_password:
        print(f"Ditemukan {c.highlight(str(len(emails)))} email di accounts.yaml")
        print(f"Password default: {'*' * min(len(default_password), 8)}...")
        print()

        # Build login list: email -> password
        login_list: list[tuple[str, str, str]] = []
        custom_pw_map = {a["email"]: a["password"] for a in custom_accounts if "email" in a and "password" in a}

        for email in emails:
            pw = custom_pw_map.get(email, default_password)
            name = email.split("@")[0].replace(".", "_")
            login_list.append((email, pw, name))

        print("Akun yang akan di-login:")
        for email, _, name in login_list:
            existing = get_session_file(name).exists()
            status = c.muted("(session ada)") if existing else ""
            print(f"  - {email} → @{name} {status}")
        print()

        mode = input("Login semua otomatis? [Y/n]: ").strip().lower()
        if mode in ("", "y", "ya", "yes"):
            success = 0
            for email, pw, name in login_list:
                try:
                    login_auto(email, pw, name)
                    print(c.ok(f"  [{name}] Berhasil!\n"))
                    success += 1
                except TimeoutError as e:
                    print(c.fail(f"  {e}\n"))
                except Exception as e:
                    print(c.fail(f"  [{name}] Error: {e}\n"))
                time.sleep(2)

            print(f"\n{c.ok(str(success))}/{len(login_list)} akun berhasil login.")
            sessions = list_saved_sessions()
            for s in sessions:
                status = c.ok("aktif") if s.has_session else c.fail("kosong")
                print(f"  - @{s.name} ({status})")
            return 0

    # Fallback: manual login one by one
    print("Mode manual: login satu per satu lewat browser.\n")
    while True:
        name = input("Nama akun (ketik nama bebas, misal: main): ").strip()
        if not name:
            print(c.warn("Nama tidak boleh kosong."))
            continue

        try:
            login_interactive(name)
            print(c.ok(f"  Login @{name} berhasil & session tersimpan!\n"))
        except TimeoutError as e:
            print(c.fail(f"  {e}\n"))
        except Exception as e:
            print(c.fail(f"  Error: {e}\n"))

        lagi = input("Login akun lain? [y/N]: ").strip().lower()
        if lagi not in ("y", "ya", "yes"):
            break

    sessions = list_saved_sessions()
    print(f"\nTotal session tersimpan: {c.highlight(str(len(sessions)))}")
    for s in sessions:
        status = c.ok("aktif") if s.has_session else c.fail("kosong")
        print(f"  - @{s.name} ({status})")
    print(f"\nUntuk posting, jalankan: "
          + c.info("python toolsx.py --session"))
    return 0


def _handle_session_post(args) -> int:
    """Post using saved sessions instead of API keys."""
    sessions = list_saved_sessions()
    if not sessions:
        print(c.fail("Belum ada session tersimpan."))
        print(f"Jalankan dulu: {c.info('python toolsx.py --login')}")
        return 2

    # Determine text & media
    text = args.text
    media_paths = [Path(m) for m in args.media] if args.media else []

    if text is None and not media_paths:
        # Interactive-ish: ask for text and media
        print()
        print(c.header("  Posting via Session"))
        print(c.muted("=" * 56))
        print()
        text = input("Tweet : ").strip()
        # Simple media ask
        media_input = input("Path media (kosongkan jika tidak ada): ").strip()
        if media_input:
            media_paths = [Path(p.strip()) for p in media_input.split(",")]

    if not (text or "").strip() and not media_paths:
        print(c.fail("Tidak ada teks maupun media. Batal."), file=sys.stderr)
        return 2

    text = text or ""

    # Select which sessions to use
    print(f"\nSession tersedia:")
    for i, s in enumerate(sessions, 1):
        status = c.ok("aktif") if s.has_session else c.fail("expired?")
        print(f"  {c.highlight(str(i))}) @{s.name} ({status})")

    print()
    pick = input(f"Pilih akun (angka dipisah koma, atau Enter = semua): ").strip()
    if pick:
        indices = [int(x.strip()) for x in pick.split(",") if x.strip().isdigit()]
        selected = [sessions[i - 1] for i in indices if 1 <= i <= len(sessions)]
    else:
        selected = sessions

    if not selected:
        print(c.fail("Tidak ada akun dipilih."))
        return 2

    # Post
    print(_fmt_header_session(selected, media_paths))
    results: list[PostResult] = []
    total = len(selected)
    for i, session in enumerate(selected, 1):
        print(_fmt_progress(i, total, type("A", (), {"name": session.name})))
        print("   " + c.muted("mengirim via session..."), end="", flush=True)
        result = post_tweet_session(session.name, session.cookies_file, text, media_paths)
        print("\r" + _fmt_result(result))
        results.append(result)
        if i < total:
            time.sleep(3)  # Longer delay for session-based to avoid detection

    print(_fmt_summary(results))
    fail_count = sum(1 for r in results if not r.ok)
    return 0 if fail_count == 0 else 1


def _fmt_header_session(selected: list, media: list[Path]) -> str:
    names = ", ".join(c.info(f"@{s.name}") for s in selected)
    bar = c.muted("=" * 56)
    lines = ["", bar, f"  Target : {c.highlight(str(len(selected)))} akun -> {names}"]
    lines.append("  Mode   : " + c.info("SESSION (browser cookies)"))
    if media:
        media_names = ", ".join(c.info(p.name) for p in media)
        lines.append(f"  Media  : {c.highlight(str(len(media)))} file -> {media_names}")
    lines.append(bar)
    return "\n".join(lines)


# ---------- main ----------

def _is_interactive_mode(args: argparse.Namespace) -> bool:
    """Use interactive if explicitly asked, or if no tweet content was given."""
    if args.interactive:
        return True
    return args.text is None and not args.media


def _select_accounts_by_flags(
    args: argparse.Namespace, config
) -> list[Account]:
    names = [n for n in args.accounts.split(",") if n.strip()]
    if names:
        return filter_accounts(config.accounts, names)

    count = args.count if args.count is not None else config.default_count
    if count < 1:
        raise ConfigError("--count must be at least 1.")
    if count > len(config.accounts):
        print(c.warn(f"  (catatan) diminta {count} akun, hanya "
                     f"{len(config.accounts)} tersedia -> pakai semua."),
              file=sys.stderr)
        count = len(config.accounts)
    return config.accounts[:count]


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    # --- Login mode: redirect to sessions.py ---
    if args.login:
        print(c.warn("Untuk login, jalankan file terpisah:"))
        print(f"  {c.info('python sessions.py')}")
        print(f"  {c.info('python sessions.py --manual')}  (mode manual)")
        return 0

    # --- Session posting mode ---
    if args.session:
        return _handle_session_post(args)

    # Load config up-front; both modes need it.
    try:
        config = load_config(args.config)
    except ConfigError as e:
        print(c.fail(f"Config error: {e}"), file=sys.stderr)
        return 2

    # --- Interactive mode ---
    if _is_interactive_mode(args):
        banner()
        text = ask_text()
        media_paths = ask_media(config)
        selected = ask_accounts(config)

        if not text.strip() and not media_paths:
            print(c.fail("Tidak ada teks maupun media. Batal."), file=sys.stderr)
            return 2

        if not confirm(text, media_paths, selected):
            print(c.warn("Dibatalkan."))
            return 0

    # --- Flag mode ---
    else:
        text = args.text or ""
        media_paths = [Path(m) for m in args.media]

        if not text.strip() and not media_paths:
            print(c.fail("Error: beri --text dan/atau --media."), file=sys.stderr)
            return 2
        if len(text) > TWEET_MAX_CHARS:
            print(c.fail(f"Error: teks {len(text)} karakter "
                         f"(maks {TWEET_MAX_CHARS})."), file=sys.stderr)
            return 2

        try:
            selected = _select_accounts_by_flags(args, config)
        except ConfigError as e:
            print(c.fail(f"Config error: {e}"), file=sys.stderr)
            return 2

    # --- Actually post (or dry-run) ---
    print(_fmt_header(selected, media_paths, args.dry_run))

    if args.dry_run:
        print("\n" + c.warn("Dry run selesai. Tidak ada yang diposting.") + "\n")
        return 0

    results: list[PostResult] = []
    total = len(selected)
    for i, account in enumerate(selected, 1):
        print(_fmt_progress(i, total, account))
        print("   " + c.muted("mengirim..."), end="", flush=True)
        result = post_tweet(account, text, media_paths)
        # overwrite the "mengirim..." line with the real status
        print("\r" + _fmt_result(result))
        results.append(result)
        if i < total and args.delay > 0:
            time.sleep(args.delay)

    print(_fmt_summary(results))
    fail_count = sum(1 for r in results if not r.ok)
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
