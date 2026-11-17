import pytest
from playwright.sync_api import Playwright

# -------------------------------------------------------------------
# Fixture: Creates a reusable Playwright Request Context for the session
# -------------------------------------------------------------------


@pytest.fixture(scope="session")
def api_request(playwright: Playwright):
    context = playwright.request.new_context()
    yield context
    context.dispose()



