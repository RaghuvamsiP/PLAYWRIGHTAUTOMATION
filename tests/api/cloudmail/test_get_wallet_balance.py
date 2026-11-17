"""
Wallet Balance API Tests
GET: /api/wallet/balance/{client_id}/{wallet_type}

Positive Tests:
1) Verify status code is 200 for an existing wallet
2) Verify response status is "success"
3) Verify response message
4) Verify "data" object is present
5) Verify "balance" field exists and is numeric
6) Verify "last_recharged_amount" field exists and is numeric
7) Verify "last_recharged_date" field exists and is a valid datetime string
8) Verify "threshold_balance" field exists and is numeric
9) Verify "auto_reload_enabled" field exists and is boolean
10) Verify "recharge_with_amount" field exists and is numeric

Negative Tests:
11) Verify wallet-not-found returns "error" status with proper message
12) Verify wallet-not-found response contains no "data" key
13) Verify invalid (non-numeric) client_id returns error
14) Verify invalid wallet_type returns error
15) Verify POST method is not allowed
16) Verify PUT method is not allowed
17) Verify DELETE method is not allowed
18) Verify invalid endpoint returns 404
"""

from datetime import datetime

base_url = "http://qa-cloudmail-letters.internal.creditrepaircloud.com/api"
VALID_CLIENT_ID = 1001584
VALID_WALLET_TYPE = "cloudmail"

valid_endpoint = f"{base_url}/wallet/balance/{VALID_CLIENT_ID}/{VALID_WALLET_TYPE}"


# -------------------------------------------------------------------
# Positive Tests
# -------------------------------------------------------------------
def test_status_code_is_200(request_context):
    """Verify GET wallet balance returns 200 for existing wallet"""
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
    assert data["message"] == "Wallet balance retrieved successfully"


def test_data_object_present(request_context):
    """Verify response contains a 'data' object"""
    response = request_context.get(valid_endpoint)
    assert response.status == 200

    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], dict)


def test_balance_field(request_context):
    """Verify 'balance' field exists and is numeric"""
    response = request_context.get(valid_endpoint)
    assert response.status == 200

    body = response.json()["data"]
    assert "balance" in body
    assert isinstance(body["balance"], (int, float))
    assert body["balance"] >= 0


def test_last_recharged_amount_field(request_context):
    """Verify 'last_recharged_amount' exists and is numeric"""
    response = request_context.get(valid_endpoint)
    assert response.status == 200

    body = response.json()["data"]
    assert "last_recharged_amount" in body
    assert isinstance(body["last_recharged_amount"], (int, float))


def test_last_recharged_date_field(request_context):
    """Verify 'last_recharged_date' exists and is a valid datetime string"""
    response = request_context.get(valid_endpoint)
    assert response.status == 200

    body = response.json()["data"]
    assert "last_recharged_date" in body
    datetime.strptime(body["last_recharged_date"], "%Y-%m-%d %H:%M:%S")


def test_threshold_balance_field(request_context):
    """Verify 'threshold_balance' exists and is numeric"""
    response = request_context.get(valid_endpoint)
    assert response.status == 200

    body = response.json()["data"]
    assert "threshold_balance" in body
    assert isinstance(body["threshold_balance"], (int, float))


def test_auto_reload_enabled_field(request_context):
    """Verify 'auto_reload_enabled' exists and is boolean"""
    response = request_context.get(valid_endpoint)
    assert response.status == 200

    body = response.json()["data"]
    assert "auto_reload_enabled" in body
    assert isinstance(body["auto_reload_enabled"], bool)


def test_recharge_with_amount_field(request_context):
    """Verify 'recharge_with_amount' exists and is numeric"""
    response = request_context.get(valid_endpoint)
    assert response.status == 200

    body = response.json()["data"]
    assert "recharge_with_amount" in body
    assert isinstance(body["recharge_with_amount"], (int, float))


# -------------------------------------------------------------------
# Negative Tests
# -------------------------------------------------------------------
def test_wallet_not_found_returns_error_status(request_context):
    """Verify response when wallet does not exist for the given client_id"""
    non_existent_client_id = 999999999
    endpoint = f"{base_url}/wallet/balance/{non_existent_client_id}/{VALID_WALLET_TYPE}"
    response = request_context.get(endpoint)

    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "No wallet found with the given details"


def test_wallet_not_found_has_no_data(request_context):
    """Verify wallet-not-found response does not include a 'data' object"""
    non_existent_client_id = 999999999
    endpoint = f"{base_url}/wallet/balance/{non_existent_client_id}/{VALID_WALLET_TYPE}"
    response = request_context.get(endpoint)

    data = response.json()
    assert "data" not in data or data.get("data") in (None, {}, [])


def test_invalid_client_id_format(request_context):
    """Verify invalid (non-numeric) client_id is rejected"""
    endpoint = f"{base_url}/wallet/balance/abc/{VALID_WALLET_TYPE}"
    response = request_context.get(endpoint)

    assert response.status != 200
    body = response.json()
    assert body.get("status") != "success"


def test_invalid_wallet_type(request_context):
    """Verify an invalid wallet_type is rejected"""
    endpoint = f"{base_url}/wallet/balance/{VALID_CLIENT_ID}/invalidtype"
    response = request_context.get(endpoint)

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


def test_invalid_endpoint_returns_404(request_context):
    """Verify a malformed endpoint returns 404"""
    response = request_context.get(f"{base_url}/wallet/invalid/{VALID_CLIENT_ID}/{VALID_WALLET_TYPE}")
    assert response.status == 404
