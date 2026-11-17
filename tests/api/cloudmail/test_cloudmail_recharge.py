"""
Cloudmail Wallet Recharge API Tests
POST: /api/wallet/recharge

Payload:
    {
        "registration_id": <int>,
        "wallet_type": "cloudmail",
        "amount": <float>
    }

Positive Tests:
1)  Verify status code is 200
2)  Verify response status is "success"
3)  Verify response message
4)  Verify response contains data.wallet
5)  Verify wallet has all required fields (id, type, crc_user_id, balance, recharge_with_amount)
6)  Verify wallet "id" is a valid UUID
7)  Verify wallet "type" matches payload wallet_type
8)  Verify wallet.crc_user_id matches payload registration_id  (request id == response id)
9)  Verify recharging twice cumulatively increases the balance by the recharged amounts

Negative Tests:
10) Verify non-existent wallet (registration_id) is rejected
11) Verify missing registration_id is rejected
12) Verify missing wallet_type is rejected
13) Verify missing amount is rejected
14) Verify zero amount is rejected
15) Verify negative amount is rejected
16) Verify non-numeric amount is rejected
17) Verify invalid wallet_type is rejected
18) Verify GET method is not allowed
19) Verify PUT method is not allowed
20) Verify DELETE method is not allowed
"""

import uuid

import pytest

base_url = "http://qa-cloudmail-letters.internal.creditrepaircloud.com/api"
recharge_endpoint = f"{base_url}/wallet/recharge"
balance_endpoint_template = f"{base_url}/wallet/balance/{{registration_id}}/{{wallet_type}}"

REGISTRATION_ID = 1001584
WALLET_TYPE = "cloudmail"
DEFAULT_AMOUNT = 1.00


def _recharge_payload(amount: float = DEFAULT_AMOUNT) -> dict:
    return {
        "registration_id": REGISTRATION_ID,
        "wallet_type": WALLET_TYPE,
        "amount": amount,
    }


def _get_current_balance(request_context) -> float:
    """Fetch the current wallet balance for the seed registration_id."""
    url = balance_endpoint_template.format(
        registration_id=REGISTRATION_ID, wallet_type=WALLET_TYPE
    )
    response = request_context.get(url)
    assert response.status == 200, f"Failed to fetch balance: {response.status}"
    return float(response.json()["data"]["balance"])


# -------------------------------------------------------------------
# Positive Tests
# -------------------------------------------------------------------
def test_status_code_is_200(request_context):
    """Verify recharge returns 200"""
    response = request_context.post(recharge_endpoint, data=_recharge_payload())
    assert response.status == 200


def test_response_status_is_success(request_context):
    """Verify response status is 'success'"""
    response = request_context.post(recharge_endpoint, data=_recharge_payload())
    data = response.json()
    assert data["status"] == "success"


def test_response_message(request_context):
    """Verify response message"""
    response = request_context.post(recharge_endpoint, data=_recharge_payload())
    data = response.json()
    assert data["message"] == "Wallet recharged successfully"


def test_response_contains_wallet(request_context):
    """Verify response contains data.wallet"""
    response = request_context.post(recharge_endpoint, data=_recharge_payload())
    data = response.json()
    assert "data" in data
    assert "wallet" in data["data"]


def test_wallet_has_required_fields(request_context):
    """Verify the returned wallet contains all required fields"""
    response = request_context.post(recharge_endpoint, data=_recharge_payload())
    wallet = response.json()["data"]["wallet"]

    for field in ("id", "type", "crc_user_id", "balance", "recharge_with_amount"):
        assert field in wallet, f"Missing field: {field}"


def test_wallet_id_is_uuid(request_context):
    """Verify wallet 'id' is a valid UUID"""
    response = request_context.post(recharge_endpoint, data=_recharge_payload())
    wallet_id = response.json()["data"]["wallet"]["id"]
    uuid.UUID(wallet_id)


def test_wallet_type_matches_payload(request_context):
    """Verify wallet 'type' matches payload wallet_type"""
    payload = _recharge_payload()
    response = request_context.post(recharge_endpoint, data=payload)
    wallet = response.json()["data"]["wallet"]
    assert wallet["type"] == payload["wallet_type"]


def test_request_id_matches_response_id(request_context):
    """Verify the registration_id sent in the payload matches wallet.crc_user_id in the response."""
    payload = _recharge_payload()
    response = request_context.post(recharge_endpoint, data=payload)
    wallet = response.json()["data"]["wallet"]

    assert wallet["crc_user_id"] == payload["registration_id"], (
        f"crc_user_id mismatch: payload registration_id={payload['registration_id']}, "
        f"response crc_user_id={wallet['crc_user_id']}"
    )


def test_balance_accumulates_across_two_recharges(request_context):
    """
    Recharge twice and verify the balance increases by exactly the sum
    of the two recharge amounts.
    """
    first_amount = 1.00
    second_amount = 2.50

    starting_balance = _get_current_balance(request_context)

    first_response = request_context.post(
        recharge_endpoint, data=_recharge_payload(first_amount)
    )
    assert first_response.status == 200, f"First recharge failed: {first_response.text()}"
    balance_after_first = float(first_response.json()["data"]["wallet"]["balance"])

    expected_after_first = round(starting_balance + first_amount, 2)
    assert balance_after_first == expected_after_first, (
        f"After first recharge: expected {expected_after_first}, got {balance_after_first}"
    )

    second_response = request_context.post(
        recharge_endpoint, data=_recharge_payload(second_amount)
    )
    assert second_response.status == 200, f"Second recharge failed: {second_response.text()}"
    balance_after_second = float(second_response.json()["data"]["wallet"]["balance"])

    expected_after_second = round(balance_after_first + second_amount, 2)
    assert balance_after_second == expected_after_second, (
        f"After second recharge: expected {expected_after_second}, got {balance_after_second}"
    )

    total_added = round(balance_after_second - starting_balance, 2)
    assert total_added == round(first_amount + second_amount, 2), (
        f"Cumulative recharge mismatch: expected {first_amount + second_amount}, "
        f"got {total_added}"
    )


# -------------------------------------------------------------------
# Negative Tests
# -------------------------------------------------------------------
def test_non_existent_registration_id_rejected(request_context):
    """Verify recharging a wallet that does not exist is rejected"""
    payload = {
        "registration_id": 999999999,
        "wallet_type": WALLET_TYPE,
        "amount": DEFAULT_AMOUNT,
    }
    response = request_context.post(recharge_endpoint, data=payload)
    body = response.json()
    assert body["status"] != "success"


def test_missing_registration_id_rejected(request_context):
    """Verify request without registration_id is rejected"""
    payload = {"wallet_type": WALLET_TYPE, "amount": DEFAULT_AMOUNT}
    response = request_context.post(recharge_endpoint, data=payload)
    body = response.json()

    assert body["status"] == "fail"
    assert body["code"] == "invalid_request"
    assert "registration_id" in body["message"]


def test_missing_wallet_type_rejected(request_context):
    """Verify request without wallet_type is rejected"""
    payload = {"registration_id": REGISTRATION_ID, "amount": DEFAULT_AMOUNT}
    response = request_context.post(recharge_endpoint, data=payload)
    body = response.json()

    assert body["status"] == "fail"
    assert body["code"] == "invalid_request"
    assert "wallet_type" in body["message"]


def test_missing_amount_rejected(request_context):
    """Verify request without amount is rejected"""
    payload = {"registration_id": REGISTRATION_ID, "wallet_type": WALLET_TYPE}
    response = request_context.post(recharge_endpoint, data=payload)
    body = response.json()

    assert body["status"] == "fail"
    assert body["code"] == "invalid_request"
    assert "amount" in body["message"]


@pytest.mark.parametrize("invalid_amount", [0, 0.00])
def test_zero_amount_rejected(request_context, invalid_amount):
    """Verify zero amount is rejected"""
    response = request_context.post(recharge_endpoint, data=_recharge_payload(invalid_amount))
    body = response.json()
    assert body["status"] != "success"


def test_negative_amount_rejected(request_context):
    """Verify a negative amount is rejected"""
    response = request_context.post(recharge_endpoint, data=_recharge_payload(-5.00))
    body = response.json()
    assert body["status"] != "success"


def test_non_numeric_amount_rejected(request_context):
    """Verify non-numeric amount is rejected"""
    payload = {
        "registration_id": REGISTRATION_ID,
        "wallet_type": WALLET_TYPE,
        "amount": "abc",
    }
    response = request_context.post(recharge_endpoint, data=payload)
    body = response.json()
    assert body["status"] != "success"


def test_invalid_wallet_type_rejected(request_context):
    """Verify an invalid wallet_type value is rejected"""
    payload = {
        "registration_id": REGISTRATION_ID,
        "wallet_type": "invalidtype",
        "amount": DEFAULT_AMOUNT,
    }
    response = request_context.post(recharge_endpoint, data=payload)
    body = response.json()
    assert body["status"] != "success"


def test_get_method_not_allowed(request_context):
    """Verify GET method is not allowed"""
    response = request_context.get(recharge_endpoint)
    assert response.status == 405


def test_put_method_not_allowed(request_context):
    """Verify PUT method is not allowed"""
    response = request_context.put(recharge_endpoint)
    assert response.status == 405


def test_delete_method_not_allowed(request_context):
    """Verify DELETE method is not allowed"""
    response = request_context.delete(recharge_endpoint)
    assert response.status == 405
