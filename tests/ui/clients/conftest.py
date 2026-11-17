import pytest
import allure
from playwright.sync_api import sync_playwright

from crc_automation.config.settings import HEADLESS, require
from crc_automation.config.urls import AppURLs



@pytest.fixture(scope="session")
def pdf_user_browser():
    """Launch a browser and login with pdf@yopmail.com credentials.
    Session-scoped so the login happens once for all tests using this fixture."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context()

        # Block tracking popups that overlay UI elements
        context.route("**/*userproof*", lambda route: route.abort())
        context.route("**/*intercom*", lambda route: route.abort())

        # Login once for the entire session
        login_page = context.new_page()
        login_page.goto(AppURLs.Auth.LOGIN, wait_until="domcontentloaded", timeout=60000)
        login_page.get_by_placeholder("Email or User ID").fill(
            require("CRC_PDF_USER_EMAIL")
        )
        login_page.get_by_placeholder("Password").fill(
            require("CRC_PDF_USER_PASSWORD")
        )
        login_page.get_by_role("button", name="Login").click()
        login_page.wait_for_url(f"**{AppURLs.Auth.HOME}", timeout=30000)
        login_page.close()

        yield browser, context

        context.close()
        browser.close()


@pytest.fixture
def pdf_user_page(pdf_user_browser, request):
    """Provides a fresh page tab within the authenticated pdf@yopmail.com session."""
    browser, context = pdf_user_browser
    page = context.new_page()
    yield page

    # On failure: attach screenshot and URL to Allure
    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        allure.attach(
            page.screenshot(full_page=True),
            name="Screenshot on Failure",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            page.url,
            name="Page URL on Failure",
            attachment_type=allure.attachment_type.TEXT,
        )

    page.close()
