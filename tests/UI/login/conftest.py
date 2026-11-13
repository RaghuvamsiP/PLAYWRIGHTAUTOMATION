import pytest
import allure
from playwright.sync_api import sync_playwright

from config.settings import HEADLESS


@pytest.fixture(scope="session")
def unauthenticated_browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        yield browser
        browser.close()


@pytest.fixture
def fresh_page(unauthenticated_browser, request):
    """Provides a fresh browser page with no stored auth state — required for login tests."""
    context = unauthenticated_browser.new_context(permissions=["clipboard-read", "clipboard-write"])
    page = context.new_page()
    yield page

    # On failure: attach screenshot, current URL, and page source to Allure
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
    context.close()
