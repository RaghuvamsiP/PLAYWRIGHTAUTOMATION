"""
API Tests for Restful Booker using Playwright
Best practice: One authenticated request context fixture
"""

import pytest
import json
from pathlib import Path
from playwright.sync_api import Playwright

# -------------------------------------------------------------------
# Base directory & Base URL
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2] / "test_data" / "api"
BASE_URL = "https://restful-booker.herokuapp.com"


# -------------------------------------------------------------------
# Utility Function: Reads JSON data from a given file
# -------------------------------------------------------------------
def read_json(filename):
    return json.loads((BASE_DIR / filename).read_text())


# -------------------------------------------------------------------
# Fixture: Authenticated Request Context
# -------------------------------------------------------------------
@pytest.fixture(scope="session")
def request_context(playwright: Playwright):
    """
    Creates a Playwright APIRequestContext with auth token automatically
    included in headers for all requests.
    """
    # Step 1: Temporary context to get auth token
    temp_context = playwright.request.new_context(base_url=BASE_URL)
    login_data = read_json("token_request_body.json")
    response = temp_context.post("/auth", data=login_data)
    assert response.ok, "Failed to get auth token"
    token = response.json()["token"]
    temp_context.dispose()

    # Step 2: Create authenticated context with token in headers
    context = playwright.request.new_context(
        base_url=BASE_URL,
        extra_http_headers={"Cookie": f"token={token}",
                            "Content-Type": "application/json"}
    )

    yield context
    context.dispose()


# -------------------------------------------------------------------
# 1) Create Booking (POST)
# -------------------------------------------------------------------
def test_create_booking(request_context):
    data = read_json("post_request_body.json")
    response = request_context.post("/booking", data=data)

    assert response.ok
    assert response.status == 200

    res_body = response.json()
    print("\nCreate Booking Response:", res_body)

    # Validate response
    assert "bookingid" in res_body
    assert "booking" in res_body
    booking = res_body["booking"]

    assert booking["firstname"] == data["firstname"]
    assert booking["lastname"] == data["lastname"]
    assert booking["totalprice"] == data["totalprice"]
    assert booking["depositpaid"] == data["depositpaid"]
    assert booking["bookingdates"]["checkin"] == data["bookingdates"]["checkin"]
    assert booking["bookingdates"]["checkout"] == data["bookingdates"]["checkout"]

    # Store booking ID for other tests
    global booking_id
    booking_id = res_body["bookingid"]


# -------------------------------------------------------------------
# 2) Get Booking Details (GET)
# -------------------------------------------------------------------
def test_get_booking_by_id(request_context):
    response = request_context.get(f"/booking/{booking_id}")
    assert response.ok
    assert response.status == 200

    res_body = response.json()
    print(f"\nBooking details fetched by ID {booking_id}:", res_body)
    assert "firstname" in res_body
    assert "lastname" in res_body


def test_get_booking_by_name(request_context):
    params = {"firstname": "Jim", "lastname": "Brown"}
    response = request_context.get("/booking", params=params)
    assert response.ok
    assert response.status == 200

    res_body = response.json()
    print(f"\nBooking details fetched by Name {params}:", res_body)
    assert len(res_body) > 0
    for item in res_body:
        assert "bookingid" in item


def test_get_booking_by_dates(request_context):
    params = {"checkin": "2025-12-15", "checkout": "2025-12-20"}
    response = request_context.get("/booking", params=params)
    assert response.ok
    assert response.status == 200

    res_body = response.json()
    print(f"\nBooking details fetched by Dates {params}:", res_body)
    for item in res_body:
        assert "bookingid" in item


# -------------------------------------------------------------------
# 3) Partial Update Booking (PATCH)
# -------------------------------------------------------------------
def test_partial_update_booking(request_context):
    data = read_json("patch_request_body.json")
    response = request_context.patch(f"/booking/{booking_id}", data=data)
    assert response.ok
    assert response.status == 200

    res_body = response.json()
    print(f"\nPartial Update Response for booking {booking_id}:", res_body)

    for key in data.keys():
        assert key in res_body
        assert res_body[key] == data[key]


# -------------------------------------------------------------------
# 4) Full Update Booking (PUT)
# -------------------------------------------------------------------
def test_full_update_booking(request_context):
    data = read_json("put_request_body.json")
    response = request_context.put(f"/booking/{booking_id}", data=data)
    assert response.ok
    assert response.status == 200

    res_body = response.json()
    print(f"\nFull Update Response for booking {booking_id}:", res_body)

    assert res_body["firstname"] == data["firstname"]
    assert res_body["lastname"] == data["lastname"]
    assert res_body["totalprice"] == data["totalprice"]


# -------------------------------------------------------------------
# 5) Delete Booking (DELETE)
# -------------------------------------------------------------------
def test_delete_booking(request_context):
    response = request_context.delete(f"/booking/{booking_id}")
    assert response.status == 201
    assert response.status_text == "Created"
    print(f"\nBooking deleted successfully - ID: {booking_id}")
