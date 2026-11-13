
import pytest
from playwright.sync_api import Playwright

from crc_automation.api.payloads.login_details import RESEND_LOGIN_DETAILS
from crc_automation.api.payloads.create_client import build_create_client_payload
from crc_automation.api.payloads.create_affiliate import build_create_affiliate_payload
from crc_automation.api.payloads.update_affiliate import build_update_affiliate_payload
from crc_automation.api.payloads.forgot_password import FORGOT_PASSWORD
from crc_automation.api.payloads.login import LOGIN

from crc_automation.config.settings import API_TEST_DATA_DIR

BEARER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6IjRmYzEzZjk2MzExNzkzN2RlZjlmMjE3MDFiMWRjOTZjNDgxZmUwZGIxMTAyN2NlMGJjMTVjODI5ZjY5Yzk3NDRkOGQxMmY4YmIzMGQyNTZkIiwiY29tcGFueV9uYW1lIjoiIiwiZmlyc3RfbmFtZSI6IlN1cHBvcnQiLCJsYXN0X25hbWUiOiJzeXN0ZW0iLCJhZG1pbl9lbWFpbCI6ImNyY3N1cHBvcnRzeXN0ZW1AdGVzdG1haWwuY3JlZGl0cmVwYWlyY2xvdWQuY29tIiwidXNlcl9pZCI6ODU1MjQ2NSwicmVnX2lkIjoyMzQ0OTcsImJpbGxpbmdfcmVmX2lkIjoiMjhiYTMxZTktMTQ3ZC00ZTk1LWE4N2QtZWNkYzhmNjY2NDIwIiwidXNlcl90eXBlIjoiYWRtaW4iLCJhY2NvdW50X3N0YXR1cyI6ImFjdGl2ZSIsInJlY3VybHlfcGF5bWVudF9zdGF0dXMiOiJwYWlkIiwiY291bnRyeV9jb2RlIjoyMjQsImNvdW50cnlfbmFtZSI6IlVuaXRlZCBTdGF0ZXMiLCJ0d29fZGlnaXRfY291bnRyeV9jb2RlIjoiVVMiLCJjdXJyZW5jeV9jb2RlIjoiVVNEIiwiY3VycmVuY3lfc3ltYm9sIjoiJCIsInRpbWV6b25lIjoiQW1lcmljYS9Mb3NfQW5nZWxlcyIsImlzX2Vhcmx5X2FjY2VzcyI6MSwiaXNfcHJlX2xhdW5jaCI6ZmFsc2UsImNoYXJnZWJlZV9lbnJvbGxlZCI6ZmFsc2UsImNoYXJnZWJlZV9lbmFibGVkIjpmYWxzZSwiY3JjX2JpbGxpbmdfZW5hYmxlZCI6dHJ1ZSwiaWF0IjoxNzg2OTM3NDY4LCJuYmYiOjE3ODY5Mzc0NjgsImV4cCI6MTc4NzAyMzg2OCwic2lnbnVwX3N0YXR1cyI6ImNvbXBsZXRlIiwicGxhbl9uYW1lIjoiU3RhcnQiLCJwdXJjaGFzZWRfbWFzdGVyY2xhc3MiOiJ5ZXMiLCJpc19zaWduZWQiOnRydWV9.SNRJvMTZA-UEmGiQ_GtOzsI5xBlhXY1HqlnIYREd6J5DydzV_yj0l5RerDmJ9Xzi94x60Rmbgla8OnFsLvNCDYWyG-TaDH1Z9Y3uyeaz2ofC5ZHQgRJaA6gY4gkWibxuU7vc1mk8bz6r5HBddQHo6Lov-w-K6zANFcHW05WecEsSWFaVu49JeWlYvakfwwi3GiSAArG2WnKuFSOoOi-9n9TGbu8NYhoDAFZTOWUF9uDMgDizhmvhHofkAZ3d4k-pJOdsHce14skJdl4RucSExjGxAWSEyxzLycWw2BfLpi1Sq6KgqzBsb0mbilQrlSmk4QJciqCv6BJbIhWVMRyHer5vkENCh4WQ0MfOz5Ep_PS9onhXuDsnfUEGAGqRXnbwothyHHV7cbO01BqCelC2LhnZXBwpCpPuyLQ3N7gUU7QFFt__efU6vu5QVW4ApFxylesmZpcfKqO7W2Lc4MvnHA9CqjWJRaAoFvzwi-hNXuhfaAmcx9Xs-ljINlX4R1Z_uute9xP2sw8FoqeMsSflsaRBldRHVWaIrApPqt_JiancSI7kiRI8BLq6zdvjWS_C7Fi1m_NMt9RPMN1c4MOva3FbINlcWEt5-6DwNqm4aC5ek7s4WnqyiwybZ4BANrxprfv8FfHaNR7-1K6hd3QHRm6GDjLZlmB_Y6z0h8A5_VY"
TEAM_MEMBER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6IjQyNGI5YWY5OWI0MDk1YzM1N2I2MGU3OTViODA3YzViYWE3M2FiMjZlNjcwYzM2NGZhYmI3ZWU1ZDlkNDJiYTJjZmI5MjFmNzRmZGVmNWQ3IiwiY29tcGFueV9uYW1lIjoiIiwiZmlyc3RfbmFtZSI6IlVEIiwibGFzdF9uYW1lIjoiVE0iLCJhZG1pbl9lbWFpbCI6InVkYXlyZWRkeWN3QHRlc3RtYWlsLmNyZWRpdHJlcGFpcmNsb3VkLmNvbSIsInVzZXJfaWQiOjg1NjU5NDcsInJlZ19pZCI6MjMzODA0LCJiaWxsaW5nX3JlZl9pZCI6bnVsbCwidXNlcl90eXBlIjoidGVhbSIsImFjY291bnRfc3RhdHVzIjoiYWN0aXZlIiwicmVjdXJseV9wYXltZW50X3N0YXR1cyI6InBhaWQiLCJjb3VudHJ5X2NvZGUiOjIyNCwiY291bnRyeV9uYW1lIjoiVW5pdGVkIFN0YXRlcyIsInR3b19kaWdpdF9jb3VudHJ5X2NvZGUiOiJVUyIsImN1cnJlbmN5X2NvZGUiOiJVU0QiLCJjdXJyZW5jeV9zeW1ib2wiOiIkIiwidGltZXpvbmUiOiJBbWVyaWNhL0xvc19BbmdlbGVzIiwiaXNfZWFybHlfYWNjZXNzIjoxLCJpc19wcmVfbGF1bmNoIjpmYWxzZSwiY2hhcmdlYmVlX2Vucm9sbGVkIjpmYWxzZSwiY2hhcmdlYmVlX2VuYWJsZWQiOmZhbHNlLCJjcmNfYmlsbGluZ19lbmFibGVkIjpmYWxzZSwiaWF0IjoxNzg2NzAxNTMwLCJuYmYiOjE3ODY3MDE1MzAsImV4cCI6MTc4Njc4NzkzMCwic2lnbnVwX3N0YXR1cyI6ImNvbXBsZXRlIiwicGxhbl9uYW1lIjoiU3RhcnQiLCJwdXJjaGFzZWRfbWFzdGVyY2xhc3MiOiJ5ZXMiLCJpc19zaWduZWQiOnRydWV9.d23Z5dmZyY60IYUNF6fT8TAk6rnWFZ8qXX9RS-CmUJBAZ55RqnqrtI3E6XRbLUFVwdioETsFugBmCWJHFDrVSvgTy1gJSDXsu5QuDIfDnHZ-mfWevyNOpvbQkxSPj3mXJZiTATiyD-LJ2YL5ixWLg5SQ4o9ejDiCXsuO3FOzT50cKlSv6LOAMQgDFHtwRULUb_qlXEG0iBNOAMml0aFRTBhIWuvR6zukUba5nkJqEYIvuYUklzFkO7yMv2I4OP_tcZ8UGLWOA_YWmt5v-WvBQ1uEKNVahvMBTMpAQxYpgxjxzIN3BfpAMC4UUP6T-a3YhaHSNHHENq6BXM9KhNXlFhavQ72NZ7mVTZrBaoRkbcUb-I2R61YtulZS0o-8wq0jGJsuFnINXft2O91oqtvt3PGzwnWjz74Lbj_jmFPfbUIXB-AJ71cATdFpZKCdsztR44HrqulAcpfdMVHNn752-SAPWTtvMKbDCmBl-BR7wUgRv_l1hjCREm8bz0ZZAnlRDwcQP3Ty4R0lJeOixnrJYCcbYq4r_ioWi7OzcM7o7CpkonFnAkKiLdmFygs_VEDawFIxdoHalkwPYAawS1t4lBmpSOhAzw3U9tV1_9ngU1l3TL1adrPpK7YywPx64JpMwM0eeJbfrmsdwQfIHnozqirri4VqNIfLY2C1ajR8aZo"
BASE_URL = "https://api.creditrepaircloud.com"
PATH = "/api/clients/4/login-details"

# The OAuth host (forgot-password) uses a custom "authorizationtoken" header,
# NOT the CloudFront Bearer token. This is a browser session token and expires —
# refresh it from DevTools if forgot-password starts returning 401.
OAUTH_BASE_URL = "https://oauth.creditrepaircloud.com"
FORGOT_PASSWORD_PATH = "/api/forgot-password"

# Auth-migration host, used only by the login test.
AUTH_MIGRATION_BASE_URL = "https://prod-auth-migration.creditrepaircloud.com"
LOGIN_PATH = "/api/v1/login"
AUTHORIZATION_TOKEN = "ac6883a30ac991ebb28c917d0613e08c5ed4049d:569d2b722abe8786125440ca653c712fa06be617afbccdfc3fa08d84095ba858"

# CSV files used by the import tests.
CSV_FILE = API_TEST_DATA_DIR / "clients_import.csv"
AFFILIATES_CSV_FILE = API_TEST_DATA_DIR / "affiliates_import.csv"

# Number of times each endpoint is called in its loop.
n_times = 100
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