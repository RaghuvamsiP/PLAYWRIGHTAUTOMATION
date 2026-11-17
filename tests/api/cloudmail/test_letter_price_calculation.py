"""
Letter price calculation test.

Calls the letter-pricing POST endpoint and validates that the price
returned by the API matches the expected value computed from the
fixed Lob (printing) + USPS (mailing) fee tables.
"""

import pytest

# ──────────────────────────────────────────────────────────
# Fixed pricing constants (from the pricing UI)
# ──────────────────────────────────────────────────────────
# Printing fees (Lob) — per page
PRINTING_FEES = {
    "bw":    {"first_page": 0.00, "additional": 0.12, "seven_plus_extra": 2.35},
    "color": {"first_page": 0.00, "additional": 0.24, "seven_plus_extra": 2.35},
}

# Mailing fees (USPS) — flat per letter
MAILING_FEES = {
    "firstclass": {"bw": 1.01, "color": 1.20},
    "certified":  {"bw": 6.64, "color": 6.64},
}


def calculate_letter_price(payload: dict) -> float:
    """
    Rules:
      - side_type == "double"  → page_count is multiplied by 2
      - 1st page is free
      - Pages 2..N billed at the "additional" per-page rate
        ($0.12 B&W, $0.24 Color)
      - If final page count > 7 → add a flat $2.35 extra
      - Mailing fee is a flat fee based on letter_type + color
    """
    pages = payload["page_count"]
    if payload["side_type"].lower() == "double":
        pages *= 2

    color_key = "color" if payload["color"] else "bw"
    letter_type = payload["letter_type"].lower()

    fees = PRINTING_FEES[color_key]

    # 1st page free; remaining pages at the additional rate
    printing = max(pages - 1, 0) * fees["additional"]

    # Extra flat fee when page count exceeds 7
    if pages > 7:
        printing += fees["seven_plus_extra"]

    mailing = MAILING_FEES[letter_type][color_key]

    return round(printing + mailing, 2)


# ──────────────────────────────────────────────────────────
# Endpoint
# ──────────────────────────────────────────────────────────
LETTER_PRICE_URL = "http://qa-cloudmail-letters.internal.creditrepaircloud.com/api/letter/price"


# ──────────────────────────────────────────────────────────
# Test cases
# ──────────────────────────────────────────────────────────
@pytest.mark.parametrize("payload", [
    # 5 pages, certified, color, single → 4 × $0.24 + $6.64 = $7.60
    {"page_count": 1, "letter_type": "firstclass", "color": False, "side_type": "single"},
])
def test_letter_price(request_context, payload):
    """POST to the pricing endpoint and validate the returned price."""
    expected = calculate_letter_price(payload)

    response = request_context.post(LETTER_PRICE_URL, data=payload)
    print(f"\nPayload : {payload}")
    print(f"Status  : {response.status} {response.status_text}")
    print(f"Body    : {response.text()}")

    assert response.ok, f"Request failed: {response.status} {response.status_text}"

    body = response.json()
    assert body.get("status") == "success", f"API returned non-success: {body}"

    actual = float(body["data"]["letter_price"])
    print(f"Expected: ${expected}")
    print(f"Actual  : ${actual}")

    assert actual == expected, (
        f"Price mismatch for {payload}: expected ${expected}, got ${actual}"
    )


# ──────────────────────────────────────────────────────────
# Permutation / combination payloads
# page_count × letter_type × color × side_type
# ──────────────────────────────────────────────────────────
PAGE_COUNTS = [1, 3, 7, 8]
LETTER_TYPES = ["firstclass", "certified"]
COLORS = [False, True]
SIDE_TYPES = ["single", "double"]

PERMUTATION_PAYLOADS = [
    {
        "page_count": pc,
        "letter_type": lt,
        "color": c,
        "side_type": st,
    }
    for pc in PAGE_COUNTS
    for lt in LETTER_TYPES
    for c in COLORS
    for st in SIDE_TYPES
]


@pytest.mark.parametrize("payload", PERMUTATION_PAYLOADS)
def test_letter_price_calculation_only(payload):
    """Compute and print the expected letter price for each payload permutation."""
    expected = calculate_letter_price(payload)
    print(f"\nPayload : {payload}")
    print(f"Price   : ${expected}")


# ──────────────────────────────────────────────────────────
# Edge case: page_count = 0
# ──────────────────────────────────────────────────────────
def test_letter_price_zero_pages(request_context):
    """
    A letter with 0 pages is invalid. The API is expected to reject it
    with a structured validation error:
        {
          "status": "fail",
          "code":   "invalid_request",
          "message": {"page_count": ["The page count must be at least 1."]}
        }
    """
    payload = {
        "page_count": 0,
        "letter_type": "firstclass",
        "color": False,
        "side_type": "single",
    }

    response = request_context.post(LETTER_PRICE_URL, data=payload)
    body = response.json()

    print(f"\nPayload : {payload}")
    print(f"Status  : {response.status} {response.status_text}")
    print(f"Body    : {body}")

    assert body.get("status") == "fail", f"Expected status='fail', got {body.get('status')}"
    assert body.get("code") == "invalid_request", (
        f"Expected code='invalid_request', got {body.get('code')}"
    )
    assert body.get("message", {}).get("page_count") == [
        "The page count must be at least 1."
    ], f"Unexpected page_count error message: {body.get('message')}"
