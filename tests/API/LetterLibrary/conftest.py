import os

import pytest
from playwright.sync_api import Playwright

from tests.API.helpers.auth import login_and_get_token

AUTH_BASE_URL = "https://prod-auth-migration.creditrepaircloud.com"
LOGIN_PATH = "/api/v1/login"
API_BASE_URL = "https://api.creditrepaircloud.com"
EMAIL_ENV_VAR = "CRC_SUPPORT_EMAIL"
PASSWORD_ENV_VAR = "CRC_SUPPORT_PASSWORD"


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        pytest.fail(f"Environment variable {name} must be set for Letter Library tests")
    return value


@pytest.fixture(scope="session")
def token(playwright: Playwright) -> str:
    """Authenticate once through the login API and return the bearer token."""
    email = _required_env(EMAIL_ENV_VAR)
    password = _required_env(PASSWORD_ENV_VAR)
    request = playwright.request.new_context(
        base_url=AUTH_BASE_URL,
        extra_http_headers={"Content-Type": "application/json"},
    )
    try:
        return login_and_get_token(request, email, password, LOGIN_PATH)
    finally:
        request.dispose()


@pytest.fixture(scope="session")
def auth_api(playwright: Playwright, token: str):
    """Provide an API request context authenticated with the login token."""
    context = playwright.request.new_context(
        base_url=API_BASE_URL,
        extra_http_headers={"Authorization": f"Bearer {token}"},
    )
    yield context
    context.dispose()
