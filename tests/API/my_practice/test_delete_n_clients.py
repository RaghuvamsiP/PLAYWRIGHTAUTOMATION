"""
DELETE /api/clients/{client_id} — delete every client id in a given range.

Set FROM_CLIENT_ID / TO_CLIENT_ID below; the test deletes each id in that
inclusive range and prints the response for each call.
Uses a Playwright APIRequestContext with a static bearer token.
"""

import pytest
from playwright.sync_api import Playwright

BASE_URL = "https://qa-api.creditrepaircloud.com"

# Bearer token expires — refresh it from DevTools if you start getting 401s.
BEARER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6IjU5NzlkMmE0NjgwMDMxZDgyZTlmNDlhNWQzNGNhNTA1MTAxYzMzNjQyZWIxNjQ4MWMwOTMyYTdiNzA0ODJjMGFmOWFhZmE3MGU4YjQ0MTcxIiwiY29tcGFueV9uYW1lIjoiIiwiZmlyc3RfbmFtZSI6InVkYXkiLCJsYXN0X25hbWUiOiJOZXdVUkwiLCJhZG1pbl9lbWFpbCI6InVkYXluZXd1cmxAeW9wbWFpbC5jb20iLCJ1c2VyX2lkIjo0Mjc4NjYsInJlZ19pZCI6MTAwMzIxNywiYmlsbGluZ19yZWZfaWQiOm51bGwsInVzZXJfdHlwZSI6ImFkbWluIiwiYWNjb3VudF9zdGF0dXMiOiJhY3RpdmUiLCJyZWN1cmx5X3BheW1lbnRfc3RhdHVzIjoicGFpZCIsImNvdW50cnlfY29kZSI6MjI0LCJjb3VudHJ5X25hbWUiOiJVbml0ZWQgU3RhdGVzIiwidHdvX2RpZ2l0X2NvdW50cnlfY29kZSI6IlVTIiwiY3VycmVuY3lfY29kZSI6IlVTRCIsImN1cnJlbmN5X3N5bWJvbCI6IiQiLCJ0aW1lem9uZSI6IkFtZXJpY2EvTG9zX0FuZ2VsZXMiLCJpc19lYXJseV9hY2Nlc3MiOjEsImlzX3ByZV9sYXVuY2giOmZhbHNlLCJjaGFyZ2ViZWVfZW5yb2xsZWQiOmZhbHNlLCJjaGFyZ2ViZWVfZW5hYmxlZCI6ZmFsc2UsImNyY19iaWxsaW5nX2VuYWJsZWQiOmZhbHNlLCJpYXQiOjE3ODU4Mzc5MjIsIm5iZiI6MTc4NTgzNzkyMiwiZXhwIjoxNzg1OTI0MzIyLCJwbGFuX25hbWUiOiJTdGFydCIsInB1cmNoYXNlZF9tYXN0ZXJjbGFzcyI6Im5vIiwiaXNfc2lnbmVkIjp0cnVlLCJzaWdudXBfc3RhdHVzIjoiY29tcGxldGUifQ.YDfEWyy1ket5A9ILNjeXr6pOmRrU53L91EeFi-dL0-9RTff9rIr8JayGeYO0TPUN-w6rLrutZT2Hl7PP3rHyhorlL5pjWcACCdG6IioD6B7AnvJ_KrbiGauYceewGELN4oJ8QeEzr35ocD1bypIgvl5RwbAQrn_k9V-NKhqyNgNMrRa0ws7sh_iN9ykM7CGcfl7UaXhTCPT3yh8ktZZEL8z9XLFjNzgXupJQyl4uf6DSu_teLOVkpsZTRxezCxnG4LLWIJb1IWKV0gMpwbAUvpLhfV2M3h-s4y_EiPe8OkkcqnJbO1xIPtXSP4BBckFCcBkpAQPeYnlDFC5pbvI0_w"

# Inclusive range of client ids to delete. Edit these two values.
FROM_CLIENT_ID = 3
TO_CLIENT_ID = 15


@pytest.fixture(scope="session")
def authed_api(playwright: Playwright):
    context = playwright.request.new_context(
        base_url=BASE_URL,
        extra_http_headers={"Authorization": f"Bearer {BEARER_TOKEN}"},
    )
    yield context
    context.dispose()


def test_delete_n_clients(authed_api):
    for client_id in range(FROM_CLIENT_ID, TO_CLIENT_ID + 1):
        resp = authed_api.delete(f"/api/clients/{client_id}")
        print(f"Delete client_id={client_id}: status={resp.status} body={resp.text()}")
