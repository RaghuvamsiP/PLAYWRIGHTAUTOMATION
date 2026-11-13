from typing import Any

from playwright.sync_api import APIRequestContext


LOGIN_PATH = "/api/v1/login"
USER_DETAILS_PATH = "/api/user-details"


def login_and_get_token(
    request: APIRequestContext,
    email: str,
    password: str,
    login_path: str = LOGIN_PATH,
) -> str:
    """Authenticate through the login API and return the CRC bearer token."""
    response = request.post(
        login_path,
        data={"username": email, "password": password},
    )
    if not response.ok:
        raise AssertionError(
            f"Login API failed with status {response.status}: {response.text()}"
        )

    body: Any = response.json()
    data = body.get("data") if isinstance(body, dict) else None
    crc_data = data.get("crc") if isinstance(data, dict) else None
    token = crc_data.get("access_token") if isinstance(crc_data, dict) else None

    if not token:
        raise AssertionError("Login API succeeded but did not return data.crc.access_token")

    return token


def get_company_id(request: APIRequestContext) -> int:
    """Fetch the authenticated user's company_id from the user-details API."""
    response = request.get(USER_DETAILS_PATH)
    if not response.ok:
        raise AssertionError(
            f"User details API failed with status {response.status}: {response.text()}"
        )

    body: Any = response.json()
    company_id = body.get("team_details", {}).get("company_id")
    if not company_id:
        raise AssertionError(
            "User details API succeeded but did not return team_details.company_id"
        )

    return company_id