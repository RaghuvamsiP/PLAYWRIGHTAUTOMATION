import time
from datetime import datetime

import pytest
from faker import Faker
from playwright.sync_api import Playwright

fake = Faker()
BASE_URL = "https://d2z6bx74pusiw2.cloudfront.net"
DELETE_BASE_URL = "https://d2z6bx74pusiw2.cloudfront.net"
CLIENT_COUNT = 3  # change this to create more clients in test_create_n_clients

BEARER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6ImNiMGQzYTk5M2I2ZWJkZDVhMTllOTBjZDUwZDI4NjE3YzY5YzJjMDgyZTc3YTJmZWE3MzRmYmI0NzNiYWFkNDE1NTRiZTBiZmVhOGVmM2RkIiwiY29tcGFueV9uYW1lIjoiQ3JlZGl0IFJlcGFpciBCdXNpbmVzcyIsImZpcnN0X25hbWUiOiJBdHRhY2ggUGRmIiwibGFzdF9uYW1lIjoiVGVzdGluZyIsImFkbWluX2VtYWlsIjoicGRmQHlvcG1haWwuY29tIiwidXNlcl9pZCI6NDIzNjk2LCJyZWdfaWQiOjEwMDI3MTMsImJpbGxpbmdfcmVmX2lkIjoiM2Y3ZDBkZGYtZjA1Ny00OTZiLWI0OWMtZjAxZTA1ZGU5ODcyIiwidXNlcl90eXBlIjoiYWRtaW4iLCJhY2NvdW50X3N0YXR1cyI6ImFjdGl2ZSIsInJlY3VybHlfcGF5bWVudF9zdGF0dXMiOiJwYWlkIiwiY291bnRyeV9jb2RlIjoyMjQsImNvdW50cnlfbmFtZSI6IlVuaXRlZCBTdGF0ZXMiLCJ0d29fZGlnaXRfY291bnRyeV9jb2RlIjoiVVMiLCJjdXJyZW5jeV9jb2RlIjoiVVNEIiwiY3VycmVuY3lfc3ltYm9sIjoiJCIsInRpbWV6b25lIjoiQW1lcmljYS9Mb3NfQW5nZWxlcyIsImlzX2Vhcmx5X2FjY2VzcyI6MSwiaXNfcHJlX2xhdW5jaCI6ZmFsc2UsImNoYXJnZWJlZV9lbnJvbGxlZCI6ZmFsc2UsImNoYXJnZWJlZV9lbmFibGVkIjpmYWxzZSwiY3JjX2JpbGxpbmdfZW5hYmxlZCI6dHJ1ZSwiaWF0IjoxNzgyMTg5MjkyLCJuYmYiOjE3ODIxODkyOTIsImV4cCI6MTc4MjI3NTY5MiwicGxhbl9uYW1lIjoiU3RhcnQiLCJwdXJjaGFzZWRfbWFzdGVyY2xhc3MiOiJubyIsImlzX3NpZ25lZCI6dHJ1ZSwic2lnbnVwX3N0YXR1cyI6ImNvbXBsZXRlIn0.BI-Ds4DiXqtY4YgrCDcSOHs1xpISZ1ALkJenE85j_GNtZAQhWqFrKWxKpBnoBS9USSPeXfSa0j3V4tD9OxHlgGFdCqepByEHRnTN94V6LNH6bPGbnWazq6jQdPam-R3F-KC1u5_tm_mQKKmjprMY7EIc9-fEj89a6xfgqgHEdldehZJgvdEOx77dAC12wrUxN4C_Uy67qlbpHEz6NjpDAejI7pm0xn2q8feAyqGJE6nopJ42_dmZoMrYehLXx7DlxQYQohUwJpqSyjvzPiI767eoyvuT9n1o-oi9p_pOGzf0EL2QDb784d7ATA26Rm4zwkfx1omglsBfXSyHqgEAWQ"

@pytest.fixture(scope="session")
def authed_api(playwright: Playwright):
    """Playwright APIRequestContext with the bearer token in headers."""
    context = playwright.request.new_context(
        extra_http_headers={"Authorization": f"Bearer {BEARER_TOKEN}"},
    )
    yield context
    context.dispose()


def _build_payload(index, run_id):
    """Build a unique client payload with Faker-generated names. run_id keeps email unique across runs."""
    first_name = f"SSN {fake.first_name()}"
    last_name = fake.last_name()
    email = f"{first_name}.{last_name}".lower().replace(" ", "") + f".{run_id}{index}@yopmail.com"
    start_date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "client_status": "1",
        "start_date": start_date,
        "assigned_to": [1],
        "portal_access": "on",
        "agreement": "no",
        "portal_language": "en",
        "has_email": "0",
        "sendlogininfo": True,
    }


def test_create_n_clients(authed_api):
    """Create n clients via the CRC clients API and print client ids from the response."""
    run_id = int(time.time())
    created_ids = []
    failures = []

    for i in range(1, CLIENT_COUNT + 1):
        payload = _build_payload(i, run_id)
        response = authed_api.post(f"{BASE_URL}/api/clients", data=payload)

        if response.status in (200, 201):
            client_id = response.json()["details"]["id"]
            created_ids.append(client_id)
            print(f"[{i}/{CLIENT_COUNT}] {payload['first_name']} {payload['last_name']} "
                  f"({payload['email']}) -> client_id={client_id}")
        else:
            failures.append((payload["email"], response.status, response.text()))
            print(f"[{i}/{CLIENT_COUNT}] FAILED: email={payload['email']}  "
                  f"status={response.status}  body={response.text()[:200]}")

    print("\n=== Client IDs ===")
    for cid in created_ids:
        print(cid)

    assert not failures, f"{len(failures)} client(s) failed to create: {failures}"
    assert len(created_ids) == CLIENT_COUNT


def test_delete_clients(authed_api):
    """Delete clients with ids 100..200 (inclusive). 2xx and 404 are both acceptable."""
    deleted = []
    not_found = []
    failures = []

    for client_id in range(100, 201):
        url = f"{DELETE_BASE_URL}/api/clients/{client_id}"
        response = authed_api.delete(url)

        if 200 <= response.status < 300:
            deleted.append(client_id)
            print(f"Deleted client_id={client_id}  status={response.status}")
        elif response.status == 404:
            not_found.append(client_id)
            print(f"Not found  client_id={client_id}")
        else:
            failures.append((client_id, response.status, response.text()[:200]))
            print(f"FAILED client_id={client_id}  status={response.status}  "
                  f"body={response.text()[:200]}")

    print(f"\nSummary: deleted={len(deleted)}  not_found={len(not_found)}  failed={len(failures)}")
    print(f"Deleted ids: {deleted}")

    assert not failures, f"{len(failures)} delete(s) failed: {failures}"
