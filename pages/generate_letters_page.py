import re

import allure
from playwright.sync_api import Page, expect

from pages.base_page import BasePage
from config.urls import AppURLs


class GenerateLettersPage(BasePage):
    """Page object for the Generate Letters / Send Letters workflow on a client's profile."""

    def __init__(self, page: Page):
        super().__init__(page)

    # ─── Clients List ────────────────────────────────────────

    @allure.step("Navigate to clients list")
    def navigate_to_clients(self):
        self.navigate(AppURLs.Clients.LIST)

    @allure.step("Click on first client in the list")
    def click_first_client(self):
        # Client names are links inside a grid role-based table
        first_client = self.page.locator("div[role='grid'] a").first
        first_client.wait_for(state="visible", timeout=15000)
        first_client.click()
        self.page.wait_for_load_state("domcontentloaded")

    # ─── Generate Letters Tab ────────────────────────────────

    @allure.step("Click on 'Generate Letters' tab")
    def click_generate_letters_tab(self):
        tab = self.page.get_by_role("tab", name="Generate Letters")
        tab.wait_for(state="visible", timeout=15000)
        tab.click()
        self.page.wait_for_load_state("domcontentloaded")

    # ─── Step 1: Choose Dispute Round ────────────────────────

    @allure.step("Select 'Round 1 Basic Dispute' radio button")
    def select_round1_basic_dispute(self):
        radio = self.page.get_by_role("radio", name="Round 1 Basic Dispute")
        radio.wait_for(state="visible", timeout=10000)
        radio.click()

    # ─── New Dispute Item ────────────────────────────────────

    @allure.step("Click 'New Dispute Item' button")
    def click_new_dispute_item(self):
        btn = self.page.get_by_role("button", name="New Dispute Item")
        btn.wait_for(state="visible", timeout=10000)
        btn.click()
        # Wait for the "Add New Dispute Items" dialog to appear
        dialog = self.page.locator("div[role='dialog']")
        expect(dialog).to_be_visible(timeout=10000)

    @allure.step("Select all bureaus")
    def select_all_bureaus(self):
        for bureau in ["Equifax", "Experian", "Transunion"]:
            checkbox = self.page.get_by_role("checkbox", name=bureau)
            if not checkbox.is_checked():
                checkbox.check()

    @allure.step("Select dispute reason")
    def select_reason(self):
        reason_field = self.page.get_by_role("combobox", name="Reason*")
        reason_field.click()
        # Select the first real option (skip placeholder "Select a reason for your dispute")
        options = self.page.get_by_role("option")
        options.nth(1).click()

    @allure.step("Click 'Add to Dispute' to save dispute item")
    def save_dispute_item(self):
        btn = self.page.get_by_role("button", name="Add to Dispute")
        btn.click()
        # Wait for dialog to close
        dialog = self.page.locator("div[role='dialog']")
        expect(dialog).to_be_hidden(timeout=10000)

    # ─── Generate Library Letter ─────────────────────────────

    @allure.step("Click 'Generate Library Letter' button")
    def click_generate_library_letter(self):
        btn = self.page.get_by_role("button", name="Generate Library Letter")
        btn.wait_for(state="visible", timeout=10000)
        btn.click()
        # The letter editor loads dynamically (SPA) — wait for the save button to confirm it rendered
        self.page.get_by_role("button", name="Save & Continue To Print").wait_for(
            state="visible", timeout=30000
        )

    @allure.step("Click 'Save & Continue To Print'")
    def click_save_and_continue_to_print(self):
        btn = self.page.get_by_role("button", name="Save & Continue To Print")
        btn.wait_for(state="visible", timeout=15000)
        btn.click()
        self.page.wait_for_load_state("domcontentloaded")

    # ─── Save All Letters ────────────────────────────────────

    @allure.step("Click 'Save All Letters' button")
    def click_save_all_letters(self):
        # The "Save Letter" dialog appears with a dynamic button: "Save All {x} Letters"
        btn = self.page.get_by_role("button", name=re.compile(r"Save All \d+ Letters"))
        btn.wait_for(state="visible", timeout=15000)
        btn.click()
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("Verify redirected to 'Send Letters' tab")
    def verify_on_send_letters_tab(self):
        self.page.wait_for_url("**/send-letters", timeout=15000)
        send_tab = self.page.get_by_role("tab", name="Send Letters")
        expect(send_tab).to_have_attribute("aria-selected", "true", timeout=15000)

    # ─── Send Letters Flow ───────────────────────────────────

    @allure.step("Select last letter in the list")
    def select_last_letter(self):
        # Letters are in a grid with checkboxes labeled "Select row"
        checkboxes = self.page.get_by_role("checkbox", name="Select row")
        checkboxes.last.wait_for(state="visible", timeout=10000)
        if not checkboxes.last.is_checked():
            checkboxes.last.check()

    @allure.step("Click 'Next' button")
    def click_next(self):
        btn = self.page.get_by_role("button", name="Next")
        btn.wait_for(state="visible", timeout=10000)
        btn.click()
        self.page.wait_for_timeout(2000)

    # ─── Attach Additional Documents ─────────────────────────

    @allure.step("Click 'Attach Additional Documents' accordion")
    def click_attach_additional_documents(self):
        accordion = self.page.get_by_role("button", name="Attach Additional Documents")
        accordion.wait_for(state="visible", timeout=10000)
        accordion.click()
        self.page.wait_for_timeout(1000)

    @allure.step("Click 'Upload New' for selected letter and upload PDF file")
    def upload_pdf(self, file_path: str):
        # Target the "Upload New" button inside the accordion's letter grid row,
        # NOT the Photo ID or Proof of Address upload buttons above.
        accordion_region = self.page.locator("region")
        upload_btn = accordion_region.get_by_role("button", name="Upload New")
        upload_btn.wait_for(state="visible", timeout=10000)
        upload_btn.click()

        # "Upload New Document" dialog opens with a hidden input#choose-file
        dialog = self.page.locator("div[role='dialog']")
        expect(dialog).to_be_visible(timeout=10000)

        file_input = self.page.locator("input#choose-file")
        file_input.set_input_files(file_path)

        # Wait for file to be attached, then click "Upload Document(s)"
        self.page.wait_for_timeout(2000)
        upload_docs_btn = dialog.get_by_role("button", name="Upload Document(s)")
        upload_docs_btn.wait_for(state="visible", timeout=10000)
        upload_docs_btn.click()

        # Wait for upload to complete and dialog to close
        expect(dialog).to_be_hidden(timeout=15000)

    # ─── Mailing Options ─────────────────────────────────────

    @allure.step("Select 'First Class Mail' option")
    def select_first_class_mail(self):
        card = self.page.get_by_text("First Class Mail", exact=False).first
        card.wait_for(state="visible", timeout=10000)
        card.click()

    # ─── Submit Order ────────────────────────────────────────

    @allure.step("Click 'Submit Order' button")
    def click_submit_order(self):
        btn = self.page.get_by_role("button", name="Submit Order")
        btn.wait_for(state="visible", timeout=10000)
        btn.click()

    @allure.step("Confirm order in the confirmation modal")
    def confirm_order(self):
        # "Confirm Order" modal appears — click "Submit Order" again to confirm
        dialog = self.page.locator("div[role='dialog']")
        expect(dialog).to_be_visible(timeout=10000)
        confirm_btn = dialog.get_by_role("button", name="Submit Order")
        confirm_btn.wait_for(state="visible", timeout=10000)
        confirm_btn.click()

    @allure.step("Wait for 'Submitting Cloud Mail Order' to complete")
    def wait_for_cloud_mail_submission(self):
        # "Submitting Cloud Mail Order" modal shows 3 loading steps
        # Wait until the "Order Submitted!" text appears
        self.page.get_by_text("Order Submitted!").wait_for(state="visible", timeout=60000)

    @allure.step("Click 'View Letter Statuses' button")
    def click_view_letter_statuses(self):
        btn = self.page.get_by_role("button", name="View Letter Statuses")
        btn.wait_for(state="visible", timeout=10000)
        btn.click()
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("Verify redirected to 'Letters & Status' tab")
    def verify_on_letters_status_tab(self):
        self.page.wait_for_url("**/letters-status**", timeout=15000)
        status_tab = self.page.get_by_role("tab", name="Letters & Status")
        expect(status_tab).to_have_attribute("aria-selected", "true", timeout=15000)
