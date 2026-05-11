"""Tiny ANSI color helper.

Colors auto-disable when stdout is not a TTY (e.g. piped to a file, CI logs)
or when the NO_COLOR environment variable is set. On Windows, colors work on
modern terminals (Windows Terminal, PowerShell 7, VS Code) without extra
dependencies. On legacy cmd.exe we try to enable ANSI support automatically.
"""

from __future__ import annotations

import os
import sys


# ---- raw ANSI codes ----
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

# Foreground colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
GREY = "\033[90m"

# Bright variants
BRIGHT_GREEN = "\033[92m"
BRIGHT_RED = "\033[91m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_CYAN = "\033[96m"


def _supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    return True


def _enable_windows_ansi() -> None:
    """Best-effort enable ANSI processing on legacy Windows terminals."""
    if os.name != "nt":
        return
    try:
        import ctypes  # type: ignore

        kernel32 = ctypes.windll.kernel32
        # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass


_enable_windows_ansi()
_ENABLED = _supports_color()


def paint(text: str, color: str, bold: bool = False) -> str:
    """Wrap `text` with the given color code, or return it plain if disabled."""
    if not _ENABLED or not color:
        return text
    prefix = (BOLD if bold else "") + color
    return f"{prefix}{text}{RESET}"


# Convenience shortcuts used across the codebase.
def ok(text: str) -> str:
    return paint(text, BRIGHT_GREEN, bold=True)


def fail(text: str) -> str:
    return paint(text, BRIGHT_RED, bold=True)


def warn(text: str) -> str:
    return paint(text, BRIGHT_YELLOW)


def info(text: str) -> str:
    return paint(text, BRIGHT_CYAN)


def step_label(text: str) -> str:
    return paint(text, BLUE, bold=True)


def muted(text: str) -> str:
    return paint(text, GREY)


def highlight(text: str) -> str:
    return paint(text, BRIGHT_YELLOW, bold=True)


def header(text: str) -> str:
    return paint(text, BRIGHT_CYAN, bold=True)
