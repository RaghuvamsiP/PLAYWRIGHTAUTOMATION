"""Creates and stores the authenticated browser session used by the UI suite."""

from playwright.sync_api import sync_playwright

from crc_automation.config.settings import (
    AUTH_DIR,
    AUTH_FILE,
    DEFAULT_EMAIL,
    DEFAULT_PASSWORD,
    HEADLESS,
    LOGIN_URL,
)

__all__ = ["AUTH_FILE", "create_auth"]


def create_auth():
    """Log in once and persist the storage state to AUTH_FILE."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context()
        page = context.new_page()

        page.goto(LOGIN_URL, timeout=60000)

        page.get_by_placeholder("Email or User ID").fill(DEFAULT_EMAIL)
        page.get_by_placeholder("Password").fill(DEFAULT_PASSWORD)
        page.locator("button[type='submit']").click()

        page.wait_for_url("**/app/home")

        AUTH_DIR.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=AUTH_FILE)

        browser.close()
