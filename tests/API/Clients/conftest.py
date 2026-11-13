import os

import pytest
from playwright.sync_api import Playwright

from config.settings import AUTH_API_BASE_URL, CRC_API_BASE_URL, LOGIN_API_PATH
from tests.API.helpers.auth import get_company_id, login_and_get_token

# Service account for the Clients API suite. Override in CI rather than
# editing these defaults.
EMAIL = os.getenv("CRC_CLIENTS_EMAIL", "tollysystem@testmail.creditrepaircloud.com")
PASSWORD = os.getenv("CRC_CLIENTS_PASSWORD", "P@ssw0rd12345")


@pytest.fixture(scope="session")
def token(playwright: Playwright) -> str:
    """Authenticate once through the login API and return the bearer token."""
    request = playwright.request.new_context(
        base_url=AUTH_API_BASE_URL,
        extra_http_headers={"Content-Type": "application/json"},
    )

    try:
        return login_and_get_token(request, EMAIL, PASSWORD, LOGIN_API_PATH)
    finally:
        request.dispose()


@pytest.fixture(scope="session")
def auth_api(playwright: Playwright, token: str):
    """Provide a reusable Clients API context authenticated with the login token."""
    context = playwright.request.new_context(
        base_url=CRC_API_BASE_URL,
        extra_http_headers={"Authorization": f"Bearer {token}"},
    )
    yield context
    context.dispose()


@pytest.fixture(scope="session")
def company_id(auth_api) -> int:
    """Return the company ID used by report processing requests."""
    return get_company_id(auth_api)
