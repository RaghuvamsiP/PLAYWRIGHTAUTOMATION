import pytest
import allure
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def unauthenticated_browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture
def fresh_page(unauthenticated_browser, request):
    """Provides a fresh browser page with no stored auth state — required for login tests."""
    context = unauthenticated_browser.new_context(permissions=["clipboard-read", "clipboard-write"])
    page = context.new_page()
    yield page

    # On failure: attach screenshot, current URL, and page source to Allure
    if request.node.rep_call and request.node.rep_call.failed:
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


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Store test result on the item so the fresh_page fixture can access it."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
