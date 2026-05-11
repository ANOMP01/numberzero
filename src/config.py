"""Load and validate account credentials from a YAML file."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml


REQUIRED_FIELDS = (
    "name",
    "api_key",
    "api_secret",
    "access_token",
    "access_token_secret",
)

# Fallback when accounts.yaml does not set `default_count`.
DEFAULT_ACCOUNT_COUNT = 2

# Default media folders, relative to the project root.
DEFAULT_IMAGES_DIR = "media/images"
DEFAULT_VIDEOS_DIR = "media/videos"


class ConfigError(Exception):
    """Raised when the accounts config file is missing or malformed."""


@dataclass(frozen=True)
class Account:
    name: str
    api_key: str
    api_secret: str
    access_token: str
    access_token_secret: str


@dataclass(frozen=True)
class Config:
    """Parsed accounts config: the full account list plus defaults."""

    accounts: list[Account]
    default_count: int
    images_dir: Path
    videos_dir: Path


def load_config(path: str | Path) -> Config:
    """Load accounts + settings from a YAML file."""
    path = Path(path)
    if not path.exists():
        raise ConfigError(
            f"Accounts file not found: {path}. "
            f"This file is only needed for API mode. Use --session instead."
        )

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    raw_accounts = data.get("accounts")
    if not isinstance(raw_accounts, list) or not raw_accounts:
        raise ConfigError(
            f"{path} must contain a non-empty top-level 'accounts' list."
        )

    accounts: list[Account] = []
    seen_names: set[str] = set()
    for idx, entry in enumerate(raw_accounts):
        if not isinstance(entry, dict):
            raise ConfigError(f"Account #{idx + 1} must be a mapping.")

        missing = [f for f in REQUIRED_FIELDS if not entry.get(f)]
        if missing:
            label = entry.get("name") or f"#{idx + 1}"
            raise ConfigError(
                f"Account {label} is missing required fields: {', '.join(missing)}"
            )

        name = str(entry["name"]).strip()
        if name in seen_names:
            raise ConfigError(f"Duplicate account name: {name!r}")
        seen_names.add(name)

        accounts.append(
            Account(
                name=name,
                api_key=str(entry["api_key"]),
                api_secret=str(entry["api_secret"]),
                access_token=str(entry["access_token"]),
                access_token_secret=str(entry["access_token_secret"]),
            )
        )

    raw_default = data.get("default_count", DEFAULT_ACCOUNT_COUNT)
    try:
        default_count = int(raw_default)
    except (TypeError, ValueError):
        raise ConfigError(
            f"`default_count` must be an integer, got: {raw_default!r}"
        )
    if default_count < 1:
        raise ConfigError("`default_count` must be at least 1.")

    images_dir = Path(str(data.get("images_dir", DEFAULT_IMAGES_DIR))).expanduser()
    videos_dir = Path(str(data.get("videos_dir", DEFAULT_VIDEOS_DIR))).expanduser()

    return Config(
        accounts=accounts,
        default_count=default_count,
        images_dir=images_dir,
        videos_dir=videos_dir,
    )


def load_accounts(path: str | Path) -> list[Account]:
    """Backwards-compatible helper: return just the list of accounts."""
    return load_config(path).accounts


def filter_accounts(
    accounts: list[Account], names: Iterable[str] | None
) -> list[Account]:
    """Filter accounts by a list of names. If names is None/empty, return all."""
    names = [n.strip() for n in (names or []) if n and n.strip()]
    if not names:
        return accounts

    by_name = {a.name: a for a in accounts}
    missing = [n for n in names if n not in by_name]
    if missing:
        available = ", ".join(a.name for a in accounts)
        raise ConfigError(
            f"Unknown account name(s): {', '.join(missing)}. Available: {available}"
        )
    return [by_name[n] for n in names]
