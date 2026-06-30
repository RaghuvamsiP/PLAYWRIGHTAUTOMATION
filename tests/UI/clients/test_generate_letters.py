"""
Test: Generate Dispute Letters and Send via First Class Mail
============================================================
E2E workflow:
  1. Login with pdf@yopmail.com / P@ssw0rd
  2. Click on first client in the clients list
  3. Click on 'Generate Letters' tab
  4. Choose 'Round 1 Basic Dispute' radio button
  5. Click 'New Dispute Item'
  6. Select all bureaus, select reason, and save
  7. Click 'Generate Library Letter' button
  8. Click 'Save & Continue To Print'
  9. Click 'Save All {x} Letters' → redirects to 'Send Letters' tab
  10. Select last letter and click 'Next'
  11. Click 'Attach Additional Documents' accordion
  12. Click 'Upload New' and upload a PDF file
  13. Click 'Next'
  14. Choose 'First Class Mail' and click 'Next'
  15. Click 'Submit Order' → Confirm Order modal → Submit again
      → Wait for 'Submitting Cloud Mail Order' (3 loading steps)
      → 'Order Submitted!' modal → Click 'View Letter Statuses'
      → Redirects to Letters & Status tab
"""

import os

import allure
import pytest
from playwright.sync_api import Page, expect

from pages.generate_letters_page import GenerateLettersPage
from config.urls import AppURLs

# Resolve the PDF path relative to the project root
PDF_FILE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "test_data", "test_document.pdf"
)


@allure.feature("Generate Letters")
@allure.story("Dispute Letter E2E — Round 1 Basic Dispute via First Class Mail")
@allure.title("Generate dispute letter for first client and send via first class mail")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.regression
def test_generate_and_send_dispute_letter(pdf_user_page: Page):
    """
    Full E2E: login → first client → generate Round 1 Basic Dispute letter
    → add dispute item → generate library letter → save → send via first class mail.
    """
    page = pdf_user_page
    gl = GenerateLettersPage(page)

    # ── Step 1: Navigate to Clients list ─────────────────────
    with allure.step("Step 1: Navigate to clients list"):
        gl.navigate_to_clients()
        page.wait_for_load_state("networkidle", timeout=30000)

    # ── Step 2: Click on first client ────────────────────────
    with allure.step("Step 2: Click on first client in the list"):
        gl.click_first_client()
        page.wait_for_url("**/clients/*/dashboard", timeout=15000)

    # ── Step 3: Click on 'Generate Letters' tab ──────────────
    with allure.step("Step 3: Click on 'Generate Letters' tab"):
        gl.click_generate_letters_tab()
        page.wait_for_url("**/generate-letters**", timeout=15000)

    # ── Step 4: Choose 'Round 1 Basic Dispute' radio button ──
    with allure.step("Step 4: Select 'Round 1 Basic Dispute' radio button"):
        gl.select_round1_basic_dispute()

    # ── Step 5: Click 'New Dispute Item' ─────────────────────
    with allure.step("Step 5: Click 'New Dispute Item' button"):
        gl.click_new_dispute_item()

    # ── Step 6: Select all bureaus, select reason, and save ──
    with allure.step("Step 6: Select all bureaus and reason, then save"):
        gl.select_all_bureaus()
        gl.select_reason()
        gl.save_dispute_item()

    # ── Step 7: Click 'Generate Library Letter' ────────────────
    with allure.step("Step 7: Click 'Generate Library Letter' button"):
        gl.click_generate_library_letter()

    # ── Step 8: Click 'Save and Continue to Print' ───────────
    with allure.step("Step 8: Click 'Save and Continue to Print'"):
        gl.click_save_and_continue_to_print()

    # ── Step 9: Click 'Save All {x} Letters' ─────────────────
    with allure.step("Step 9: Click 'Save All Letters' and verify redirect to Send Letters tab"):
        gl.click_save_all_letters()
        gl.verify_on_send_letters_tab()

    # ── Step 10: Select last letter and click 'Next' ─────────
    with allure.step("Step 10: Select last letter and click 'Next'"):
        gl.select_last_letter()
        gl.click_next()

    # ── Step 11: Click 'Attach Additional Documents' ─────────
    with allure.step("Step 11: Expand 'Attach Additional Documents' accordion"):
        gl.click_attach_additional_documents()

    # ── Step 12: Upload a PDF file ───────────────────────────
    with allure.step("Step 12: Upload PDF file"):
        pdf_path = os.path.abspath(PDF_FILE_PATH)
        assert os.path.exists(pdf_path), f"Test PDF not found at: {pdf_path}"
        gl.upload_pdf(pdf_path)

    # ── Step 13: Click 'Next' ────────────────────────────────
    with allure.step("Step 13: Click 'Next' after attaching documents"):
        gl.click_next()

    # ── Step 14: Choose 'First Class Mail' and click 'Next' ──
    with allure.step("Step 14: Select 'First Class Mail' and click 'Next'"):
        gl.select_first_class_mail()
        gl.click_next()

    # ── Step 15: Click 'Submit Order' and complete submission ─
    with allure.step("Step 15: Click 'Submit Order' to send the letter"):
        gl.click_submit_order()

    with allure.step("Step 15a: Confirm order in the confirmation modal"):
        gl.confirm_order()

    with allure.step("Step 15b: Wait for Cloud Mail submission to complete"):
        gl.wait_for_cloud_mail_submission()

    with allure.step("Step 15c: Click 'View Letter Statuses' and verify redirect"):
        gl.click_view_letter_statuses()
        gl.verify_on_letters_status_tab()
