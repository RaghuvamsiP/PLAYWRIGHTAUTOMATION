"""
1) Create Booking (POST) ---> BookingID
2) Get Booking Details (GET) - By ID, By Names, By Dates
3) Create Token (POST /auth)
4) Partial Update Booking (PATCH)
5) Full Update Booking (PUT)
6) Delete Booking (DELETE)
"""

import pytest
import json
from pathlib import Path
from playwright.sync_api import Playwright

# -------------------------------------------------------------------
# Base URL of the RESTful Booker API
# -------------------------------------------------------------------
base_url = "https://restful-booker.herokuapp.com"

# -------------------------------------------------------------------
# Test data directory
# -------------------------------------------------------------------
TEST_DATA_DIR = Path(__file__).resolve().parents[2] / "test_data" / "api"


# -------------------------------------------------------------------
# Utility Function: Reads and returns JSON data from a given file path
# -------------------------------------------------------------------
def read_json(filename):
    with open(TEST_DATA_DIR / filename, "r") as file:
        return json.load(file)


# -------------------------------------------------------------------
# 1) Create Booking (POST)
# -------------------------------------------------------------------
def test_create_booking(request_context):
    """Create a new booking and validate response"""
    data = read_json("post_request_body.json")

    # Send POST request to create booking
    response = request_context.post(f"{base_url}/booking", data=data)

    assert response.ok  # (or)  assert response.status_text=="OK"
    assert response.status == 200

    response_body = response.json()
    print("\nCreate Booking Response:", response_body)

    # Basic validation of response fields
    assert "bookingid" in response_body
    assert "booking" in response_body

    booking = response_body["booking"]

    # Validate key booking details
    assert booking["firstname"] == data["firstname"]
    assert booking["lastname"] == data["lastname"]
    assert booking["totalprice"] == data["totalprice"]
    assert booking["depositpaid"] == data["depositpaid"]
    assert booking["bookingdates"]["checkin"] == data["bookingdates"]["checkin"]
    assert booking["bookingdates"]["checkout"] == data["bookingdates"]["checkout"]

    # Store booking ID globally for reuse in subsequent tests
    global booking_id
    booking_id = response_body["bookingid"]


# -------------------------------------------------------------------
# 2) Get Booking Details (GET)
# -------------------------------------------------------------------
def test_get_booking_by_id(request_context):
    """Get booking details using booking ID"""
    response = request_context.get(f"{base_url}/booking/{booking_id}")

    assert response.ok
    assert response.status == 200

    response_body = response.json()
    print(f"\nBooking details fetched by ID {booking_id}:", response_body)

    # Validate presence of expected fields
    assert "firstname" in response_body
    assert "lastname" in response_body


def test_get_booking_by_name(request_context):
    """Get bookings filtered by first and last name"""
    name_params = {"firstname": "Jim", "lastname": "Brown"}
    response = request_context.get(f"{base_url}/booking", params=name_params)

    assert response.ok
    assert response.status == 200

    response_body = response.json()
    print(f"\nBooking details fetched by Name {name_params}:", response_body)

    # Ensure at least one booking found and contains 'bookingid'
    assert len(response_body) > 0
    for item in response_body:
        assert "bookingid" in item


def test_get_booking_by_dates(request_context):
    """Get bookings filtered by check-in and check-out dates"""
    date_params = {"checkin": "2025-12-15", "checkout": "2025-12-20"}
    response = request_context.get(f"{base_url}/booking", params=date_params)

    assert response.ok
    assert response.status == 200

    response_body = response.json()
    print(f"\nBooking details fetched by Dates {date_params}:", response_body)

    # Validate that response contains booking IDs
    for item in response_body:
        assert "bookingid" in item


# -------------------------------------------------------------------
# 3) Create Token (POST /auth)
# -------------------------------------------------------------------
def test_create_token(request_context):
    """Create an authentication token for further operations"""
    data = read_json("token_request_body.json")
    response = request_context.post(f"{base_url}/auth", data=data)

    assert response.ok
    assert response.status == 200

    response_body = response.json()
    print("\nToken creation response:", response_body)

    # Validate and store token globally
    assert "token" in response_body
    global token
    token = response_body["token"]
    assert len(token) > 5


# -------------------------------------------------------------------
# 4) Partial Update Booking (PATCH)
# -------------------------------------------------------------------
def test_partial_update_booking(request_context):
    """Partially update an existing booking"""
    data = read_json("patch_request_body.json")

    response = request_context.patch(
        f"{base_url}/booking/{booking_id}",
        headers={"Cookie": f"token={token}"},
        data=data,
    )
    assert response.ok
    assert response.status == 200

    response_body = response.json()
    print(f"\nPartial Update Response for booking {booking_id}:", response_body)

    # Validate updated fields match request data
    for key in data.keys():
        assert key in response_body
        assert response_body[key] == data[key]


# -------------------------------------------------------------------
# 5) Full Update Booking (PUT)
# -------------------------------------------------------------------
def test_full_update_booking(request_context):
    """Update entire booking record"""
    data = read_json("put_request_body.json")

    response = request_context.put(
        f"{base_url}/booking/{booking_id}",
        headers={"Cookie": f"token={token}"},
        data=data,
    )
    assert response.ok
    assert response.status == 200

    response_body = response.json()
    print(f"\nFull Update Response for booking {booking_id}:", response_body)

    # Validate that full booking details were updated correctly
    assert response_body["firstname"] == data["firstname"]
    assert response_body["lastname"] == data["lastname"]
    assert response_body["totalprice"] == data["totalprice"]


# -------------------------------------------------------------------
# 6) Delete Booking (DELETE)
# -------------------------------------------------------------------
def test_delete_booking(request_context):
    """Delete booking using auth token"""
    response = request_context.delete(
        f"{base_url}/booking/{booking_id}",
        headers={"Cookie": f"token={token}"}
    )

    # API returns 201 on successful deletion
    assert response.status == 201
    assert response.status_text == "Created"

    print(f"\nBooking deleted successfully - ID:", booking_id)
