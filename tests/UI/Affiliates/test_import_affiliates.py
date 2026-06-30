"""
Affiliate CSV Import — UI Automation
====================================
Flow under test (per requirement):
  1. Login to the application                       -> handled by the authenticated `page` fixture
  2. Click on the 'Affiliates' tab                  -> navigate_to_affiliates()
  3. Click on the 'Export/Import' button            -> open_import_dialog()
  4. Click on the 'Import' option                   -> open_import_dialog()
  5. Upload the CSV file & import it                 -> upload_csv() + submit_uploaded_csv()
  6. Close the dialog WITHOUT importing the records  -> close_import_dialog()

The operation is performed 2 times (parametrized: run 1 and run 2).

Auth note: the shared `page` fixture (root conftest) logs in via tests/auth.json,
created by utils/auth_helper.py. To run specifically as pdf@yopmail.com, update the
credentials in utils/auth_helper.py (and delete tests/auth.json so it regenerates).
"""

import os
import time

import allure
import pytest
from playwright.sync_api import Page, expect

from pages.affiliate_page import AffiliatePage

# CSV bundled with the repo so the test is self-contained.
CSV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "test_data", "ui", "my_affiliates_import.csv")
)


@pytest.fixture
def aff_page(page: Page) -> AffiliatePage:
    """Open the Affiliate Partners page (step 2)."""
    ap = AffiliatePage(page)
    ap.navigate_to_affiliates()
    return ap


@allure.feature("Affiliates")
@allure.story("CSV Import")
@allure.title("Import the CSV file and close (no record import) — run {run}")
@pytest.mark.ui
@pytest.mark.parametrize("run", [1, 2])
def test_import_csv_file_and_close(aff_page: AffiliatePage, run: int):
    """Upload + import the CSV file, then close the dialog without importing the records."""
    assert os.path.exists(CSV_PATH), f"CSV file not found: {CSV_PATH}"

    # Capture the time (in seconds) before execution
    start_time = time.time()
    print(f"\n[Run {run}] Start time: {start_time:.2f} seconds")

    # Steps 3 + 4: Export/Import -> Import
    aff_page.open_import_dialog()

    # Step 5: upload the CSV file and import it (opens the records preview)
    aff_page.upload_csv(CSV_PATH)
    expect(aff_page.import_dialog.get_by_text("my_affiliates_import.csv")).to_be_visible(timeout=10000)
    aff_page.submit_uploaded_csv()
    expect(aff_page.import_affiliates_button).to_be_visible()

    # Step 6: close the dialog WITHOUT importing the records
    aff_page.close_import_dialog()
    expect(aff_page.import_dialog).to_be_hidden()

    # Capture the time (in seconds) after execution and print the elapsed time
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"[Run {run}] End time:   {end_time:.2f} seconds")
    print(f"[Run {run}] Execution time: {elapsed:.2f} seconds")
    allure.attach(
        f"Start: {start_time:.2f}s\nEnd: {end_time:.2f}s\nElapsed: {elapsed:.2f}s",
        name=f"Execution Time (run {run})",
        attachment_type=allure.attachment_type.TEXT,
    )
