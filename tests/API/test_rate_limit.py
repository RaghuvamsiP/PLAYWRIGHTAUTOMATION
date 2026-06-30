"""
PUT /api/clients/{client_id}/login-details — call 4 times and print the response.
Uses a Playwright APIRequestContext with a static bearer token.
"""

import pytest
from pathlib import Path
from playwright.sync_api import Playwright

from tests.API.payloads.login_details import RESEND_LOGIN_DETAILS
from tests.API.payloads.create_client import build_create_client_payload
from tests.API.payloads.create_affiliate import build_create_affiliate_payload
from tests.API.payloads.update_affiliate import build_update_affiliate_payload
from tests.API.payloads.forgot_password import FORGOT_PASSWORD

BEARER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6IjQyYWQ2ZWM0NjhiNmZiNDk2OTI1ZDVjYmYwZjEzNjhmNTFjZDMxNTIxYmNmODNiMDJlM2VlMjc5ZmUwZThjNGFlZDY4ZTI0NTZhYmE4N2FhIiwiY29tcGFueV9uYW1lIjoiIiwiZmlyc3RfbmFtZSI6IlJhdGUgTGltaXQiLCJsYXN0X25hbWUiOiJUcmlhbCIsImFkbWluX2VtYWlsIjoicmF0ZWxpbWl0dHJpYWxAeW9wbWFpbC5jb20iLCJ1c2VyX2lkIjo0MjYxNzEsInJlZ19pZCI6MTAwMzA3OCwiYmlsbGluZ19yZWZfaWQiOm51bGwsInVzZXJfdHlwZSI6ImFkbWluIiwiYWNjb3VudF9zdGF0dXMiOiJhY3RpdmUiLCJyZWN1cmx5X3BheW1lbnRfc3RhdHVzIjoidHJpYWwiLCJjb3VudHJ5X2NvZGUiOjIyNCwiY291bnRyeV9uYW1lIjoiVW5pdGVkIFN0YXRlcyIsInR3b19kaWdpdF9jb3VudHJ5X2NvZGUiOiJVUyIsImN1cnJlbmN5X2NvZGUiOiJVU0QiLCJjdXJyZW5jeV9zeW1ib2wiOiIkIiwidGltZXpvbmUiOiJBbWVyaWNhL0xvc19BbmdlbGVzIiwiaXNfZWFybHlfYWNjZXNzIjoxLCJpc19wcmVfbGF1bmNoIjpmYWxzZSwiY2hhcmdlYmVlX2Vucm9sbGVkIjpmYWxzZSwiY2hhcmdlYmVlX2VuYWJsZWQiOmZhbHNlLCJjcmNfYmlsbGluZ19lbmFibGVkIjpmYWxzZSwiaWF0IjoxNzgxNzgxNDAzLCJuYmYiOjE3ODE3ODE0MDMsImV4cCI6MTc4MTg2NzgwMywicGxhbl9uYW1lIjoiU3RhcnQiLCJwdXJjaGFzZWRfbWFzdGVyY2xhc3MiOiJubyIsImlzX3NpZ25lZCI6dHJ1ZSwic2lnbnVwX3N0YXR1cyI6ImNvbXBsZXRlIn0.Q7dWSrh3etqttDZG2gcqViQF_IxuaGcorZeS-UF42hyF2BNeXLkoNhTz8YSZqVpgVmFRLMw75VtPBDB_O0lql3mXyrDnmaOytDFL_Ok0Qh8Fg8tDIlx0pP7XSUJwXquWoF-9z79rKiIIXgiZ4lnP_g_IuqEKlAQelv6gOuf9WQyqy3ald_7LQbDVHGWYM6V33K4iyrCJ6hg-mMPC3uDrnAEM4Rd7CIy_BOI_L-TkLOF0-LmeA5z3IR3qdd7YtL2x1d-WJxeFeFJbVBl4_BWCDH0wUuYwKMkTi-9dFAD1S75BrHGWRiOQ6cQNbAiWl8omgyM5CNib4Yvclpx_LCfjKg"


# Team-member token, used only by the validate-access test.
TEAM_MEMBER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6ImJkMTgyN2FlMmE2NTEzNGJlMWM0ZDIyMjI3YjIxM2I3ZGNkNzUzNmVjYTRiMjNlZjM1Mzc0YTUyYWFlMzBhMTE1MWQwOWI3Y2E0YmQ3ZDY1IiwiY29tcGFueV9uYW1lIjoiIiwiZmlyc3RfbmFtZSI6IlRlYW0iLCJsYXN0X25hbWUiOiJtZW1iZXIiLCJhZG1pbl9lbWFpbCI6InJhdGVsaW1pdHRyaWFsQHlvcG1haWwuY29tIiwidXNlcl9pZCI6NDI2MjUzLCJyZWdfaWQiOjEwMDMwNzgsImJpbGxpbmdfcmVmX2lkIjpudWxsLCJ1c2VyX3R5cGUiOiJ0ZWFtIiwiYWNjb3VudF9zdGF0dXMiOiJhY3RpdmUiLCJyZWN1cmx5X3BheW1lbnRfc3RhdHVzIjoidHJpYWwiLCJjb3VudHJ5X2NvZGUiOjIyNCwiY291bnRyeV9uYW1lIjoiVW5pdGVkIFN0YXRlcyIsInR3b19kaWdpdF9jb3VudHJ5X2NvZGUiOiJVUyIsImN1cnJlbmN5X2NvZGUiOiJVU0QiLCJjdXJyZW5jeV9zeW1ib2wiOiIkIiwidGltZXpvbmUiOiJBbWVyaWNhL0xvc19BbmdlbGVzIiwiaXNfZWFybHlfYWNjZXNzIjoxLCJpc19wcmVfbGF1bmNoIjpmYWxzZSwiY2hhcmdlYmVlX2Vucm9sbGVkIjpmYWxzZSwiY2hhcmdlYmVlX2VuYWJsZWQiOmZhbHNlLCJjcmNfYmlsbGluZ19lbmFibGVkIjpmYWxzZSwiaWF0IjoxNzgxNzgxODY1LCJuYmYiOjE3ODE3ODE4NjUsImV4cCI6MTc4MTg2ODI2NSwicGxhbl9uYW1lIjoiU3RhcnQiLCJwdXJjaGFzZWRfbWFzdGVyY2xhc3MiOiJubyIsImlzX3NpZ25lZCI6dHJ1ZSwic2lnbnVwX3N0YXR1cyI6ImNvbXBsZXRlIn0.ucxypU-9wonxm2_MCZHAl_5r6EJ8zxcsq1bCRwy-qk90xeck6X2ZFX4z_uz-haTAdpUzrmmxITfvyVCca0-vAuBRAgQQxeJF3hB679rs4I_vb3lWaJthP3uPtRjHvY_jfroYQPPMx2itYhH4sLyOMGYymrmwTuqRRMN30be8dJL-MF6kFeqkqEICKc0jcqLI_vTxO2rtWhAZaWFuoZlYSQh9KG_jglkQJ27ZkJdz6-RQxOh3S2WIfvm6RC0gCEvicXPLZEZVmPP8m4zPnoPxfsgFT4CHVWXoh0PjVZGn-smSvzB_9G-nh5NotAob6a2YDOZo9wfL0RwDYMkcvMb84w"

BASE_URL = "https://d2z6bx74pusiw2.cloudfront.net"
PATH = "/api/clients/9/login-details"

# The OAuth host (forgot-password) uses a custom "authorizationtoken" header,
# NOT the CloudFront Bearer token. This is a browser session token and expires —
# refresh it from DevTools if forgot-password starts returning 401.
FORGOT_PASSWORD_URL = "https://qa-oauth.creditrepaircloud.com/api/forgot-password"
AUTHORIZATION_TOKEN = (
    "170aba3364f9355436f4b6e8c376aa43dc0ff588:"
    "ec2289abb60785466800c85068eaa75d85cd11a771b7c93a9607a0daca4f9fa9"
)

# CSV files used by the import tests.
CSV_FILE = Path(__file__).resolve().parents[2] / "test_data" / "api" / "clients_import.csv"
AFFILIATES_CSV_FILE = Path(__file__).resolve().parents[2] / "test_data" / "api" / "affiliates_import.csv"

# Number of times each endpoint is called in its loop.
n_times = 1
import_n_times = 2



@pytest.fixture(scope="session")
def authed_api(playwright: Playwright):
    context = playwright.request.new_context(
        base_url=BASE_URL,
        extra_http_headers={"Authorization": f"Bearer {BEARER_TOKEN}"},
    )
    yield context
    context.dispose()


@pytest.fixture(scope="session")
def team_member_api(playwright: Playwright):
    context = playwright.request.new_context(
        base_url=BASE_URL,
        extra_http_headers={"Authorization": f"Bearer {TEAM_MEMBER_TOKEN}"},
    )
    yield context
    context.dispose()


def test_call_login_details_n_times(authed_api):
    for i in range(1, n_times + 1):
        resp = authed_api.put(PATH, data=RESEND_LOGIN_DETAILS)
        print(f"Request {i}: status={resp.status} body={resp.text()}")
        


def test_create_client_n_times(authed_api):
    for i in range(1, n_times + 1):
        payload = build_create_client_payload()  # new last_name + email each call
        resp = authed_api.post("/api/clients", data=payload)
        print(
            f"Request {i}: last_name={payload['last_name']} email={payload['email']} "
            f"status={resp.status} body={resp.json()["message"]}"
        )


def test_login_activity_n_times(authed_api):
    for i in range(1, n_times + 1):
        resp = authed_api.post("/api/activities/login")
        print(f"Request {i}: status={resp.status} body={resp.text()}")


def test_create_affiliate_n_times(authed_api):
    for i in range(1, n_times + 1):
        payload = build_create_affiliate_payload()  # new last_name + email each call
        resp = authed_api.post("/api/affiliates", data=payload)
        print(
            f"Request {i}: last_name={payload['last_name']} email={payload['email']} "
            f"status={resp.status} body={resp.json()["message"]}"
        )


def test_update_affiliate_n_times(authed_api):
    for i in range(1, n_times + 1):
        payload = build_update_affiliate_payload()  # new last_name + phone each call
        resp = authed_api.put("/api/affiliates/3", data=payload)
        print(
            f"Request {i}: last_name={payload['last_name']} phone={payload['phone']} "
            f"status={resp.status} body={resp.text()}"
        )




def test_validate_access_n_times(team_member_api):
    # No payload; uses the team-member token via its own context.
    for i in range(1, n_times + 1):
        resp = team_member_api.post("/api/users/validate-access")
        print(f"Request {i}: status={resp.status} body={resp.text()}")


def test_import_clients_csv_n_times(authed_api):
    # Uploads the clients CSV as multipart/form-data ("file" field) each call.
    for i in range(1, import_n_times + 1):
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
    for i in range(1, import_n_times + 1):
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
    # OAuth host uses a custom "authorizationtoken" header, not Bearer, so it
    # needs its own request context (not the CloudFront authed_api fixture).
    context = playwright.request.new_context(
        extra_http_headers={
            "authorizationtoken": AUTHORIZATION_TOKEN,
            "content-type": "application/json",
            "origin": "https://qa.creditrepaircloud.com",
            "referer": "https://qa.creditrepaircloud.com/",
        },
    )
    for i in range(1, n_times + 1):
        resp = context.post(FORGOT_PASSWORD_URL, data=FORGOT_PASSWORD)
        print(f"Request {i}: status={resp.status} body={resp.text()}")
    context.dispose()