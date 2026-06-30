"""
Send Letter API tests.

POSTs to the send-letter endpoint and validates the response.
One test per combination of:
  - mail_type        ("firstclass", "certified")
  - color            (False / True  -> bw / color)
  - double_sided     (False / True  -> single / double sided)
  - return_envelope  (False / True  -> no / with return envelope)

Business rule: when mail_type == "certified" the response tracking_number
must NOT be null (USPS certified mail always carries a tracking number),
and the wallet amount sent must be > $6.
"""

import copy
import json
from pathlib import Path

SEND_LETTER_URL = "http://qa-cloudmail-letters.internal.creditrepaircloud.com/api/letter"

TEST_DATA_DIR = Path(__file__).resolve().parents[2] / "test_data" / "api"
BASE_PAYLOAD_FILE = TEST_DATA_DIR / "send_letter_payload.json"

with open(BASE_PAYLOAD_FILE, "r", encoding="utf-8") as _f:
    _BASE_PAYLOAD = json.load(_f)

# ──────────────────────────────────────────────────────────
# Tweakable per-run inputs — change here to retarget all tests
# ──────────────────────────────────────────────────────────
REGISTRATION_ID = 1001584
CLIENT_ID = 290

# Wallet amount sent with the request. Certified mail must be > $6
# (printing + USPS certified fee ≈ $6.64).
FIRSTCLASS_AMOUNT = 1.50
CERTIFIED_AMOUNT = 6.64


def _build_payload(color, double_sided, return_envelope, mail_type, amount):
    payload = copy.deepcopy(_BASE_PAYLOAD)
    payload["registration_id"] = REGISTRATION_ID
    payload["client_id"] = CLIENT_ID
    payload["color"] = color
    payload["double_sided"] = double_sided
    payload["return_envelope"] = return_envelope
    payload["mail_type"] = mail_type
    payload["amount"] = amount
    return payload


def _send_and_validate(request_context, color, double_sided, return_envelope, mail_type, amount):
    payload = _build_payload(color, double_sided, return_envelope, mail_type, amount)

    response = request_context.post(SEND_LETTER_URL, data=payload)
    print(
        f"\nVariant : color={color}, double_sided={double_sided}, "
        f"return_envelope={return_envelope}, mail_type={mail_type}, amount={amount}"
    )
    print(f"Status  : {response.status} {response.status_text}")
    print(f"Body    : {response.text()}")

    assert response.ok, f"Request failed: {response.status} {response.status_text}"

    body = response.json()
    assert body.get("status") == "success", f"API returned non-success: {body}"

    data = body.get("data") or {}
    letter_uuid = data.get("letter_uuid")
    tracking_number = data.get("tracking_number")

    assert letter_uuid, f"Expected non-empty letter_uuid, got {letter_uuid!r}"
    assert "tracking_number" in data, (
        f"tracking_number key missing from response data: {data}"
    )

    if mail_type == "certified":
        assert amount > 6, (
            f"Certified mail requires amount > 6, got {amount}"
        )
        assert tracking_number is not None and str(tracking_number).strip() != "", (
            f"Expected non-null tracking_number for mail_type='certified', "
            f"got {tracking_number!r}"
        )


# ──────────────────────────────────────────────────────────
# First-class · B&W
# ──────────────────────────────────────────────────────────
def test_send_letter_firstclass_bw_single_sided_no_return_envelope(request_context):
    _send_and_validate(request_context, color=False, double_sided=False, return_envelope=False, mail_type="firstclass", amount=FIRSTCLASS_AMOUNT)


def test_send_letter_firstclass_bw_single_sided_with_return_envelope(request_context):
    _send_and_validate(request_context, color=False, double_sided=False, return_envelope=True, mail_type="firstclass", amount=FIRSTCLASS_AMOUNT)


def test_send_letter_firstclass_bw_double_sided_no_return_envelope(request_context):
    _send_and_validate(request_context, color=False, double_sided=True, return_envelope=False, mail_type="firstclass", amount=FIRSTCLASS_AMOUNT)


def test_send_letter_firstclass_bw_double_sided_with_return_envelope(request_context):
    _send_and_validate(request_context, color=False, double_sided=True, return_envelope=True, mail_type="firstclass", amount=FIRSTCLASS_AMOUNT)


# ──────────────────────────────────────────────────────────
# First-class · Color
# ──────────────────────────────────────────────────────────
def test_send_letter_firstclass_color_single_sided_no_return_envelope(request_context):
    _send_and_validate(request_context, color=True, double_sided=False, return_envelope=False, mail_type="firstclass", amount=FIRSTCLASS_AMOUNT)


def test_send_letter_firstclass_color_single_sided_with_return_envelope(request_context):
    _send_and_validate(request_context, color=True, double_sided=False, return_envelope=True, mail_type="firstclass", amount=FIRSTCLASS_AMOUNT)


def test_send_letter_firstclass_color_double_sided_no_return_envelope(request_context):
    _send_and_validate(request_context, color=True, double_sided=True, return_envelope=False, mail_type="firstclass", amount=FIRSTCLASS_AMOUNT)


def test_send_letter_firstclass_color_double_sided_with_return_envelope(request_context):
    _send_and_validate(request_context, color=True, double_sided=True, return_envelope=True, mail_type="firstclass", amount=FIRSTCLASS_AMOUNT)


# ──────────────────────────────────────────────────────────
# Certified · B&W
# ──────────────────────────────────────────────────────────
def test_send_letter_certified_bw_single_sided_no_return_envelope(request_context):
    _send_and_validate(request_context, color=False, double_sided=False, return_envelope=False, mail_type="certified", amount=CERTIFIED_AMOUNT)


def test_send_letter_certified_bw_single_sided_with_return_envelope(request_context):
    _send_and_validate(request_context, color=False, double_sided=False, return_envelope=True, mail_type="certified", amount=CERTIFIED_AMOUNT)


def test_send_letter_certified_bw_double_sided_no_return_envelope(request_context):
    _send_and_validate(request_context, color=False, double_sided=True, return_envelope=False, mail_type="certified", amount=CERTIFIED_AMOUNT)


def test_send_letter_certified_bw_double_sided_with_return_envelope(request_context):
    _send_and_validate(request_context, color=False, double_sided=True, return_envelope=True, mail_type="certified", amount=CERTIFIED_AMOUNT)


# ──────────────────────────────────────────────────────────
# Certified · Color
# ──────────────────────────────────────────────────────────
def test_send_letter_certified_color_single_sided_no_return_envelope(request_context):
    _send_and_validate(request_context, color=True, double_sided=False, return_envelope=False, mail_type="certified", amount=CERTIFIED_AMOUNT)


def test_send_letter_certified_color_single_sided_with_return_envelope(request_context):
    _send_and_validate(request_context, color=True, double_sided=False, return_envelope=True, mail_type="certified", amount=CERTIFIED_AMOUNT)


def test_send_letter_certified_color_double_sided_no_return_envelope(request_context):
    _send_and_validate(request_context, color=True, double_sided=True, return_envelope=False, mail_type="certified", amount=CERTIFIED_AMOUNT)


def test_send_letter_certified_color_double_sided_with_return_envelope(request_context):
    _send_and_validate(request_context, color=True, double_sided=True, return_envelope=True, mail_type="certified", amount=CERTIFIED_AMOUNT)
