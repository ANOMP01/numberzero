"""Login to X via browser and save/load session cookies.

Flow:
1. Open a real browser (Playwright Chromium, headed mode).
2. User logs in manually (email + password + 2FA if any).
3. After login detected, cookies are saved to sessions/<name>.json.
4. Next time, cookies are loaded from file — no login needed.

Sessions are stored per-account so multiple accounts can coexist.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from dataclasses import dataclass

SESSIONS_DIR = Path("sessions")
X_HOME_URL = "https://x.com/home"
X_LOGIN_URL = "https://x.com/i/flow/login"


@dataclass
class SessionAccount:
    """An account that authenticates via saved browser session."""
    name: str
    cookies_file: Path

    @property
    def has_session(self) -> bool:
        return self.cookies_file.exists() and self.cookies_file.stat().st_size > 10


def get_session_file(name: str) -> Path:
    """Return the path where session cookies for `name` would be stored."""
    SESSIONS_DIR.mkdir(exist_ok=True)
    return SESSIONS_DIR / f"{name}.json"


def list_saved_sessions() -> list[SessionAccount]:
    """List all accounts that have a saved session file."""
    SESSIONS_DIR.mkdir(exist_ok=True)
    sessions = []
    for f in sorted(SESSIONS_DIR.glob("*.json")):
        name = f.stem
        sessions.append(SessionAccount(name=name, cookies_file=f))
    return sessions


def login_interactive(name: str) -> Path:
    """Open browser for user to login. Save cookies after success.
    
    Returns the path to the saved cookies file.
    """
    from playwright.sync_api import sync_playwright

    cookies_file = get_session_file(name)
    
    print(f"\n  Membuka browser untuk login akun: @{name}")
    print("  Login secara manual (email + password).")
    print("  Setelah berhasil masuk ke halaman Home, browser akan otomatis tertutup.\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        page.goto(X_LOGIN_URL)

        # Wait until user is logged in (URL changes to /home or similar)
        print("  Menunggu kamu login...")
        max_wait = 300  # 5 minutes max
        start = time.time()
        while time.time() - start < max_wait:
            url = page.url
            # Logged in indicators: URL is /home, or has /compose, or
            # the page has the "Post" compose button
            if "/home" in url or "/compose" in url:
                break
            try:
                # Check for the compose tweet button as a sign of being logged in
                if page.query_selector('[data-testid="tweetTextarea_0"]'):
                    break
                if page.query_selector('[data-testid="SideNav_NewTweet_Button"]'):
                    break
            except Exception:
                pass
            time.sleep(2)
        else:
            browser.close()
            raise TimeoutError(
                "Timeout: login tidak terdeteksi dalam 5 menit. Coba lagi."
            )

        # Small delay to let cookies finalize
        time.sleep(3)

        # Save cookies
        cookies = context.cookies()
        cookies_file.parent.mkdir(exist_ok=True)
        with cookies_file.open("w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2)

        browser.close()

    print(f"  Session disimpan: {cookies_file}")
    return cookies_file


def login_auto(email: str, password: str, name: str | None = None) -> Path:
    """Auto-login to X using email + password. Save cookies.
    
    Opens a headed browser, fills in credentials automatically.
    User may still need to handle captcha/2FA manually if prompted.
    
    Args:
        email: Email or username for the X account.
        password: Password for the X account.
        name: Label for the session file. Defaults to email prefix.
    
    Returns the path to the saved cookies file.
    """
    from playwright.sync_api import sync_playwright

    if not name:
        name = email.split("@")[0]

    cookies_file = get_session_file(name)

    print(f"\n  [{name}] Login otomatis: {email}")
    print("  Browser akan terbuka. Kalau ada captcha/verifikasi, selesaikan manual.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        page.goto(X_LOGIN_URL, wait_until="networkidle")
        time.sleep(3)

        # Step 1: Fill email/username
        try:
            email_input = page.wait_for_selector(
                'input[autocomplete="username"], input[name="text"]',
                timeout=15000,
            )
            email_input.click()
            email_input.fill(email)
            time.sleep(1)

            # Click "Next"
            next_btn = page.query_selector('[role="button"]:has-text("Next")') or \
                       page.query_selector('[role="button"]:has-text("Berikutnya")')
            if next_btn:
                next_btn.click()
            else:
                page.keyboard.press("Enter")
            time.sleep(3)
        except Exception:
            print("  (tidak bisa otomatis isi email — selesaikan manual)")

        # Step 2: Fill password
        try:
            pw_input = page.wait_for_selector(
                'input[name="password"], input[type="password"]',
                timeout=15000,
            )
            pw_input.click()
            pw_input.fill(password)
            time.sleep(1)

            # Click "Log in"
            login_btn = page.query_selector('[data-testid="LoginForm_Login_Button"]') or \
                        page.query_selector('[role="button"]:has-text("Log in")') or \
                        page.query_selector('[role="button"]:has-text("Masuk")')
            if login_btn:
                login_btn.click()
            else:
                page.keyboard.press("Enter")
            time.sleep(5)
        except Exception:
            print("  (tidak bisa otomatis isi password — selesaikan manual)")

        # Step 3: Wait for Home (or user to complete captcha/2FA)
        print("  Menunggu login berhasil (maks 5 menit)...")
        max_wait = 300
        start = time.time()
        while time.time() - start < max_wait:
            url = page.url
            if "/home" in url or "/compose" in url:
                break
            try:
                if page.query_selector('[data-testid="SideNav_NewTweet_Button"]'):
                    break
            except Exception:
                pass
            time.sleep(2)
        else:
            browser.close()
            raise TimeoutError(
                f"[{name}] Timeout: login tidak berhasil dalam 5 menit."
            )

        time.sleep(3)

        # Save cookies
        cookies = context.cookies()
        cookies_file.parent.mkdir(exist_ok=True)
        with cookies_file.open("w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2)

        browser.close()

    print(f"  [{name}] Session disimpan: {cookies_file}")
    return cookies_file


def load_cookies(cookies_file: Path) -> list[dict]:
    """Load cookies from a saved session file."""
    with cookies_file.open("r", encoding="utf-8") as f:
        return json.load(f)


def post_with_session(
    cookies_file: Path,
    text: str,
    media_paths: list[Path] | None = None,
) -> dict:
    """Post a tweet using saved session cookies.
    
    Returns dict with keys: ok (bool), tweet_url (str|None), error (str|None)
    """
    from playwright.sync_api import sync_playwright

    cookies = load_cookies(cookies_file)
    media_paths = list(media_paths or [])

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        context.add_cookies(cookies)
        page = context.new_page()

        try:
            # Navigate to compose
            page.goto("https://x.com/compose/post", wait_until="networkidle", timeout=30000)
            time.sleep(2)

            # Check if we're still logged in
            if "/login" in page.url or "/i/flow/login" in page.url:
                browser.close()
                return {"ok": False, "tweet_url": None, "error": "Session expired. Jalankan --login ulang."}

            # Type the tweet text
            if text:
                tweet_box = page.wait_for_selector(
                    '[data-testid="tweetTextarea_0"]',
                    timeout=15000,
                )
                tweet_box.click()
                tweet_box.fill(text)
                time.sleep(1)

            # Upload media if any
            if media_paths:
                file_input = page.wait_for_selector(
                    'input[data-testid="fileInput"]',
                    timeout=10000,
                )
                abs_paths = [str(p.resolve()) for p in media_paths]
                file_input.set_input_files(abs_paths)
                # Wait for upload to process
                time.sleep(3 + len(media_paths) * 2)

            # Click the Post button
            post_btn = page.wait_for_selector(
                '[data-testid="tweetButton"]',
                timeout=10000,
            )
            post_btn.click()

            # Wait for post to go through
            time.sleep(4)

            # Try to detect success (URL might change, or toast appears)
            browser.close()
            return {"ok": True, "tweet_url": None, "error": None}

        except Exception as e:
            browser.close()
            return {"ok": False, "tweet_url": None, "error": str(e)}
