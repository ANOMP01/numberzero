"""Post tweets (with optional media) to X on behalf of a single account."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import tweepy

from .config import Account


# Media type constraints per X API docs.
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
VIDEO_EXTS = {".mp4", ".mov"}
ALLOWED_EXTS = IMAGE_EXTS | VIDEO_EXTS

# X allows up to 4 images OR 1 GIF OR 1 video per tweet.
MAX_IMAGES = 4


class PostError(Exception):
    """Raised when a tweet cannot be posted."""


@dataclass
class PostResult:
    account: str
    ok: bool
    tweet_id: str | None = None
    error: str | None = None


def _validate_media(paths: Sequence[Path]) -> None:
    if not paths:
        return

    for p in paths:
        if not p.exists():
            raise PostError(f"Media file not found: {p}")
        if p.suffix.lower() not in ALLOWED_EXTS:
            raise PostError(
                f"Unsupported media type: {p.suffix} "
                f"(allowed: {sorted(ALLOWED_EXTS)})"
            )

    has_video = any(p.suffix.lower() in VIDEO_EXTS for p in paths)
    has_gif = any(p.suffix.lower() == ".gif" for p in paths)

    if has_video and len(paths) > 1:
        raise PostError("Only one video may be attached per tweet.")
    if has_gif and len(paths) > 1:
        raise PostError("Only one GIF may be attached per tweet.")
    if len(paths) > MAX_IMAGES:
        raise PostError(f"At most {MAX_IMAGES} images may be attached per tweet.")


def _build_v1_api(account: Account) -> tweepy.API:
    """Build a v1.1 API client (needed for media uploads)."""
    auth = tweepy.OAuth1UserHandler(
        account.api_key,
        account.api_secret,
        account.access_token,
        account.access_token_secret,
    )
    return tweepy.API(auth)


def _build_v2_client(account: Account) -> tweepy.Client:
    """Build a v2 client (used to create the tweet itself)."""
    return tweepy.Client(
        consumer_key=account.api_key,
        consumer_secret=account.api_secret,
        access_token=account.access_token,
        access_token_secret=account.access_token_secret,
    )


def _upload_media(api_v1: tweepy.API, paths: Sequence[Path]) -> list[str]:
    """Upload each media file via v1.1 media/upload and return media_ids."""
    media_ids: list[str] = []
    for p in paths:
        is_video = p.suffix.lower() in VIDEO_EXTS
        # chunked=True is required for videos and works for images too.
        media = api_v1.media_upload(filename=str(p), chunked=is_video)
        media_ids.append(media.media_id_string)
    return media_ids


def post_tweet_session(
    account_name: str,
    cookies_file: "Path",
    text: str,
    media_paths: Sequence[Path] | None = None,
) -> PostResult:
    """Post using saved browser session (no API keys needed)."""
    from .auth import post_with_session

    media_paths = list(media_paths or [])
    try:
        _validate_media(media_paths)
        result = post_with_session(cookies_file, text, media_paths)
        if result["ok"]:
            return PostResult(account=account_name, ok=True, tweet_id="(via session)")
        return PostResult(account=account_name, ok=False, error=result["error"])
    except PostError as e:
        return PostResult(account=account_name, ok=False, error=str(e))
    except Exception as e:
        return PostResult(account=account_name, ok=False, error=f"Unexpected: {e}")


def post_tweet(
    account: Account,
    text: str,
    media_paths: Sequence[Path] | None = None,
) -> PostResult:
    """Post a single tweet for one account. Never raises on post failure."""
    media_paths = list(media_paths or [])
    try:
        _validate_media(media_paths)

        media_ids: list[str] | None = None
        if media_paths:
            api_v1 = _build_v1_api(account)
            media_ids = _upload_media(api_v1, media_paths)

        client = _build_v2_client(account)
        response = client.create_tweet(text=text or None, media_ids=media_ids)

        tweet_id = None
        if response and getattr(response, "data", None):
            tweet_id = str(response.data.get("id"))
        return PostResult(account=account.name, ok=True, tweet_id=tweet_id)

    except PostError as e:
        return PostResult(account=account.name, ok=False, error=str(e))
    except tweepy.TweepyException as e:
        return PostResult(account=account.name, ok=False, error=f"X API error: {e}")
    except Exception as e:  # pragma: no cover - safety net
        return PostResult(account=account.name, ok=False, error=f"Unexpected: {e}")
