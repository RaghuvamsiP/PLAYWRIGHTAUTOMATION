"""Root pytest configuration.

Provides the shared authenticated browser/context/page fixtures and the
report hook that lets page-level fixtures detect a failed test.
"""

import os
import time

import pytest
from playwright.sync_api import sync_playwright

from config.settings import HEADLESS
from utils.auth_helper import AUTH_FILE, create_auth

SESSION_MAX_AGE_SECONDS = 2 * 60 * 60  # 2 hours


def _refresh_auth_if_expired():
    """Regenerate auth.json if it is missing or older than SESSION_MAX_AGE_SECONDS."""
    if not os.path.exists(AUTH_FILE):
        print("\n[auth] auth.json not found — creating fresh session...")
        create_auth()
        return

    age = time.time() - os.path.getmtime(AUTH_FILE)
    if age > SESSION_MAX_AGE_SECONDS:
        print(f"\n[auth] Session expired ({int(age / 60)} min old) — refreshing auth.json...")
        create_auth()


@pytest.fixture(scope="session")
def browser():
    """Authenticated browser, reusing the stored session so tests skip login."""
    _refresh_auth_if_expired()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        yield browser
        browser.close()


@pytest.fixture(scope="session")
def context(browser):
    context = browser.new_context(storage_state=AUTH_FILE)

    # Block tracking popups that overlay UI elements
    context.route("**/*userproof*", lambda route: route.abort())
    context.route("**/*intercom*", lambda route: route.abort())

    yield context
    context.close()


@pytest.fixture
def page(context):
    page = context.new_page()
    yield page
    page.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Store each phase's report on the item so fixtures can see failures.

    Fixtures read this as `getattr(request.node, "rep_call", None)` — `rep_call`
    is absent when a test errors during setup.
    """
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
