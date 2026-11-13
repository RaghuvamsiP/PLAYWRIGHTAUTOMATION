import pytest
from playwright.sync_api import APIRequestContext

from crc_automation.api.payloads.letter_library import build_letter_payload

LIBRARY_PATH = "/api/library"
PAGE_LIMIT = 20
LAST_PAGE = 8
CLIENT_ID = 93
AI_BUREAU_LETTER_PATH = f"/api/clients/{CLIENT_ID}/ai-letters/bureau"


@pytest.fixture(scope="module")
def ai_letters(auth_api: APIRequestContext) -> list[dict]:
    """Fetch Letter Library pages 1..8 and return every letter where isAILetter is true."""
    letters_found = []
    total_letters = 0

    for page in range(1, LAST_PAGE + 1):
        response = auth_api.get(
            LIBRARY_PATH,
            params={"page": page, "limit": PAGE_LIMIT},
        )
        assert response.ok, (
            f"Library API page {page} failed with status {response.status}: {response.text()}"
        )

        letters = response.json().get("list", [])
        page_ai = [letter for letter in letters if letter.get("isAILetter") is True]

        total_letters += len(letters)
        letters_found.extend(page_ai)
        print(f"\nPage {page}: {len(letters)} letters, {len(page_ai)} AI letters")

    print(f"\nTotal letters across {LAST_PAGE} pages: {total_letters}")
    print(f"Total AI letters (isAILetter = true): {len(letters_found)}")
    return letters_found


def test_letter_library_ai_letter_count(ai_letters: list[dict]):
    """Report the number of AI letters in the library."""
    ai_letter_ids = [letter["id"] for letter in ai_letters]
    print(f"\nAI letter IDs ({len(ai_letter_ids)}): {ai_letter_ids}")
    assert ai_letter_ids, "No AI letters found in the library"


def test_generate_ai_bureau_letters(auth_api: APIRequestContext, ai_letters: list[dict]):
    """POST each AI letter ID to the AI bureau letter API and collect IDs that did not return 200."""
    failed_ids = []

    for letter in ai_letters:
        letter_id = letter["id"]
        response = auth_api.post(
            AI_BUREAU_LETTER_PATH,
            data=build_letter_payload(letter_id),
        )
        print(f"\nLetter {letter_id} ({letter['title']}) -> {response.status}")
        if response.status != 200:
            print(f"  Response: {response.text()[:300]}")
            failed_ids.append(letter_id)

    print(f"\nAI letters checked: {len(ai_letters)}")
    print(f"IDs without a 200 response ({len(failed_ids)}): {failed_ids}")
    assert not failed_ids, f"AI letter IDs without a 200 response: {failed_ids}"
