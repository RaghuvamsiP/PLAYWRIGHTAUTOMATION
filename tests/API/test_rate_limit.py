

import pytest
from pathlib import Path
from playwright.sync_api import Playwright

from tests.API.payloads.login_details import RESEND_LOGIN_DETAILS
from tests.API.payloads.create_client import build_create_client_payload
from tests.API.payloads.create_affiliate import build_create_affiliate_payload
from tests.API.payloads.update_affiliate import build_update_affiliate_payload
from tests.API.payloads.forgot_password import FORGOT_PASSWORD
from tests.API.payloads.login import LOGIN

BEARER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6Ijk1ZmI2ZWFjMjQ5Y2M5M2JhY2Q0OTFhNzVjY2UwNTczNWM3YjEzYzc4OWQ0ZTVmNjc1MzJhOGNiMTc4MWNiMWNiZjk2NDU1MzYwN2NkYzZiIiwiY29tcGFueV9uYW1lIjoiIiwiZmlyc3RfbmFtZSI6IlJhdGUgTGltaXQiLCJsYXN0X25hbWUiOiJQYWlkIiwiYWRtaW5fZW1haWwiOiJyYXRlbGltaXRwYWlkQHlvcG1haWwuY29tIiwidXNlcl9pZCI6NDI2MTQ3LCJyZWdfaWQiOjEwMDMwNzcsImJpbGxpbmdfcmVmX2lkIjoiODZiYTViZjUtNzU2Ny00N2YzLWJmZTgtZDlmZmM4OTlhZTNhIiwidXNlcl90eXBlIjoiYWRtaW4iLCJhY2NvdW50X3N0YXR1cyI6ImFjdGl2ZSIsInJlY3VybHlfcGF5bWVudF9zdGF0dXMiOiJwYWlkIiwiY291bnRyeV9jb2RlIjoyMjQsImNvdW50cnlfbmFtZSI6IlVuaXRlZCBTdGF0ZXMiLCJ0d29fZGlnaXRfY291bnRyeV9jb2RlIjoiVVMiLCJjdXJyZW5jeV9jb2RlIjoiVVNEIiwiY3VycmVuY3lfc3ltYm9sIjoiJCIsInRpbWV6b25lIjoiQW1lcmljYS9Mb3NfQW5nZWxlcyIsImlzX2Vhcmx5X2FjY2VzcyI6MSwiaXNfcHJlX2xhdW5jaCI6ZmFsc2UsImNoYXJnZWJlZV9lbnJvbGxlZCI6ZmFsc2UsImNoYXJnZWJlZV9lbmFibGVkIjpmYWxzZSwiY3JjX2JpbGxpbmdfZW5hYmxlZCI6dHJ1ZSwiaWF0IjoxNzg2OTM4MzQ5LCJuYmYiOjE3ODY5MzgzNDksImV4cCI6MTc4NzAyNDc0OSwicGxhbl9uYW1lIjoiR3JvdyIsInB1cmNoYXNlZF9tYXN0ZXJjbGFzcyI6Im5vIiwiaXNfc2lnbmVkIjp0cnVlLCJzaWdudXBfc3RhdHVzIjoiY29tcGxldGUifQ.LKd7xWJkGRwAg-28_sq4_yhfApVImrOxIUWLzfdPhx5Eab8HmEc9DwB0neIWUg5RkCTVGen10fFKbsGSdtCsm9tlvkSXHNcQTfVhzFZ6-zBez3WYf6xkfdB7Sh42N1kM2drhDNfi1htPFfKLxL8UzBm9Xspvim2L7jlf_Q9zpgPgTtVCuxtfnkszZlcYOVvPVKWPU0cfa-b2XllrQ3nxp5f-3zT0s4ve_MxeB5yI4taPaXKChhf9PlWR9cJrc0riTvuGzTfUCuykcTgfDYVD3BzrDvA3LtUbvc-8jwfgp3wIZNS6MM-YoHY7lGQ5edUcgMJOt8JALZEgEC3b2DJFVw"

# Team-member token, used only by the validate-access test.
TEAM_MEMBER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6IjQ3ZTJjM2ZkN2JiYTEyMDU0NDlhOWY0MmNjOTc0MDdjZWEwY2NjNmNhZTJiMDc1NmY5NDRmZDZkMGE2ZTU4NjIzODdhM2FlNTk2OWZlM2M5IiwiY29tcGFueV9uYW1lIjoiIiwiZmlyc3RfbmFtZSI6IlJhdGUgTGltaXQiLCJsYXN0X25hbWUiOiJQYWlkIiwiYWRtaW5fZW1haWwiOiJyYXRlbGltaXRwYWlkQHlvcG1haWwuY29tIiwidXNlcl9pZCI6NDI2MTQ3LCJyZWdfaWQiOjEwMDMwNzcsImJpbGxpbmdfcmVmX2lkIjoiODZiYTViZjUtNzU2Ny00N2YzLWJmZTgtZDlmZmM4OTlhZTNhIiwidXNlcl90eXBlIjoiYWRtaW4iLCJhY2NvdW50X3N0YXR1cyI6ImFjdGl2ZSIsInJlY3VybHlfcGF5bWVudF9zdGF0dXMiOiJwYWlkIiwiY291bnRyeV9jb2RlIjoyMjQsImNvdW50cnlfbmFtZSI6IlVuaXRlZCBTdGF0ZXMiLCJ0d29fZGlnaXRfY291bnRyeV9jb2RlIjoiVVMiLCJjdXJyZW5jeV9jb2RlIjoiVVNEIiwiY3VycmVuY3lfc3ltYm9sIjoiJCIsInRpbWV6b25lIjoiQW1lcmljYS9Mb3NfQW5nZWxlcyIsImlzX2Vhcmx5X2FjY2VzcyI6MSwiaXNfcHJlX2xhdW5jaCI6ZmFsc2UsImNoYXJnZWJlZV9lbnJvbGxlZCI6ZmFsc2UsImNoYXJnZWJlZV9lbmFibGVkIjpmYWxzZSwiY3JjX2JpbGxpbmdfZW5hYmxlZCI6dHJ1ZSwiaWF0IjoxNzg2OTM4MDQ2LCJuYmYiOjE3ODY5MzgwNDYsImV4cCI6MTc4NzAyNDQ0NiwicGxhbl9uYW1lIjoiR3JvdyIsInB1cmNoYXNlZF9tYXN0ZXJjbGFzcyI6Im5vIiwiaXNfc2lnbmVkIjp0cnVlLCJzaWdudXBfc3RhdHVzIjoiY29tcGxldGUifQ.AFzquaRRheAza15fDMK5mTfTjrcjC1Al_FQvNFou3me0-c6LKTu8rVLnG-QHrlORQvSTrs_wLKmDhlePmkHvMbFdbr3Vg-q4gbiJpntI_of8_siy-tF4I5FwRuKw6N1wvApgZjMvunOk_cUOjNZSaxWDdneMbhMz70yp0fBk48tOCtul_5d7Xoq3nwXEws1_IlN683v-V0O2dAeI9Yq_v5B2t3wSbsQD4rvxgy1iiokDY4JAXyUAUKt6da7RTgUIOECOQ2eeByK0nMvU3xbu-dD9V64QoWL26IAFXSuySXXlICQIo2qka3GcSk5H1oSYMIe_W4RDBSoBtWv0wf9l8g"
BASE_URL = "https://qa-api.creditrepaircloud.com"
PATH = "/api/clients/52/login-details"

# The OAuth host (forgot-password) uses a custom "authorizationtoken" header,
# NOT the CloudFront Bearer token. This is a browser session token and expires —
# refresh it from DevTools if forgot-password starts returning 401.
OAUTH_BASE_URL = "https://qa-oauth.creditrepaircloud.com"
FORGOT_PASSWORD_PATH = "/api/forgot-password"

# Auth-migration host, used only by the login test.
AUTH_MIGRATION_BASE_URL = "https://qa-auth-migration.creditrepaircloud.com"
LOGIN_PATH = "/api/v1/login"
AUTHORIZATION_TOKEN = "170aba3364f9355436f4b6e8c376aa43dc0ff588:ec2289abb60785466800c85068eaa75d85cd11a771b7c93a9607a0daca4f9fa9"

# CSV files used by the import tests.
CSV_FILE = Path(__file__).resolve().parents[2] / "test_data" / "api" / "clients_import.csv"
AFFILIATES_CSV_FILE = Path(__file__).resolve().parents[2] / "test_data" / "api" / "affiliates_import.csv"

# Number of times each endpoint is called in its loop.
n_times = 101
import_n_times = 3



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
        try:
            body = resp.json().get("message", resp.text())
        except Exception:
            body = resp.text()  # non-JSON response — print the whole thing
        print(
            f"Request {i}: last_name={payload['last_name']} email={payload['email']} "
            f"status={resp.status} body={body}"
        )


def test_login_activity_n_times(team_member_api):
    for i in range(1, n_times + 1):
        resp = team_member_api.post("/api/activities/login")
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
        base_url=OAUTH_BASE_URL,
        extra_http_headers={
            "authorizationtoken": AUTHORIZATION_TOKEN,
            "content-type": "application/json",
            "origin": "https://qa.creditrepaircloud.com",
            "referer": "https://qa.creditrepaircloud.com/",
        },
    )
    for i in range(1, n_times + 1):
        resp = context.post(FORGOT_PASSWORD_PATH, data=FORGOT_PASSWORD)
        print(f"Request {i}: status={resp.status} body={resp.text()}")
    context.dispose()


def test_login_n_times(playwright: Playwright):
    # Auth-migration host has its own base URL and needs its own request context
    # (not the CloudFront authed_api fixture).
    context = playwright.request.new_context(
        base_url=AUTH_MIGRATION_BASE_URL,
        extra_http_headers={"content-type": "application/json"},
    )
    for i in range(1, n_times + 1):
        resp = context.post(LOGIN_PATH, data=LOGIN)
        print(f"Request {i}: status={resp.status} body={resp.text()}")
    context.dispose()