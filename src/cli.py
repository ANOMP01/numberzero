"""Command-line entry point for numberzero."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from .config import Account, ConfigError, filter_accounts, load_config
from . import colors as c
from .interactive import (
    ask_accounts,
    ask_media,
    ask_text,
    banner,
    confirm,
)
from .poster import PostResult, post_tweet


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
