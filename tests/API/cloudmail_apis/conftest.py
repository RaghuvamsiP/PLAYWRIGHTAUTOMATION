import pytest
from playwright.sync_api import Playwright


@pytest.fixture(scope="session")
def request_context(playwright: Playwright):
    """Session-scoped Playwright APIRequestContext for the cloudmail API tests."""
    context = playwright.request.new_context()
    yield context
    context.dispose()
