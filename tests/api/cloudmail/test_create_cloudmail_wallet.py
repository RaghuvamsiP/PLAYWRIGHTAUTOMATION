"""
Create Cloudmail Wallet API Tests
POST: /api/wallet

Payload:
    {
        "registration_id": <int>,
        "wallet_type": "cloudmail"
    }

Positive Tests:
1) Verify creating a new wallet returns 200/201
2) Verify response status is "success"
3) Verify response message
4) Verify response contains "data.wallet"
5) Verify wallet object has all required fields (id, type, crc_user_id, balance)
6) Verify wallet "id" is a valid UUID
7) Verify wallet "type" matches the requested wallet_type
8) Verify new wallet "balance" is 0

Negative Tests:
9)  Verify creating a wallet for an existing registration_id returns "already taken"
10) Verify missing registration_id is rejected
11) Verify missing wallet_type is rejected
12) Verify empty payload is rejected
13) Verify invalid (non-numeric) registration_id is rejected
14) Verify invalid wallet_type value is rejected
15) Verify GET method is not allowed
16) Verify PUT method is not allowed
17) Verify DELETE method is not allowed
"""

import time
import uuid

import pytest

base_url = "http://qa-cloudmail-letters.internal.creditrepaircloud.com/api"
endpoint = f"{base_url}/wallet"

# Registration ID known to already have a cloudmail wallet
EXISTING_REGISTRATION_ID = 1001584
WALLET_TYPE = "cloudmail"


def _unique_registration_id() -> int:
    """Generate a registration_id unlikely to collide with existing wallets."""
    return int(time.time() * 1000) % 2_000_000_000


# -------------------------------------------------------------------
# Positive Tests
#
# NOTE: These hit a live POST endpoint. They use a generated
# registration_id so the test does not collide with seeded data.
# If the backend rejects unknown registration_ids, mark as skipped
# or replace `_unique_registration_id()` with a known-fresh id.
# -------------------------------------------------------------------
@pytest.fixture
def new_wallet_payload():
    return {
        "registration_id": _unique_registration_id(),
        "wallet_type": WALLET_TYPE,
    }


def test_create_wallet_returns_success_status(request_context, new_wallet_payload):
    """Verify a new wallet creation returns success"""
    response = request_context.post(endpoint, data=new_wallet_payload)
    assert response.status in (200, 201)

    data = response.json()
    assert data["status"] == "success"


def test_create_wallet_response_message(request_context, new_wallet_payload):
    """Verify response message on successful wallet creation"""
    response = request_context.post(endpoint, data=new_wallet_payload)
    data = response.json()
    assert data["message"] == "Wallet created successfully"


def test_create_wallet_response_contains_wallet(request_context, new_wallet_payload):
    """Verify response contains data.wallet"""
    response = request_context.post(endpoint, data=new_wallet_payload)
    data = response.json()
    assert "data" in data
    assert "wallet" in data["data"]


def test_create_wallet_required_fields(request_context, new_wallet_payload):
    """Verify the returned wallet has all required fields"""
    response = request_context.post(endpoint, data=new_wallet_payload)
    wallet = response.json()["data"]["wallet"]

    for field in ("id", "type", "crc_user_id", "balance"):
        assert field in wallet, f"Missing field: {field}"


def test_create_wallet_id_is_uuid(request_context, new_wallet_payload):
    """Verify the wallet id is a valid UUID"""
    response = request_context.post(endpoint, data=new_wallet_payload)
    wallet_id = response.json()["data"]["wallet"]["id"]
    uuid.UUID(wallet_id)


def test_create_wallet_type_matches_payload(request_context, new_wallet_payload):
    """Verify wallet 'type' matches the requested wallet_type"""
    response = request_context.post(endpoint, data=new_wallet_payload)
    wallet = response.json()["data"]["wallet"]
    assert wallet["type"] == new_wallet_payload["wallet_type"]


def test_create_wallet_initial_balance_is_zero(request_context, new_wallet_payload):
    """Verify a newly created wallet has balance = 0"""
    response = request_context.post(endpoint, data=new_wallet_payload)
    wallet = response.json()["data"]["wallet"]
    assert wallet["balance"] == 0


# -------------------------------------------------------------------
# Negative Tests
# -------------------------------------------------------------------
def test_duplicate_registration_id_rejected(request_context):
    """Verify creating a wallet for an existing registration_id is rejected"""
    payload = {
        "registration_id": EXISTING_REGISTRATION_ID,
        "wallet_type": WALLET_TYPE,
    }
    response = request_context.post(endpoint, data=payload)
    body = response.json()

    assert body["status"] == "fail"
    assert body["code"] == "invalid_request"
    assert body["message"]["registration_id"] == [
        "The registration id has already been taken."
    ]


def test_missing_registration_id_rejected(request_context):
    """Verify request without registration_id is rejected"""
    payload = {"wallet_type": WALLET_TYPE}
    response = request_context.post(endpoint, data=payload)
    body = response.json()

    assert body["status"] == "fail"
    assert body["code"] == "invalid_request"
    assert "registration_id" in body["message"]


def test_missing_wallet_type_rejected(request_context):
    """Verify request without wallet_type is rejected"""
    payload = {"registration_id": _unique_registration_id()}
    response = request_context.post(endpoint, data=payload)
    body = response.json()

    assert body["status"] == "fail"
    assert body["code"] == "invalid_request"
    assert "wallet_type" in body["message"]


def test_empty_payload_rejected(request_context):
    """Verify empty payload is rejected"""
    response = request_context.post(endpoint, data={})
    body = response.json()

    assert body["status"] == "fail"
    assert body["code"] == "invalid_request"


def test_invalid_registration_id_format(request_context):
    """Verify a non-numeric registration_id is rejected"""
    payload = {"registration_id": "not-a-number", "wallet_type": WALLET_TYPE}
    response = request_context.post(endpoint, data=payload)
    body = response.json()

    assert body["status"] == "fail"


def test_invalid_wallet_type_rejected(request_context):
    """Verify an invalid wallet_type value is rejected"""
    payload = {
        "registration_id": _unique_registration_id(),
        "wallet_type": "invalidtype",
    }
    response = request_context.post(endpoint, data=payload)
    body = response.json()

    assert body["status"] != "success"


def test_get_method_not_allowed(request_context):
    """Verify GET method is not allowed"""
    response = request_context.get(endpoint)
    assert response.status == 405


def test_put_method_not_allowed(request_context):
    """Verify PUT method is not allowed"""
    response = request_context.put(endpoint)
    assert response.status == 405


def test_delete_method_not_allowed(request_context):
    """Verify DELETE method is not allowed"""
    response = request_context.delete(endpoint)
    assert response.status == 405
