"""Rate-limit probes: call each endpoint in a loop and print what comes back.

One file for every environment. Hosts, resource IDs and loop counts come from
the active profile, so `ENV=stage pytest tests/api/rate_limit` is the whole
switch — there is no per-environment copy of this file.

Tokens are short-lived and are NOT committed. Put them in your `.env`:

    RATE_LIMIT_BEARER_TOKEN=...        # CloudFront API, admin user
    RATE_LIMIT_TEAM_MEMBER_TOKEN=...   # same API, team-member user
    RATE_LIMIT_OAUTH_TOKEN=...         # OAuth host, "authorizationtoken" header

They expire within a day — refresh them from DevTools when these start
returning 401. Without them the tests fail immediately with a message naming
the variable, rather than looking like a rate-limit result.

These tests deliberately hammer endpoints and create records. Check which
environment you are pointed at before running them.
"""

import os

import pytest
from playwright.sync_api import Playwright

from crc_automation.api.payloads.create_affiliate import build_create_affiliate_payload
from crc_automation.api.payloads.create_client import build_create_client_payload
from crc_automation.api.payloads.forgot_password import FORGOT_PASSWORD
from crc_automation.api.payloads.login import LOGIN
from crc_automation.api.payloads.login_details import RESEND_LOGIN_DETAILS
from crc_automation.api.payloads.update_affiliate import build_update_affiliate_payload
from crc_automation.config.settings import (
    API_TEST_DATA_DIR,
    AUTH_API_BASE_URL,
    BASE_URL,
    CRC_API_BASE_URL,
    OAUTH_BASE_URL,
    require,
)

FORGOT_PASSWORD_PATH = "/api/forgot-password"
LOGIN_PATH = "/api/v1/login"

# How hard to push. QA used 101/3, stage 6/6, prod 100/6 — now per profile.
N_TIMES = int(os.getenv("RATE_LIMIT_N_TIMES", "101"))
IMPORT_N_TIMES = int(os.getenv("RATE_LIMIT_IMPORT_N_TIMES", "3"))

CSV_FILE = API_TEST_DATA_DIR / "clients_import.csv"
AFFILIATES_CSV_FILE = API_TEST_DATA_DIR / "affiliates_import.csv"


def _client_id() -> str:
    return require("RATE_LIMIT_CLIENT_ID")


def _affiliate_id() -> str:
    return require("RATE_LIMIT_AFFILIATE_ID")


@pytest.fixture(scope="session")
def authed_api(playwright: Playwright):
    """CloudFront API as the admin user."""
    context = playwright.request.new_context(
        base_url=CRC_API_BASE_URL,
        extra_http_headers={
            "Authorization": f"Bearer {require('RATE_LIMIT_BEARER_TOKEN')}"
        },
    )
    yield context
    context.dispose()


@pytest.fixture(scope="session")
def team_member_api(playwright: Playwright):
    """Same API as a team member — only validate-access needs this identity."""
    context = playwright.request.new_context(
        base_url=CRC_API_BASE_URL,
        extra_http_headers={
            "Authorization": f"Bearer {require('RATE_LIMIT_TEAM_MEMBER_TOKEN')}"
        },
    )
    yield context
    context.dispose()


def test_call_login_details_n_times(authed_api):
    path = f"/api/clients/{_client_id()}/login-details"
    for i in range(1, N_TIMES + 1):
        resp = authed_api.put(path, data=RESEND_LOGIN_DETAILS)
        print(f"Request {i}: status={resp.status} body={resp.text()}")


def test_create_client_n_times(authed_api):
    for i in range(1, N_TIMES + 1):
        payload = build_create_client_payload()  # new last_name + email each call
        resp = authed_api.post("/api/clients", data=payload)
        try:
            body = resp.json().get("message", resp.text())
        except Exception:
            body = resp.text()  # non-JSON response — print the whole thing
        print(
            f"Request {i}: last_name={payload['last_name']} email={payload['email']} "
            f"status={resp.status} body={body}"
        )


def test_login_activity_n_times(authed_api):
    # NOTE: the old qa copy called this with the team-member context while the
    # stage and prod copies used the admin one. Kept as the admin user, which
    # is what two of the three did and what the team-member comment implied.
    for i in range(1, N_TIMES + 1):
        resp = authed_api.post("/api/activities/login")
        print(f"Request {i}: status={resp.status} body={resp.text()}")


def test_create_affiliate_n_times(authed_api):
    for i in range(1, N_TIMES + 1):
        payload = build_create_affiliate_payload()  # new last_name + email each call
        resp = authed_api.post("/api/affiliates", data=payload)
        try:
            body = resp.json()["message"]
        except Exception:
            body = resp.text()
        print(
            f"Request {i}: last_name={payload['last_name']} email={payload['email']} "
            f"status={resp.status} body={body}"
        )


def test_update_affiliate_n_times(authed_api):
    path = f"/api/affiliates/{_affiliate_id()}"
    for i in range(1, N_TIMES + 1):
        payload = build_update_affiliate_payload()  # new last_name + phone each call
        resp = authed_api.put(path, data=payload)
        print(
            f"Request {i}: last_name={payload['last_name']} phone={payload['phone']} "
            f"status={resp.status} body={resp.text()}"
        )


def test_validate_access_n_times(team_member_api):
    # No payload; uses the team-member token via its own context.
    for i in range(1, N_TIMES + 1):
        resp = team_member_api.post("/api/users/validate-access")
        print(f"Request {i}: status={resp.status} body={resp.text()}")


def test_import_clients_csv_n_times(authed_api):
    # Uploads the clients CSV as multipart/form-data ("file" field) each call.
    for i in range(1, IMPORT_N_TIMES + 1):
        resp = authed_api.post(
            "/api/clients/imports",
            multipart={
                "file": {
                    "name": CSV_FILE.name,
                    "mimeType": "text/csv",
                    "buffer": CSV_FILE.read_bytes(),
                }
            },
        )
        print(f"Request {i}: status={resp.status} body={resp.text()}")


def test_import_affiliates_csv_n_times(authed_api):
    # Uploads the affiliates CSV as multipart/form-data ("file" field) each call.
    for i in range(1, IMPORT_N_TIMES + 1):
        resp = authed_api.post(
            "/api/affiliates/imports",
            multipart={
                "file": {
                    "name": AFFILIATES_CSV_FILE.name,
                    "mimeType": "text/csv",
                    "buffer": AFFILIATES_CSV_FILE.read_bytes(),
                }
            },
        )
        print(f"Request {i}: status={resp.status} body={resp.text()}")


def test_forgot_password_n_times(playwright: Playwright):
    # The OAuth host uses a custom "authorizationtoken" header, not Bearer, so
    # it needs its own request context rather than the authed_api fixture.
    # origin/referer follow BASE_URL — the old stage and prod copies still sent
    # the qa web app here, which was a copy-paste leftover.
    context = playwright.request.new_context(
        base_url=OAUTH_BASE_URL,
        extra_http_headers={
            "authorizationtoken": require("RATE_LIMIT_OAUTH_TOKEN"),
            "content-type": "application/json",
            "origin": BASE_URL,
            "referer": f"{BASE_URL}/",
        },
    )
    for i in range(1, N_TIMES + 1):
        resp = context.post(FORGOT_PASSWORD_PATH, data=FORGOT_PASSWORD)
        print(f"Request {i}: status={resp.status} body={resp.text()}")
    context.dispose()


def test_login_n_times(playwright: Playwright):
    # Auth-migration host has its own base URL and needs its own context.
    context = playwright.request.new_context(
        base_url=AUTH_API_BASE_URL,
        extra_http_headers={"content-type": "application/json"},
    )
    for i in range(1, N_TIMES + 1):
        resp = context.post(LOGIN_PATH, data=LOGIN)
        print(f"Request {i}: status={resp.status} body={resp.text()}")
    context.dispose()
