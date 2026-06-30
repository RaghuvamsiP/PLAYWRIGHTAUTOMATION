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
from tests.API.payloads.update_affiliate_paid import build_update_affiliate_paid_payload
from tests.API.payloads.forgot_password import FORGOT_PASSWORD_PAID

BEARER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6IjgwMGEwMDRhZmEzZTUyY2FjOTZkMTc0YWJhNmRhNmUzNGJmZjA2NDJjYzhlMzJiZGQ2YzI1ZGVkYTMxY2ZmYWMyM2I1ZjZiNzliYjEzMGIzIiwiY29tcGFueV9uYW1lIjoiIiwiZmlyc3RfbmFtZSI6IlJhdGUgTGltaXQiLCJsYXN0X25hbWUiOiJQYWlkIiwiYWRtaW5fZW1haWwiOiJyYXRlbGltaXRwYWlkQHlvcG1haWwuY29tIiwidXNlcl9pZCI6NDI2MTQ3LCJyZWdfaWQiOjEwMDMwNzcsImJpbGxpbmdfcmVmX2lkIjoiODZiYTViZjUtNzU2Ny00N2YzLWJmZTgtZDlmZmM4OTlhZTNhIiwidXNlcl90eXBlIjoiYWRtaW4iLCJhY2NvdW50X3N0YXR1cyI6ImFjdGl2ZSIsInJlY3VybHlfcGF5bWVudF9zdGF0dXMiOiJwYWlkIiwiY291bnRyeV9jb2RlIjoyMjQsImNvdW50cnlfbmFtZSI6IlVuaXRlZCBTdGF0ZXMiLCJ0d29fZGlnaXRfY291bnRyeV9jb2RlIjoiVVMiLCJjdXJyZW5jeV9jb2RlIjoiVVNEIiwiY3VycmVuY3lfc3ltYm9sIjoiJCIsInRpbWV6b25lIjoiQW1lcmljYS9Mb3NfQW5nZWxlcyIsImlzX2Vhcmx5X2FjY2VzcyI6MSwiaXNfcHJlX2xhdW5jaCI6ZmFsc2UsImNoYXJnZWJlZV9lbnJvbGxlZCI6ZmFsc2UsImNoYXJnZWJlZV9lbmFibGVkIjpmYWxzZSwiY3JjX2JpbGxpbmdfZW5hYmxlZCI6dHJ1ZSwiaWF0IjoxNzgxNzU4ODk1LCJuYmYiOjE3ODE3NTg4OTUsImV4cCI6MTc4MTg0NTI5NSwicGxhbl9uYW1lIjoiR3JvdyIsInB1cmNoYXNlZF9tYXN0ZXJjbGFzcyI6Im5vIiwiaXNfc2lnbmVkIjp0cnVlLCJzaWdudXBfc3RhdHVzIjoiY29tcGxldGUifQ.x3xM3pdZdVJ_XgHaj-usHvowewIT8kO_R4L27ddY3nuV3ErqNz3kGCtQlVSf_PBntZbxwqwXfORzXuYIhv9rkcbl2vohjwHH_VrVccD-IFjCsI5NpIFKbmuv5HRz_v-void_QL7iFZW3xWVC6tu0paBrVI_ahhCPG8Z9iYWVYrfFmyzLc_R_MqyHhdzC4e6_f_1TCsxEOkFhHSdwjADV6u5FkjlXJZMgBMlpXYElrEU8ODDyuabjcjHAx1Cgh8F3FgjxvFs9H6Mw5WVbNwEMQYKVUsDUtsy7mMSt_XOmnJqjic-qjYlExWrqaca4auSAd2WMCarPy6w312ZIRAaGxw"

# Team-member token, used only by the validate-access test.
TEAM_MEMBER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6Ijk0NWQyMDIzMTQzYWNmZmFlNTAwNTI3N2FjNDgzNzUxYzRhMDk5NDg4ZjJmZjg5YWU5ZTkyYjAzN2RhMjE4MzU1MTk5MjYxZTE4MDQyMzg5IiwiY29tcGFueV9uYW1lIjoiIiwiZmlyc3RfbmFtZSI6IlJMIiwibGFzdF9uYW1lIjoiVE0iLCJhZG1pbl9lbWFpbCI6InJhdGVsaW1pdHBhaWRAeW9wbWFpbC5jb20iLCJ1c2VyX2lkIjo0MjY0ODIsInJlZ19pZCI6MTAwMzA3NywiYmlsbGluZ19yZWZfaWQiOiI4NmJhNWJmNS03NTY3LTQ3ZjMtYmZlOC1kOWZmYzg5OWFlM2EiLCJ1c2VyX3R5cGUiOiJ0ZWFtIiwiYWNjb3VudF9zdGF0dXMiOiJhY3RpdmUiLCJyZWN1cmx5X3BheW1lbnRfc3RhdHVzIjoicGFpZCIsImNvdW50cnlfY29kZSI6MjI0LCJjb3VudHJ5X25hbWUiOiJVbml0ZWQgU3RhdGVzIiwidHdvX2RpZ2l0X2NvdW50cnlfY29kZSI6IlVTIiwiY3VycmVuY3lfY29kZSI6IlVTRCIsImN1cnJlbmN5X3N5bWJvbCI6IiQiLCJ0aW1lem9uZSI6IkFtZXJpY2EvTG9zX0FuZ2VsZXMiLCJpc19lYXJseV9hY2Nlc3MiOjEsImlzX3ByZV9sYXVuY2giOmZhbHNlLCJjaGFyZ2ViZWVfZW5yb2xsZWQiOmZhbHNlLCJjaGFyZ2ViZWVfZW5hYmxlZCI6ZmFsc2UsImNyY19iaWxsaW5nX2VuYWJsZWQiOmZhbHNlLCJpYXQiOjE3ODE3NjIwNzcsIm5iZiI6MTc4MTc2MjA3NywiZXhwIjoxNzgxODQ4NDc3LCJwbGFuX25hbWUiOiJHcm93IiwicHVyY2hhc2VkX21hc3RlcmNsYXNzIjoibm8iLCJpc19zaWduZWQiOnRydWUsInNpZ251cF9zdGF0dXMiOiJjb21wbGV0ZSJ9.bu5JX5D7xJA0i7bJM0eXg7jahEH2LZdfS4PfFs-UEtygpNeaC5x4x-fpTmSceDPRZn9_emV6gbtWEUym3Di_ZtmZxqWlMs8WzG2_zAV99LjkhmHA9H7CBn2FAUZq8tg7rGhaMImpGuZVoYrhDf8Z3xvo05i-VOS_hwSFiKCYmxC9yQ9grWTyHatW5W6iWYveC0ez38P3BVd732XMNSxgYZhrwb9JHKpZvlxHKWoFAwPatzMBUYEPIjgcoUdtL0DOQC4c7KnMijSgQZSMq3WBXFW_3gLi5UMTPyVM0TEKUwfb2vslxmoDE-fWiR0XdvETE4MAy4CyPtkBS3NHHAzQiA"

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
n_times = 200
import_n_times = 5



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
            f"Request {i}: email={payload['email']} "
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
            f"Request {i}: email={payload['email']}"
            f"status={resp.status} body={resp.json()["message"]}"
        )


def test_update_affiliate_n_times(authed_api):
    for i in range(1, n_times + 1):
        payload = build_update_affiliate_paid_payload()  # new last_name + phone each call
        resp = authed_api.put("/api/affiliates/2", data=payload)
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
        resp = context.post(FORGOT_PASSWORD_URL, data=FORGOT_PASSWORD_PAID)
        print(f"Request {i}: status={resp.status} body={resp.text()}")
    context.dispose()