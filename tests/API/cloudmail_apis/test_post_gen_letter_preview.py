"""
Letter preview generation test.

Loads 14 payloads from a single test-data file and POSTs each one
to the letter-preview endpoint.
"""

import json
from pathlib import Path

import pytest

LETTER_PREVIEW_URL = "http://qa-cloudmail-letters.internal.creditrepaircloud.com/api/letter/preview"

TEST_DATA_DIR = Path(__file__).resolve().parents[2] / "test_data" / "api"
PAYLOADS_FILE = TEST_DATA_DIR / "letter_preview_payloads.json"

with open(PAYLOADS_FILE, "r", encoding="utf-8") as _f:
    _PAYLOADS = json.load(_f)


@pytest.mark.parametrize("payload", _PAYLOADS)
def test_generate_letter_preview(request_context, payload):
    """POST to the letter preview endpoint and validate the response."""
    response = request_context.post(LETTER_PREVIEW_URL, data=payload)
    print(f"\nStatus  : {response.status} {response.status_text}")
    print(f"Body    : {response.text()}")

    assert response.ok, f"Request failed: {response.status} {response.status_text}"

    body = response.json()
    assert body.get("status") == "success", f"API returned non-success: {body}"
    assert body.get("message") == "Letter preview generated successfully.", (
        f"Unexpected message: {body.get('message')}"
    )

    data = body.get("data", {})
    page_count = data.get("page_count")
    letter_pdf_url = data.get("letter_pdf_url")

    assert isinstance(page_count, int) and page_count >= 1, (
        f"Expected page_count to be a positive int, got {page_count!r}"
    )
    assert isinstance(letter_pdf_url, str) and letter_pdf_url.startswith(
        "http://qa-cloudmail-letters.internal.creditrepaircloud.com/api/letter/preview/"
    ), f"Unexpected letter_pdf_url: {letter_pdf_url!r}"

    print(f"Page count     : {page_count}")
    print(f"Letter PDF URL : {letter_pdf_url}")
