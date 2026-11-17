import asyncio
import csv
import io
import threading

import pytest
from playwright.async_api import async_playwright
from playwright.sync_api import Playwright


def _run_async(coro):
    """Run a coroutine in a dedicated thread with its own event loop.

    pytest-playwright's sync fixtures keep an event loop running on the main
    thread, so asyncio.run() can't be used directly here.
    """
    box = {}

    def runner():
        loop = asyncio.new_event_loop()
        try:
            box["result"] = loop.run_until_complete(coro)
        except BaseException as exc:  # noqa: BLE001 - re-raised on main thread
            box["error"] = exc
        finally:
            loop.close()

    thread = threading.Thread(target=runner)
    thread.start()
    thread.join()
    if "error" in box:
        raise box["error"]
    return box["result"]

BASE_URL = "https://array.io"
SERVER_TOKEN = "D34328E2-4150-4AD3-9749-EFC14BCD8BFE"
CONCURRENCY = 20  # how many alert requests to run in parallel

# Google Sheet holding the "User ID" column.
# NOTE: the sheet must be shared as "Anyone with the link -> Viewer"
# for this CSV export URL to be readable without Google auth.
SHEET_ID = "1z0sSmCiWagPH9zuFYOmxkdpgelafqEDb95f0hAY7DWs"
SHEET_GID = "0"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={SHEET_GID}"
USER_ID_OFFSET = 0  # how many User IDs to skip from the top of the sheet
USER_ID_LIMIT = None  # how many User IDs to read after the offset; None = all


@pytest.fixture(scope="session")
def alerts_api(playwright: Playwright):
    """Playwright APIRequestContext with the array.io server token in headers."""
    context = playwright.request.new_context(
        base_url=BASE_URL,
        extra_http_headers={
            "Accept": "application/json",
            "x-array-server-token": SERVER_TOKEN,
        },
    )
    yield context
    context.dispose()


@pytest.fixture(scope="session")
def user_ids(playwright: Playwright):
    """Read the 'User ID' column from the Google Sheet (first USER_ID_LIMIT rows)."""
    context = playwright.request.new_context()
    response = context.get(SHEET_CSV_URL)
    assert response.ok, (
        f"Could not read the Google Sheet (status {response.status}). "
        "Make sure it is shared as 'Anyone with the link -> Viewer'."
    )
    body = response.text()
    context.dispose()

    # Read the first column as the User ID. Works whether or not the sheet has
    # a header row (a "User ID" header, if present, is skipped). This is robust
    # to the header being dropped or having stray whitespace.
    reader = csv.reader(io.StringIO(body))
    all_ids = []
    for row in reader:
        if not row:
            continue
        value = row[0].strip()
        if not value or value.lower() == "user id":
            continue
        all_ids.append(value)

    end = None if USER_ID_LIMIT is None else USER_ID_OFFSET + USER_ID_LIMIT
    ids = all_ids[USER_ID_OFFSET:end]

    assert ids, "No User IDs found in the sheet for the requested offset/limit"
    print(f"Loaded {len(ids)} User IDs from the sheet (rows {USER_ID_OFFSET + 1}-{USER_ID_OFFSET + len(ids)})")
    return ids


def test_fetch_alert_details(alerts_api):
    """Fetch alert details for a specific alert ID"""
    alertId = 101630149
    params = {
        "bureau": "idp",
        "userId": "57875566-667427",
    }

    response = alerts_api.get(f"/api/alerts/v2/{alertId}", params=params)
    assert response.ok, f"Failed with status {response.status}: {response.text()}"

    data = response.json()
    print(f"Alert Details: {data}")


def test_fetch_all_alerts(alerts_api):
    """Fetch all alerts for a user"""
    params = {
        "userId": "68685600-004051",
        "offset": 0,
        "count": 100,
        "bureau": "idp",
    }

    response = alerts_api.get("/api/alerts/v2", params=params)
    assert response.ok, f"Failed with status {response.status}: {response.text()}"

    data = response.json()
    print(data)
    alerts = data.get("userAlerts", [])
    print(f"Total alerts: {len(alerts)}")
    for alert in alerts:
        alert_id = alert.get("id")
        source = alert.get("properties", {}).get("source", "N/A")
        print(f"Alert ID: {alert_id}, Source: {source}")


async def _find_all_coa(user_ids):
    """Scan every user in parallel batches; return all (user_id, alert_id) with class == 'COA'."""
    async with async_playwright() as p:
        context = await p.request.new_context(
            base_url=BASE_URL,
            extra_http_headers={
                "Accept": "application/json",
                "x-array-server-token": SERVER_TOKEN,
            },
        )

        async def check(user_id):
            params = {"userId": user_id, "offset": 0, "count": 100, "bureau": "idp"}
            response = await context.get("/api/alerts/v2", params=params)
            if not response.ok:
                print(f"userId={user_id} -> request failed status={response.status}")
                return []
            alerts = (await response.json()).get("userAlerts", [])
            return [(user_id, a.get("id")) for a in alerts if a.get("class") == "COA"]

        matches = []
        # Process in batches of CONCURRENCY to cap parallel requests; scan all users.
        for start in range(0, len(user_ids), CONCURRENCY):
            batch = user_ids[start:start + CONCURRENCY]
            results = await asyncio.gather(*(check(uid) for uid in batch))
            for hits in results:
                matches.extend(hits)

        await context.dispose()
        return matches


def test_fetch_coa_dismissable_alerts(user_ids):
    """Scan all users and list every alert where class == 'COA' (parallelized)."""
    matches = _run_async(_find_all_coa(user_ids))

    print(f"\n=== COA alerts found: {len(matches)} ===")
    for user_id, alert_id in matches:
        print(f"{user_id} -> {alert_id}")
