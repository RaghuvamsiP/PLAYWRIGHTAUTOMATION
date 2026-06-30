import os
import time
import pytest
from playwright.sync_api import sync_playwright
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
        print(f"\n[auth] Session expired ({int(age/60)} min old) — refreshing auth.json...")
        create_auth()


# @pytest.fixture(scope="session")
# def browser():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         yield browser
#         browser.close()
#
#
# @pytest.fixture(scope="session")
# def context(browser):
#     context = browser.new_context()
#
#     # block tracking popups
#     context.route("**/*userproof*", lambda route: route.abort())
#     context.route("**/*intercom*", lambda route: route.abort())
#
#     page = context.new_page()
#
#     # login once
#     page.goto("https://qa.creditrepaircloud.com/login")
#     page.get_by_placeholder("Email or User ID").fill("pm@yopmail.com")
#     page.get_by_placeholder("Password").fill("Test@1234")
#     page.locator("button[type='submit']").click()
#
#     page.wait_for_url("**/app/home", timeout=10000)
#
#     yield context
#
#     context.close()
#
#
# @pytest.fixture
# def page(context):
#     page = context.new_page()
#     yield page
#     page.close()


"""Temp fixture for skipping login for each testcase"""


@pytest.fixture(scope="session")
def browser():
    _refresh_auth_if_expired()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
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


@pytest.fixture  # (scope ="function")
def page(context):
    page = context.new_page()
    yield page
    page.close()




