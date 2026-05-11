"""Command-line entry point for numberzero."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from .config import ConfigError, filter_accounts, load_accounts
from .poster import PostResult, post_tweet


TWEET_MAX_CHARS = 280


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="numberzero",
        description=(
            "Post the same tweet (with optional images/video) "
            "from multiple X accounts."
        ),
    )
    parser.add_argument(
        "-t",
        "--text",
        default="",
        help="Tweet text (can be empty if media is provided).",
    )
    parser.add_argument(
        "-m",
        "--media",
        action="append",
        default=[],
        help=(
            "Path to a media file (image or video). "
            "Repeat to attach up to 4 images."
        ),
    )
    parser.add_argument(
        "-c",
        "--config",
        default="accounts.yaml",
        help="Path to the accounts YAML file (default: accounts.yaml).",
    )
    parser.add_argument(
        "-a",
        "--accounts",
        default="",
        help=(
            "Comma-separated list of account names to post from. "
            "Default: all accounts in the config."
        ),
    )
    parser.add_argument(
        "-d",
        "--delay",
        type=float,
        default=2.0,
        help="Seconds to wait between accounts (default: 2.0).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and list target accounts, but do not post.",
    )
    return parser.parse_args(argv)


def _print_result(result: PostResult) -> None:
    if result.ok:
        print(f"  [OK]   {result.account} -> tweet id: {result.tweet_id}")
    else:
        print(f"  [FAIL] {result.account} -> {result.error}")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    text = args.text or ""
    media_paths = [Path(m) for m in args.media]

    if not text.strip() and not media_paths:
        print("Error: provide --text and/or --media.", file=sys.stderr)
        return 2

    if len(text) > TWEET_MAX_CHARS:
        print(
            f"Error: tweet text is {len(text)} chars (max {TWEET_MAX_CHARS}).",
            file=sys.stderr,
        )
        return 2

    try:
        all_accounts = load_accounts(args.config)
        selected = filter_accounts(
            all_accounts,
            [n for n in args.accounts.split(",") if n.strip()],
        )
    except ConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
        return 2

    print(f"Posting to {len(selected)} account(s): "
          f"{', '.join(a.name for a in selected)}")
    if media_paths:
        print(f"Attaching {len(media_paths)} media file(s): "
              f"{', '.join(str(p) for p in media_paths)}")

    if args.dry_run:
        print("Dry run: nothing was posted.")
        return 0

    results: list[PostResult] = []
    for i, account in enumerate(selected):
        result = post_tweet(account, text, media_paths)
        results.append(result)
        _print_result(result)
        if i < len(selected) - 1 and args.delay > 0:
            time.sleep(args.delay)

    ok_count = sum(1 for r in results if r.ok)
    fail_count = len(results) - ok_count
    print(f"\nDone. Success: {ok_count}, Failed: {fail_count}")
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
