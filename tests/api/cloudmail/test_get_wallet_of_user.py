"""
Get Wallets Of User API Tests
GET: /api/wallets/{registration_id}

Both "exists" and "not exists" responses return HTTP 200 with status=success.
The difference is whether data.wallets is populated or an empty list.

Positive Tests:
1)  Verify status code is 200 for an existing user
2)  Verify response status is "success"
3)  Verify response message
4)  Verify response contains data.wallets list
5)  Verify wallets list is not empty for a user with a wallet
6)  Verify each wallet has required fields (id, type, crc_user_id, balance, recharge_with_amount)
7)  Verify wallet "id" is a valid UUID
8)  Verify wallet "crc_user_id" matches the requested registration_id
9)  Verify wallet "balance" is numeric
10) Verify a user without a wallet returns an empty wallets list

Negative Tests:
11) Verify invalid (non-numeric) registration_id is rejected
12) Verify POST method is not allowed
13) Verify PUT method is not allowed
14) Verify DELETE method is not allowed
15) Verify malformed endpoint returns 404
"""

import uuid

base_url = "http://qa-cloudmail-letters.internal.creditrepaircloud.com/api"

EXISTING_REGISTRATION_ID = 1001584
NON_EXISTENT_REGISTRATION_ID = 999999999

valid_endpoint = f"{base_url}/wallets/{EXISTING_REGISTRATION_ID}"


# -------------------------------------------------------------------
# Positive Tests
# -------------------------------------------------------------------
def test_status_code_is_200(request_context):
    """Verify GET wallets returns 200 for an existing user"""
    response = request_context.get(valid_endpoint)
    assert response.status == 200


def test_response_status_is_success(request_context):
    """Verify response status is 'success'"""
    response = request_context.get(valid_endpoint)
    assert response.status == 200

    data = response.json()
    assert data["status"] == "success"


def test_response_message(request_context):
    """Verify response message"""
    response = request_context.get(valid_endpoint)
    assert response.status == 200

    data = response.json()
    assert data["message"] == "Wallets retrieved successfully"


def test_response_contains_wallets_list(request_context):
    """Verify response contains data.wallets list"""
    response = request_context.get(valid_endpoint)
    assert response.status == 200

    data = response.json()
    assert "data" in data
    assert "wallets" in data["data"]
    assert isinstance(data["data"]["wallets"], list)


def test_wallets_list_not_empty_for_existing_user(request_context):
    """Verify wallets list is not empty for a user with at least one wallet"""
    response = request_context.get(valid_endpoint)
    assert response.status == 200

    wallets = response.json()["data"]["wallets"]
    assert len(wallets) > 0


def test_each_wallet_has_required_fields(request_context):
    """Verify each wallet has required fields"""
    response = request_context.get(valid_endpoint)
    assert response.status == 200

    wallets = response.json()["data"]["wallets"]
    required_fields = ("id", "type", "crc_user_id", "balance", "recharge_with_amount")
    for wallet in wallets:
        for field in required_fields:
            assert field in wallet, f"Missing field '{field}' in wallet: {wallet}"


def test_wallet_id_is_uuid(request_context):
    """Verify each wallet 'id' is a valid UUID"""
    response = request_context.get(valid_endpoint)
    assert response.status == 200

    wallets = response.json()["data"]["wallets"]
    for wallet in wallets:
        uuid.UUID(wallet["id"])


def test_wallet_crc_user_id_matches_request(request_context):
    """Verify wallet.crc_user_id matches the requested registration_id"""
    response = request_context.get(valid_endpoint)
    assert response.status == 200

    wallets = response.json()["data"]["wallets"]
    for wallet in wallets:
        assert wallet["crc_user_id"] == EXISTING_REGISTRATION_ID


def test_wallet_balance_is_numeric(request_context):
    """Verify wallet 'balance' is numeric"""
    response = request_context.get(valid_endpoint)
    assert response.status == 200

    wallets = response.json()["data"]["wallets"]
    for wallet in wallets:
        assert isinstance(wallet["balance"], (int, float))
        assert wallet["balance"] >= 0


def test_user_without_wallet_returns_empty_list(request_context):
    """Verify a user with no wallet returns an empty wallets list (still success)"""
    endpoint = f"{base_url}/wallets/{NON_EXISTENT_REGISTRATION_ID}"
    response = request_context.get(endpoint)
    assert response.status == 200

    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Wallets retrieved successfully"
    assert data["data"]["wallets"] == []


# -------------------------------------------------------------------
# Negative Tests
# -------------------------------------------------------------------
def test_invalid_registration_id_format(request_context):
    """Verify a non-numeric registration_id is rejected"""
    endpoint = f"{base_url}/wallets/abc"
    response = request_context.get(endpoint)

    assert response.status != 200
    body = response.json()
    assert body.get("status") != "success"


def test_post_method_not_allowed(request_context):
    """Verify POST method returns 405"""
    response = request_context.post(valid_endpoint)
    assert response.status == 405


def test_put_method_not_allowed(request_context):
    """Verify PUT method returns 405"""
    response = request_context.put(valid_endpoint)
    assert response.status == 405


def test_delete_method_not_allowed(request_context):
    """Verify DELETE method returns 405"""
    response = request_context.delete(valid_endpoint)
    assert response.status == 405


def test_malformed_endpoint_returns_404(request_context):
    """Verify a malformed endpoint returns 404"""
    response = request_context.get(f"{base_url}/wallets/invalid/extra/segment")
    assert response.status == 404
