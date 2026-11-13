"""
Cloudmail Wallet Withdraw API Tests
POST: /api/wallet/withdraw

Payload:
    {
        "registration_id": <int>,
        "wallet_type": "cloudmail",
        "amount": <float>
    }

Positive Tests:
1) Verify status code is 200
2) Verify response status is "success"
3) Verify wallet.crc_user_id matches the payload registration_id
4) Verify withdraw deducts the amount from the initial balance
   (initial_balance - amount == response.balance)

Negative Tests:
5) Verify withdrawing more than the available balance is rejected
6) Verify zero amount is rejected
7) Verify negative amount is rejected
8) Verify missing amount is rejected
9) Verify non-existent registration_id is rejected
10) Verify GET method is not allowed
"""

import pytest

base_url = "http://qa-cloudmail-letters.internal.creditrepaircloud.com/api"
withdraw_endpoint = f"{base_url}/wallet/withdraw"
recharge_endpoint = f"{base_url}/wallet/recharge"
balance_endpoint_template = f"{base_url}/wallet/balance/{{registration_id}}/{{wallet_type}}"

REGISTRATION_ID = 1001584
WALLET_TYPE = "cloudmail"
WITHDRAW_AMOUNT = 5.00


def _withdraw_payload(amount: float = WITHDRAW_AMOUNT) -> dict:
    return {
        "registration_id": REGISTRATION_ID,
        "wallet_type": WALLET_TYPE,
        "amount": amount,
    }


def _recharge_payload(amount: float) -> dict:
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
# Auto-restore fixture
#
# Snapshots the wallet balance before each test and, after the test,
# recharges back any net debit so the wallet is left unchanged.
# Tests that intentionally need a different post-state can opt out by
# adding the marker @pytest.mark.no_balance_restore.
# -------------------------------------------------------------------
@pytest.fixture(autouse=True)
def restore_wallet_balance(request, request_context):
    if "no_balance_restore" in request.keywords:
        yield
        return

    starting_balance = _get_current_balance(request_context)
    yield
    ending_balance = _get_current_balance(request_context)

    deficit = round(starting_balance - ending_balance, 2)
    if deficit > 0:
        response = request_context.post(
            recharge_endpoint, data=_recharge_payload(deficit)
        )
        assert response.status == 200, (
            f"Failed to restore wallet balance after test "
            f"(deficit=${deficit}): {response.status} {response.text()}"
        )


# -------------------------------------------------------------------
# Positive Tests
# -------------------------------------------------------------------
def test_withdraw_status_code_is_200(request_context):
    """Verify withdraw returns 200"""
    response = request_context.post(withdraw_endpoint, data=_withdraw_payload())
    assert response.status == 200


def test_withdraw_response_status_is_success(request_context):
    """Verify response status is 'success'"""
    response = request_context.post(withdraw_endpoint, data=_withdraw_payload())
    data = response.json()
    assert data["status"] == "success"


def test_withdraw_request_id_matches_response_id(request_context):
    """Verify payload registration_id matches wallet.crc_user_id in the response"""
    payload = _withdraw_payload()
    response = request_context.post(withdraw_endpoint, data=payload)
    wallet = response.json()["data"]["wallet"]

    assert wallet["crc_user_id"] == payload["registration_id"], (
        f"crc_user_id mismatch: payload registration_id={payload['registration_id']}, "
        f"response crc_user_id={wallet['crc_user_id']}"
    )


def test_withdraw_deducts_from_initial_balance(request_context):
    """
    The core validation: capture the initial balance, withdraw $5.00,
    and verify the resulting balance equals (initial_balance - 5.00).
    """
    initial_balance = _get_current_balance(request_context)
    print(f"\nInitial balance : ${initial_balance}")

    payload = _withdraw_payload(WITHDRAW_AMOUNT)
    response = request_context.post(withdraw_endpoint, data=payload)
    assert response.status == 200, f"Withdraw failed: {response.status} {response.text()}"

    body = response.json()
    assert body["status"] == "success", f"Unexpected status: {body}"

    balance_after = float(body["data"]["wallet"]["balance"])
    expected_balance = round(initial_balance - WITHDRAW_AMOUNT, 2)

    print(f"Withdraw amount : ${WITHDRAW_AMOUNT}")
    print(f"Expected balance: ${expected_balance}")
    print(f"Actual balance  : ${balance_after}")

    assert balance_after == expected_balance, (
        f"Balance mismatch after withdraw: "
        f"expected ${expected_balance} ({initial_balance} - {WITHDRAW_AMOUNT}), "
        f"got ${balance_after}"
    )


# -------------------------------------------------------------------
# Negative Tests
# -------------------------------------------------------------------
def test_withdraw_more_than_balance_rejected(request_context):
    """Verify withdrawing more than the available balance is rejected"""
    huge_amount = _get_current_balance(request_context) + 10_000.00
    response = request_context.post(withdraw_endpoint, data=_withdraw_payload(huge_amount))
    body = response.json()
    assert body["status"] != "success"


@pytest.mark.parametrize("invalid_amount", [0, 0.00])
def test_withdraw_zero_amount_rejected(request_context, invalid_amount):
    """Verify zero amount is rejected"""
    response = request_context.post(withdraw_endpoint, data=_withdraw_payload(invalid_amount))
    body = response.json()
    assert body["status"] != "success"


def test_withdraw_negative_amount_rejected(request_context):
    """Verify a negative amount is rejected"""
    response = request_context.post(withdraw_endpoint, data=_withdraw_payload(-5.00))
    body = response.json()
    assert body["status"] != "success"


def test_withdraw_missing_amount_rejected(request_context):
    """Verify request without amount is rejected"""
    payload = {"registration_id": REGISTRATION_ID, "wallet_type": WALLET_TYPE}
    response = request_context.post(withdraw_endpoint, data=payload)
    body = response.json()

    assert body["status"] == "fail"
    assert "amount" in body.get("message", {})


def test_withdraw_non_existent_registration_id_rejected(request_context):
    """Verify withdrawing from a non-existent wallet is rejected"""
    payload = {
        "registration_id": 999999999,
        "wallet_type": WALLET_TYPE,
        "amount": WITHDRAW_AMOUNT,
    }
    response = request_context.post(withdraw_endpoint, data=payload)
    body = response.json()
    assert body["status"] != "success"


def test_withdraw_get_method_not_allowed(request_context):
    """Verify GET method is not allowed"""
    response = request_context.get(withdraw_endpoint)
    assert response.status == 405
