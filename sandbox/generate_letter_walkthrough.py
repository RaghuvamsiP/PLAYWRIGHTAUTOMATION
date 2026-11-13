"""
Test: Create a new client and generate a Round 1 (RD1) dispute letter.

Steps:
  1. Login and navigate to Home
  2. Create a new client with first name, last name, email, and address
  3. Navigate to 'Generate Letters' tab
  4. Generate a Default Round 1 (RD1) letter with no dispute items
"""

import time
import pytest
from playwright.sync_api import Page, expect


def unique_email(prefix: str = "autotest_rd1") -> str:
    return f"{prefix}_{int(time.time())}@yopmail.com"


@pytest.fixture
def client_dashboard(page: Page):
    """Create a new client from Home page and land on the client dashboard."""
    # Navigate to Home
    page.goto("https://qa.creditrepaircloud.com/app/home", wait_until="domcontentloaded", timeout=60000)
    expect(page.get_by_text("Hello, Credit Hero!")).to_be_visible(timeout=60000)

    # Open Add Lead/Client dialog
    page.get_by_text("Add New Client").click()
    dialog = page.locator("div[role='dialog']")
    expect(dialog).to_be_visible(timeout=15000)

    # Fill required fields
    email = unique_email()
    page.get_by_label("First Name*").fill("AutoTest")
    page.get_by_label("Last Name*").fill("GenLetter")
    page.get_by_label("Email Address (Necessary for Onboarding)").fill(email)

    # Fill address
    page.get_by_label("Mailing Address").fill("123 Main Street")
    page.get_by_label("City", exact=True).fill("Los Angeles")
    page.get_by_label("Zip Code", exact=True).fill("90066")

    # Select State
    page.get_by_role("combobox", name="State").click()
    page.get_by_role("combobox", name="State").fill("California")
    page.get_by_role("option", name="California").click()

    # Turn off portal access to avoid Agreement dependency
    portal_toggle = page.get_by_label("Off / On (Recommended)")
    if portal_toggle.is_checked():
        portal_toggle.uncheck()

    # Submit the form
    dialog.get_by_role("button", name="Add Lead/Client").click()

    # Handle "Save Profile?" confirmation (missing SSN warning)
    try:
        page.get_by_role("button", name="Save").click(timeout=5000)
    except Exception:
        pass

    # Verify success toaster
    toaster = page.locator(".MuiAlert-message:visible")
    expect(toaster).to_have_text("Client profile added successfully", timeout=15000)

    # Should be on client dashboard now
    page.wait_for_url("**/clients/*/dashboard", timeout=15000)
    return page


def test_create_client_and_generate_rd1_letter(client_dashboard: Page):
    """Create a client, navigate to Generate Letters, and generate a Round 1 (RD1) letter."""
    page = client_dashboard

    # Step 1: Click on "3 Generate Letters" tab
    page.get_by_role("tab", name="Generate Letters").click()
    page.wait_for_url("**/generate-letters", timeout=15000)

    # Step 2: Click "Generate a letter (with no dispute items)"
    page.get_by_text("Generate a letter (with no dispute items)").click()
    expect(page.get_by_text("Choose a Letter (No Dispute Items)")).to_be_visible(timeout=10000)

    # Step 3: Select Letter Category = "All"
    page.get_by_role("combobox", name="Letter Category*").click()
    page.get_by_role("option", name="All").click()

    # Step 4: Select Letter Name = "Default Round 1 (Dispute Credit Report Items)"
    page.get_by_role("combobox", name="Letter Name*").click()
    page.get_by_role("combobox", name="Letter Name*").fill("Round 1")
    page.get_by_role("option", name="Default Round 1 (Dispute Credit Report Items)").click()

    # Step 5: Fill To Address (Experian bureau address)
    page.get_by_role("textbox", name="Company Name").fill("Experian")
    page.get_by_role("combobox", name="Address").fill("P.O. Box 4500")
    page.keyboard.press("Escape")  # close auto-suggest if any

    # City, State, Zip in the To Address section
    city_input = page.locator("#outlined-basic").nth(2)
    zip_input = page.locator("#outlined-basic").nth(3)
    city_input.fill("Allen")
    zip_input.fill("75013")

    page.get_by_role("combobox", name="State*").click()
    page.get_by_role("combobox", name="State*").fill("Texas")
    page.get_by_role("option", name="Texas").click()

    # Step 6: Click "Generate Library Letter"
    page.get_by_role("button", name="Generate Library Letter").click()

    # Verify letter was generated — page should navigate to Send Letters or show success
    page.wait_for_url("**/send-letters**", timeout=30000)
    print("RD1 letter generated successfully!")
