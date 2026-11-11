
import pytest
from pathlib import Path
from playwright.sync_api import Playwright

from tests.API.payloads.login_details import RESEND_LOGIN_DETAILS
from tests.API.payloads.create_client import build_create_client_payload
from tests.API.payloads.create_affiliate import build_create_affiliate_payload
from tests.API.payloads.update_affiliate import build_update_affiliate_payload
from tests.API.payloads.forgot_password import FORGOT_PASSWORD
from tests.API.payloads.login import LOGIN

BEARER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6IjAzNzA0MzJhOGM3OWRjY2ZmYTZlOTcwNWEwNDZmODdhY2U4NmJhM2JhZmI1ODRiOWY3NDFiNGEzMzgyNmZhNDhhNzgxNGRlM2E4YmZjOWJlIiwiY29tcGFueV9uYW1lIjoiIiwiZmlyc3RfbmFtZSI6IlVkYXkiLCJsYXN0X25hbWUiOiJSZWRkeSIsImFkbWluX2VtYWlsIjoidWRheXJlZGR5Y3dAdGVzdG1haWwuY3JlZGl0cmVwYWlyY2xvdWQuY29tIiwidXNlcl9pZCI6ODUzNzA4MCwicmVnX2lkIjoyMzM4MDQsImJpbGxpbmdfcmVmX2lkIjpudWxsLCJ1c2VyX3R5cGUiOiJhZG1pbiIsImFjY291bnRfc3RhdHVzIjoiYWN0aXZlIiwicmVjdXJseV9wYXltZW50X3N0YXR1cyI6InBhaWQiLCJjb3VudHJ5X2NvZGUiOjIyNCwiY291bnRyeV9uYW1lIjoiVW5pdGVkIFN0YXRlcyIsInR3b19kaWdpdF9jb3VudHJ5X2NvZGUiOiJVUyIsImN1cnJlbmN5X2NvZGUiOiJVU0QiLCJjdXJyZW5jeV9zeW1ib2wiOiIkIiwidGltZXpvbmUiOiJBbWVyaWNhL0xvc19BbmdlbGVzIiwiaXNfZWFybHlfYWNjZXNzIjoxLCJpc19wcmVfbGF1bmNoIjpmYWxzZSwiY2hhcmdlYmVlX2Vucm9sbGVkIjpmYWxzZSwiY2hhcmdlYmVlX2VuYWJsZWQiOmZhbHNlLCJjcmNfYmlsbGluZ19lbmFibGVkIjpmYWxzZSwiaWF0IjoxNzg2NzAxMjc1LCJuYmYiOjE3ODY3MDEyNzUsImV4cCI6MTc4Njc4NzY3NSwic2lnbnVwX3N0YXR1cyI6ImNvbXBsZXRlIiwicGxhbl9uYW1lIjoiU3RhcnQiLCJwdXJjaGFzZWRfbWFzdGVyY2xhc3MiOiJ5ZXMiLCJpc19zaWduZWQiOnRydWV9.jfkAzDa8bPioFTFQupO9cp4vzsgUKv_XYUqX1mxVbvbENwxlbninZ_WjNrthdF1rpcfNJmQ74WnbKspwBA8Emh6kLlKHJzAVnuRoVJPZ_CK0L6oyLovsFGsAOp2Yca10_dCqwhkDHcoYnU-p-EidCofa2UKDZG-xRaQNwu0EmcPQVNtur-6YB4goJTC-KDmqbBv7P8fnIlEQBPX9lzyQvj3StjyLbkN2QHndP4Fd-5r5V73QHQK2rX_uJKQ3EkHQW2Xi3RfKnMR_RKEFL_OTmsYtlgGFNoKpe5MKwM3zPWlZPJhgZlXFx3JS56HLgErVow0N7Qa-B1_jFr31fM2OHHzZSRIn8381yzhWGEKKJxXuIEFgO4cvY7LIiRLrdidt8_zTAqWNij_gNs6xI4uZHJ12wPET5wP7hEGE0DPBC8M1Rm78S3tZp2CHhbY4W8HDiA6R6dCXfu2SepUPMbp8cFQxzIB5WwMlc1iL3SUIMghY5EYpyxA12sO2GkqhtVIALsZCvJnOsplNMnmOEyS36_grP7n5qtuiyEsVxvg_iULmDm-P5UakVeb7Bm9Qj643WFIGHWs2JnhV0NszXXa-VWsez9GmyfbHcjiz1qR64FB_JlDeFO-xOBd7D30cwJn_z7-7J0SsAnFjGikBqIc3EGU1rOnSjlIo272zOR9C9Vc"
TEAM_MEMBER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6IjJlYTIyMjQ0ZWI3MGNiZTdmZmQzOTU0MzFlNWRhNjgxMDE3NGQ2ZWFiZjU5OTY3MTEwYzMyMjNjM2U3YjM0YzEwNjBhYTk0ODJmZmJhNTIyIiwiY29tcGFueV9uYW1lIjoiTWFzdGVyIFBpZWNlIiwiZmlyc3RfbmFtZSI6ImhpbWFuIiwibGFzdF9uYW1lIjoia2luIiwiYWRtaW5fZW1haWwiOiJTU0NTX1ZQQFlPUE1BSUwuQ09NIiwidXNlcl9pZCI6NDE0NTM1LCJyZWdfaWQiOjEwMDEyNTIsImJpbGxpbmdfcmVmX2lkIjoiYTczNzc1NTAtOWE4ZC00YWUwLThlNDEtMzQ3OGY3MDg3ODRkIiwidXNlcl90eXBlIjoidGVhbSIsImFjY291bnRfc3RhdHVzIjoiYWN0aXZlIiwicmVjdXJseV9wYXltZW50X3N0YXR1cyI6InBhaWQiLCJjb3VudHJ5X2NvZGUiOjIyNCwiY291bnRyeV9uYW1lIjoiVW5pdGVkIFN0YXRlcyIsInR3b19kaWdpdF9jb3VudHJ5X2NvZGUiOiJVUyIsImN1cnJlbmN5X2NvZGUiOiJVU0QiLCJjdXJyZW5jeV9zeW1ib2wiOiIkIiwidGltZXpvbmUiOiJBbWVyaWNhL0xvc19BbmdlbGVzIiwiaXNfZWFybHlfYWNjZXNzIjoxLCJpc19wcmVfbGF1bmNoIjpmYWxzZSwiY2hhcmdlYmVlX2Vucm9sbGVkIjpmYWxzZSwiY2hhcmdlYmVlX2VuYWJsZWQiOmZhbHNlLCJjcmNfYmlsbGluZ19lbmFibGVkIjp0cnVlLCJpYXQiOjE3ODYwMDgwNTcsIm5iZiI6MTc4NjAwODA1NywiZXhwIjoxNzg2MDk0NDU3LCJzaWdudXBfc3RhdHVzIjoiY29tcGxldGUiLCJwbGFuX25hbWUiOiJTdGFydCIsInB1cmNoYXNlZF9tYXN0ZXJjbGFzcyI6Im5vIiwiaXNfc2lnbmVkIjp0cnVlfQ.myUVvT0Ktr2I1Oc9j_1W-ssDSyXh4TvJBjKuteHjvXY88HTFtvAfw2YMLuLZq4R5oY0p8ClWk09I743mwrt8M5TKHHwXpGhzDjCPUP6TG5oFNlTmcBdsHITxGIloxCNK-4yWbREa4EPWPOyP1TdiA-4zB8YPHXqVQlqqKpsW7CH4vieXiJKnhItJ_K6u7xJ4lN-4lJjC9AA_QTqaO_49b0ZOj_rtSWxmgryC9L7Z8staedF44DdBBg4JHFc50A-Yvs9hm5j2bpc9Jx5NkaMYJZdNrAhjI_slF4fXDKIc97VjjABpeOoRL3pISGwPKCyO9rcH91rH0a3xGcmV2_v4eQxA9MuXzvJmFruAnQsSJ-PdnQVPEYQTA6FzDUGNTPnKiljhccNXr3mXENn2eAPufKA_ILN9HcGmE8681FpZM96mkCLmYImrN4_fq1rL3j4WlWD2tXsxEflyXXMXoql4JRuoJ1bFoeZdtT6vGkwMFu6Wkv2f4MEzSXX7N3OgrnSYC8odzlTs2vx4tOb-9Req7k7aGmlMlvGDJnOnT3ciP8jaSJMyOOeqjsDd_AjGiPS9lGxcMVp3JUTzDnZdIuACfGD3_jUN1sTtcNUd0XSDSWJEAgalU-GO80wmNXUsefe9wq9yXh4q62BDeax5XI9IQOuN0I8uLA34BU7zEfFIqvQ"
BASE_URL = "https://stage-api.creditrepaircloud.com"
PATH = "/api/clients/5/login-details"

# The OAuth host (forgot-password) uses a custom "authorizationtoken" header,
# NOT the CloudFront Bearer token. This is a browser session token and expires —
# refresh it from DevTools if forgot-password starts returning 401.
OAUTH_BASE_URL = "https://stage-oauth.creditrepaircloud.com"
FORGOT_PASSWORD_PATH = "/api/forgot-password"

# Auth-migration host, used only by the login test.
AUTH_MIGRATION_BASE_URL = "https://stage-auth-migration.creditrepaircloud.com"
LOGIN_PATH = "/api/v1/login"
AUTHORIZATION_TOKEN = "1046bd2b3a207e4b751b43f0dc09f1a271c3c998:c0571c72956612698f7a7a26cd0d2ccb42bd5df90bcfc5cb16abb57ad42c7f4c"

# CSV files used by the import tests.
CSV_FILE = Path(__file__).resolve().parents[2] / "test_data" / "api" / "clients_import.csv"
AFFILIATES_CSV_FILE = Path(__file__).resolve().parents[2] / "test_data" / "api" / "affiliates_import.csv"

# Number of times each endpoint is called in its loop.
n_times = 6
import_n_times = 6



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