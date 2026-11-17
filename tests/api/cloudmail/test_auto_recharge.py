"""
Cloudmail Wallet Auto-Reload API Tests
POST: /api/wallet/autoreload

Payload:
    {
        "registration_id": <int>,
        "wallet_type": "cloudmail",
        "is_auto_reload_enabled": <bool>,
        "threshold_amount": <number>,
        "recharge_amount": <number>
    }

Positive Tests:
1)  Verify status code is 200
2)  Verify response status is "success"
3)  Verify response message
4)  Verify response contains data.wallet
5)  Verify wallet has all required fields (id, type, crc_user_id, balance, recharge_with_amount)
6)  Verify wallet "type" matches payload wallet_type
7)  Verify wallet.crc_user_id matches the payload registration_id
8)  Verify payload recharge_amount equals response recharge_with_amount  (core validation)
9)  Verify auto-reload can be disabled (is_auto_reload_enabled=false)
10) Verify the recharge_with_amount updates when a different recharge_amount is sent

Negative Tests:
11) Verify missing registration_id is rejected
12) Verify missing wallet_type is rejected
13) Verify missing is_auto_reload_enabled is rejected
14) Verify missing threshold_amount is rejected
15) Verify missing recharge_amount is rejected
16) Verify negative threshold_amount is rejected
17) Verify negative recharge_amount is rejected
18) Verify non-boolean is_auto_reload_enabled is rejected
19) Verify non-existent registration_id is rejected
20) Verify GET method is not allowed
21) Verify PUT method is not allowed
22) Verify DELETE method is not allowed
"""

base_url = "http://qa-cloudmail-letters.internal.creditrepaircloud.com/api"
autoreload_endpoint = f"{base_url}/wallet/autoreload"

REGISTRATION_ID = 1001584
WALLET_TYPE = "cloudmail"
DEFAULT_THRESHOLD = 10
DEFAULT_RECHARGE = 15


def _autoreload_payload(
    is_enabled: bool = True,
    threshold: float = DEFAULT_THRESHOLD,
    recharge: float = DEFAULT_RECHARGE,
) -> dict:
    return {
        "registration_id": REGISTRATION_ID,
        "wallet_type": WALLET_TYPE,
        "is_auto_reload_enabled": is_enabled,
        "threshold_amount": threshold,
        "recharge_amount": recharge,
    }


# -------------------------------------------------------------------
# Positive Tests
# -------------------------------------------------------------------
def test_status_code_is_200(request_context):
    """Verify autoreload returns 200"""
    response = request_context.post(autoreload_endpoint, data=_autoreload_payload())
    assert response.status == 200


def test_response_status_is_success(request_context):
    """Verify response status is 'success'"""
    response = request_context.post(autoreload_endpoint, data=_autoreload_payload())
    data = response.json()
    assert data["status"] == "success"


def test_response_message(request_context):
    """Verify response message"""
    response = request_context.post(autoreload_endpoint, data=_autoreload_payload())
    data = response.json()
    assert data["message"] == "Wallet autoreload settings updated successfully"


def test_response_contains_wallet(request_context):
    """Verify response contains data.wallet"""
    response = request_context.post(autoreload_endpoint, data=_autoreload_payload())
    data = response.json()
    assert "data" in data
    assert "wallet" in data["data"]


def test_wallet_has_required_fields(request_context):
    """Verify the returned wallet contains all required fields"""
    response = request_context.post(autoreload_endpoint, data=_autoreload_payload())
    wallet = response.json()["data"]["wallet"]

    for field in ("id", "type", "crc_user_id", "balance", "recharge_with_amount"):
        assert field in wallet, f"Missing field: {field}"


def test_wallet_type_matches_payload(request_context):
    """Verify wallet 'type' matches payload wallet_type"""
    payload = _autoreload_payload()
    response = request_context.post(autoreload_endpoint, data=payload)
    wallet = response.json()["data"]["wallet"]
    assert wallet["type"] == payload["wallet_type"]


def test_request_id_matches_response_id(request_context):
    """Verify payload registration_id matches wallet.crc_user_id in the response"""
    payload = _autoreload_payload()
    response = request_context.post(autoreload_endpoint, data=payload)
    wallet = response.json()["data"]["wallet"]

    assert wallet["crc_user_id"] == payload["registration_id"], (
        f"crc_user_id mismatch: payload registration_id={payload['registration_id']}, "
        f"response crc_user_id={wallet['crc_user_id']}"
    )


def test_recharge_amount_matches_recharge_with_amount(request_context):
    """
    Core validation: payload.recharge_amount must equal
    response.data.wallet.recharge_with_amount.
    """
    payload = _autoreload_payload(recharge=DEFAULT_RECHARGE)
    response = request_context.post(autoreload_endpoint, data=payload)

    body = response.json()
    assert body["status"] == "success", f"Unexpected status: {body}"

    wallet = body["data"]["wallet"]
    print(f"\nPayload recharge_amount      : {payload['recharge_amount']}")
    print(f"Response recharge_with_amount: {wallet['recharge_with_amount']}")

    assert wallet["recharge_with_amount"] == payload["recharge_amount"], (
        f"recharge_amount mismatch: payload={payload['recharge_amount']}, "
        f"response recharge_with_amount={wallet['recharge_with_amount']}"
    )


def test_disable_auto_reload(request_context):
    """Verify auto-reload can be disabled (is_auto_reload_enabled=false)"""
    payload = _autoreload_payload(is_enabled=False)
    response = request_context.post(autoreload_endpoint, data=payload)

    body = response.json()
    assert body["status"] == "success", f"Unexpected status: {body}"


def test_recharge_with_amount_updates_when_changed(request_context):
    """Verify recharge_with_amount updates when a different recharge_amount is sent"""
    first_recharge = 25
    second_recharge = 40

    first_response = request_context.post(
        autoreload_endpoint, data=_autoreload_payload(recharge=first_recharge)
    )
    first_wallet = first_response.json()["data"]["wallet"]
    assert first_wallet["recharge_with_amount"] == first_recharge

    second_response = request_context.post(
        autoreload_endpoint, data=_autoreload_payload(recharge=second_recharge)
    )
    second_wallet = second_response.json()["data"]["wallet"]
    assert second_wallet["recharge_with_amount"] == second_recharge

    assert first_wallet["recharge_with_amount"] != second_wallet["recharge_with_amount"]


# -------------------------------------------------------------------
# Negative Tests
# -------------------------------------------------------------------
def test_missing_registration_id_rejected(request_context):
    """Verify request without registration_id is rejected"""
    payload = _autoreload_payload()
    payload.pop("registration_id")
    response = request_context.post(autoreload_endpoint, data=payload)
    body = response.json()

    assert body["status"] == "fail"
    assert body["code"] == "invalid_request"
    assert "registration_id" in body["message"]


def test_missing_wallet_type_rejected(request_context):
    """Verify request without wallet_type is rejected"""
    payload = _autoreload_payload()
    payload.pop("wallet_type")
    response = request_context.post(autoreload_endpoint, data=payload)
    body = response.json()

    assert body["status"] == "fail"
    assert body["code"] == "invalid_request"
    assert "wallet_type" in body["message"]


def test_missing_is_auto_reload_enabled_rejected(request_context):
    """Verify request without is_auto_reload_enabled is rejected"""
    payload = _autoreload_payload()
    payload.pop("is_auto_reload_enabled")
    response = request_context.post(autoreload_endpoint, data=payload)
    body = response.json()

    assert body["status"] == "fail"
    assert body["code"] == "invalid_request"
    assert "is_auto_reload_enabled" in body["message"]


def test_missing_threshold_amount_rejected(request_context):
    """Verify request without threshold_amount is rejected"""
    payload = _autoreload_payload()
    payload.pop("threshold_amount")
    response = request_context.post(autoreload_endpoint, data=payload)
    body = response.json()

    assert body["status"] == "fail"
    assert body["code"] == "invalid_request"
    assert "threshold_amount" in body["message"]


def test_missing_recharge_amount_rejected(request_context):
    """Verify request without recharge_amount is rejected"""
    payload = _autoreload_payload()
    payload.pop("recharge_amount")
    response = request_context.post(autoreload_endpoint, data=payload)
    body = response.json()

    assert body["status"] == "fail"
    assert body["code"] == "invalid_request"
    assert "recharge_amount" in body["message"]


def test_negative_threshold_amount_rejected(request_context):
    """Verify a negative threshold_amount is rejected"""
    response = request_context.post(
        autoreload_endpoint, data=_autoreload_payload(threshold=-10)
    )
    body = response.json()
    assert body["status"] != "success"


def test_negative_recharge_amount_rejected(request_context):
    """Verify a negative recharge_amount is rejected"""
    response = request_context.post(
        autoreload_endpoint, data=_autoreload_payload(recharge=-15)
    )
    body = response.json()
    assert body["status"] != "success"


def test_non_boolean_is_auto_reload_enabled_rejected(request_context):
    """Verify non-boolean is_auto_reload_enabled is rejected"""
    payload = _autoreload_payload()
    payload["is_auto_reload_enabled"] = "notabool"
    response = request_context.post(autoreload_endpoint, data=payload)
    body = response.json()
    assert body["status"] != "success"


def test_non_existent_registration_id_rejected(request_context):
    """Verify autoreload for a non-existent wallet is rejected"""
    payload = _autoreload_payload()
    payload["registration_id"] = 999999999
    response = request_context.post(autoreload_endpoint, data=payload)
    body = response.json()
    assert body["status"] != "success"


def test_get_method_not_allowed(request_context):
    """Verify GET method is not allowed"""
    response = request_context.get(autoreload_endpoint)
    assert response.status == 405


def test_put_method_not_allowed(request_context):
    """Verify PUT method is not allowed"""
    response = request_context.put(autoreload_endpoint)
    assert response.status == 405


def test_delete_method_not_allowed(request_context):
    """Verify DELETE method is not allowed"""
    response = request_context.delete(autoreload_endpoint)
    assert response.status == 405
