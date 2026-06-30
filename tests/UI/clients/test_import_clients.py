"""
Clients CSV Import — UI Automation
==================================
Flow under test (per requirement):
  1. Login to the application                       -> handled by the authenticated `page` fixture
  2. Click on the 'Clients' tab                     -> navigate_to_clients()
  3. Click on the 'Import/Export' button            -> open_import_dialog()
  4. Choose 'Import'                                -> open_import_dialog()
  5. Import the CSV file and close                  -> upload_csv() + submit_uploaded_csv() + close_import_dialog()
                                                       (does NOT import the records in the CSV)
  6. Run 2 times                                    -> parametrized: run 1 and run 2
  7. Capture the execution time for both runs       -> printed per run

Auth note: the shared `page` fixture (root conftest) logs in via tests/auth.json,
created by utils/auth_helper.py.
"""

import os
import time

import allure
import pytest
from playwright.sync_api import Page, expect

from pages.create_client_page import CreateClientPage

# CSV bundled with the repo so the test is self-contained.
CSV_NAME = "3 clients.csv"
CSV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "test_data", "ui", CSV_NAME)
)


@pytest.fixture
def clients_page(page: Page) -> CreateClientPage:
    """Open the Clients page (step 2)."""
    cp = CreateClientPage(page)
    cp.navigate_to_clients()
    expect(cp.clients_heading).to_be_visible(timeout=15000)
    return cp


@allure.feature("Clients")
@allure.story("CSV Import")
@allure.title("Import the CSV file and close (no record import) — run {run}")
@pytest.mark.ui
@pytest.mark.parametrize("run", [1, 2])
def test_import_csv_file_and_close(clients_page: CreateClientPage, run: int):
    """Upload + import the CSV file, then close the dialog without importing the records."""
    assert os.path.exists(CSV_PATH), f"CSV file not found: {CSV_PATH}"

    # Capture the time (in seconds) before execution
    start_time = time.time()
    print(f"\n[Run {run}] Start time: {start_time:.2f} seconds")

    # Steps 3 + 4: Import/Export -> Import
    clients_page.open_import_dialog()

    # Step 5: upload the CSV file and import it (opens the records preview)
    clients_page.upload_csv(CSV_PATH)
    expect(clients_page.import_dialog.get_by_text(CSV_NAME)).to_be_visible(timeout=10000)
    clients_page.submit_uploaded_csv()
    expect(clients_page.import_clients_button).to_be_visible()

    # ...then close the dialog WITHOUT importing the records
    clients_page.close_import_dialog()
    expect(clients_page.import_dialog).to_be_hidden()

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
