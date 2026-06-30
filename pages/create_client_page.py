from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from config.urls import AppURLs


class CreateClientPage(BasePage):
    """Page object for the Add Lead/Client dialog on the Clients page."""

    # All available statuses in the Status dropdown
    STATUSES = ["Lead", "Prospect", "Lead/Inactive", "Client", "Inactive", "Suspended", "Custom status 1"]

    def __init__(self, page: Page):
        super().__init__(page)

        # -- Dialog --
        self.dialog = page.locator("div[role='dialog']")
        self.dialog_heading = page.get_by_role("heading", name="Add Lead/Client")
        self.close_dialog_button = self.dialog.locator("button").first

        # -- Personal Information --
        self.first_name = page.get_by_label("First Name*")
        self.middle_name = page.get_by_label("Middle Name")
        self.last_name = page.get_by_label("Last Name*")
        self.suffix = page.get_by_label("Suffix")
        self.email_address = page.get_by_label("Email Address (Necessary for Onboarding)")
        self.ssn_last4 = page.get_by_label("Last 4 of SSN")
        self.date_of_birth = page.get_by_label("Date of Birth")
        self.dob_date_picker = page.get_by_role("button", name="Choose date")

        # -- Checkboxes --
        self.no_email_checkbox = page.get_by_label("Doesn't have email address (Not recommended)")
        self.previous_address_checkbox = page.get_by_label("Previous address (If at current address less than 2 years)")

        # -- Current Address --
        self.mailing_address = page.get_by_label("Mailing Address", exact=True)
        self.apt_suite = page.get_by_label("Apt., suite, or unit (optional)", exact=True)
        self.city = page.get_by_label("City", exact=True)
        self.state = page.get_by_label("State", exact=True)
        self.zip_code = page.get_by_label("Zip Code", exact=True)
        self.country = page.get_by_label("Country", exact=True)

        # -- Previous Address (visible after checking the previous address checkbox) --
        self.prev_mailing_address = page.get_by_label("Previous Mailing Address")
        self.prev_apt_suite = page.get_by_label("Previous Apt., suite, or unit (optional)")
        self.prev_city = page.get_by_label("Previous City")
        self.prev_state = page.get_by_label("Previous State")
        self.prev_zip_code = page.get_by_label("Previous Zip Code")
        self.prev_country = page.get_by_label("Previous Country")

        # -- Phone Fields --
        self.phone_mobile = page.get_by_label("Phone (Mobile)")
        self.phone_alternate = page.get_by_label("Phone (Alternate)")
        self.phone_work = page.get_by_label("Phone (Work)")
        self.fax = page.get_by_label("Fax")

        # -- Status Section --
        self.status_dropdown = page.get_by_role("combobox", name="Status")
        self.start_date = page.get_by_label("Start Date")
        self.assigned_to = page.get_by_label("Assigned To")
        self.referred_by = page.get_by_label("Referred By")

        # Statuses where portal access should NOT be enabled
        self.NO_PORTAL_STATUSES = ["Lead", "Prospect", "Lead/Inactive", "Inactive", "Suspended"]
        # Statuses where portal access auto-enables
        self.PORTAL_STATUSES = ["Client", "Custom status 1"]

        # -- Portal Access Toggle --
        self.portal_access_toggle = page.get_by_label("Off / On (Recommended)")
        self.portal_access_info_icon = page.get_by_test_id("InfoIcon")

        # -- Action Buttons --
        self.cancel_button = self.dialog.get_by_role("button", name="Cancel")
        self.submit_button = self.dialog.get_by_role("button", name="Add Lead/Client")

        # -- Toaster --
        self.toaster = page.locator(".MuiAlert-message:visible")

        # -- Confirmation Dialog --
        self.confirm_dialog = page.locator("div[role='dialog']").nth(1)
        self.confirm_save_button = page.locator("button[type='button']", has_text="Save")

        # -- Google Places Auto-suggest --
        self.pac_container = page.locator(".pac-container:visible")
        self.pac_items = page.locator(".pac-container:visible .pac-item")

        # -- Clients Page --
        self.add_client_link = page.get_by_role("link", name="Add Lead / Client")
        self.clients_heading = page.get_by_role("heading", name="Clients")

        # -- Import / Export --
        self.import_export_button = page.get_by_role("button", name="Import/Export")
        self.export_menu_item = page.get_by_role("menuitem", name="Export")
        self.import_menu_item = page.get_by_role("menuitem", name="Import")

        # Step 1 dialog: choose & upload a CSV file
        self.import_dialog = page.get_by_role("dialog", name="Import Clients From CSV File")
        self.choose_file_button = self.import_dialog.get_by_role("button", name="Choose File")
        self.import_file_input = self.import_dialog.locator("input#choose-file[type='file']")
        self.import_upload_button = self.import_dialog.get_by_role("button", name="Import", exact=True)

        # Step 2 dialog: map fields, pick records and confirm
        self.import_as_lead_radio = self.import_dialog.get_by_role("radio", name="Import All as Lead")
        self.import_as_active_radio = self.import_dialog.get_by_role("radio", name="Import All as Active Client")
        self.import_as_inactive_radio = self.import_dialog.get_by_role("radio", name="Import All as Inactive Client")
        self.import_clients_button = self.import_dialog.get_by_role("button", name="Import Clients")
        self.import_cancel_button = self.import_dialog.get_by_role("button", name="Cancel")

    # ─── Navigation ───────────────────────────────────────────

    def navigate_to_clients(self):
        self.navigate(AppURLs.Clients.LIST)

    def navigate_to_home(self):
        self.navigate(AppURLs.Auth.HOME)

    def open_add_client_dialog(self):
        """Open the Add Lead/Client dialog from the Clients list page."""
        self.add_client_link.wait_for(state="visible", timeout=15000)
        self.add_client_link.click()
        expect(self.dialog).to_be_visible(timeout=15000)

    def open_add_client_from_home(self):
        """Open the Add Lead/Client dialog from the Home page (more reliable)."""
        self.page.get_by_text("Add New Client").click()
        expect(self.dialog).to_be_visible(timeout=15000)

    # ─── Import / Export CSV ──────────────────────────────────

    def open_import_dialog(self):
        """Click Import/Export → Import to open the 'Import Clients From CSV File' dialog."""
        self.import_export_button.click()
        self.import_menu_item.click()
        expect(self.import_dialog).to_be_visible(timeout=10000)

    def upload_csv(self, file_path: str):
        """Attach a CSV to the import dialog's file input."""
        self.import_file_input.set_input_files(file_path)
        # The chosen file name + the 'Import' button should now be shown
        expect(self.import_upload_button).to_be_visible(timeout=10000)

    def submit_uploaded_csv(self):
        """Click 'Import' to parse the uploaded CSV and open the field-mapping/preview step."""
        self.import_upload_button.click()
        # Step-2 dialog: the records preview + 'Import Clients' button
        expect(self.import_clients_button).to_be_visible(timeout=15000)

    def close_import_dialog(self):
        """Close the import dialog (Cancel) without importing any records."""
        self.import_cancel_button.click()
        expect(self.import_dialog).to_be_hidden(timeout=10000)

    # ─── Form Fill Helpers ────────────────────────────────────

    def fill_required_fields(self, first_name: str, last_name: str, email: str = None):
        self.first_name.fill(first_name)
        self.last_name.fill(last_name)
        if email:
            self.email_address.fill(email)

    def fill_required_fields_no_email(self, first_name: str, last_name: str):
        self.first_name.fill(first_name)
        self.last_name.fill(last_name)
        self.no_email_checkbox.check()

    def fill_personal_info(self, first_name: str, last_name: str, email: str = None,
                           middle_name: str = None, suffix: str = None,
                           ssn: str = None, dob: str = None):
        self.first_name.fill(first_name)
        if middle_name:
            self.middle_name.fill(middle_name)
        self.last_name.fill(last_name)
        if suffix:
            self.suffix.fill(suffix)
        if email:
            self.email_address.fill(email)
        if ssn:
            self.ssn_last4.fill(ssn)
        if dob:
            self.date_of_birth.fill(dob)

    def fill_address(self, address: str, city: str = None, state: str = None,
                     zip_code: str = None, apt: str = None):
        self.mailing_address.fill(address)
        if apt:
            self.apt_suite.fill(apt)
        if city:
            self.city.fill(city)
        if state:
            self.select_state(state)
        if zip_code:
            self.zip_code.fill(zip_code)

    def fill_previous_address(self, address: str, city: str = None, state: str = None,
                              zip_code: str = None, apt: str = None):
        if not self.previous_address_checkbox.is_checked():
            self.previous_address_checkbox.check()
        self.prev_mailing_address.fill(address)
        if apt:
            self.prev_apt_suite.fill(apt)
        if city:
            self.prev_city.fill(city)
        if state:
            self.select_previous_state(state)
        if zip_code:
            self.prev_zip_code.fill(zip_code)

    def fill_phones(self, mobile: str = None, alternate: str = None,
                    work: str = None, fax: str = None):
        if mobile:
            self.phone_mobile.fill(mobile)
        if alternate:
            self.phone_alternate.fill(alternate)
        if work:
            self.phone_work.fill(work)
        if fax:
            self.fax.fill(fax)

    # ─── Dropdown Helpers ─────────────────────────────────────

    def select_status(self, status_name: str):
        self.status_dropdown.scroll_into_view_if_needed()
        expect(self.status_dropdown).not_to_have_value("undefined", timeout=10000)
        self.status_dropdown.click()
        self.page.get_by_role("option", name=status_name, exact=True).click()

    def select_state(self, state_name: str):
        self.state.click()
        self.page.get_by_role("option", name=state_name, exact=True).click()

    def select_previous_state(self, state_name: str):
        self.prev_state.click()
        self.page.get_by_role("option", name=state_name, exact=True).click()

    def select_referred_by(self, referrer_name: str):
        self.referred_by.click()
        self.page.get_by_role("option", name=referrer_name, exact=True).click()

    def get_status_options(self) -> list[str]:
        self.status_dropdown.scroll_into_view_if_needed()
        expect(self.status_dropdown).not_to_have_value("undefined", timeout=10000)
        self.status_dropdown.click()
        options = self.page.locator("li[role='option']")
        expect(options.first).to_be_visible()
        texts = options.all_text_contents()
        self.page.keyboard.press("Escape")
        return texts

    # ─── Auto-suggest Address Helpers ─────────────────────────

    def type_and_select_autosuggest_address(self, address_text: str, suggestion_index: int = 0):
        """Type into Mailing Address to trigger Google Places, then select a suggestion."""
        self.mailing_address.fill("")
        self.mailing_address.press_sequentially(address_text, delay=100)
        expect(self.pac_items.first).to_be_visible(timeout=10000)
        self.pac_items.nth(suggestion_index).click()
        self.page.wait_for_timeout(1000)

    def type_and_select_prev_autosuggest_address(self, address_text: str, suggestion_index: int = 0):
        """Type into Previous Mailing Address to trigger Google Places, then select a suggestion."""
        if not self.previous_address_checkbox.is_checked():
            self.previous_address_checkbox.check()
        self.prev_mailing_address.fill("")
        self.prev_mailing_address.press_sequentially(address_text, delay=100)
        expect(self.pac_items.first).to_be_visible(timeout=10000)
        self.pac_items.nth(suggestion_index).click()
        self.page.wait_for_timeout(1000)

    def get_current_address_values(self) -> dict:
        """Return all current address field values as a dict."""
        return {
            "mailing_address": self.mailing_address.input_value(),
            "apt": self.apt_suite.input_value(),
            "city": self.city.input_value(),
            "state": self.state.input_value(),
            "zip_code": self.zip_code.input_value(),
            "country": self.country.input_value(),
        }

    def get_previous_address_values(self) -> dict:
        """Return all previous address field values as a dict."""
        return {
            "mailing_address": self.prev_mailing_address.input_value(),
            "apt": self.prev_apt_suite.input_value(),
            "city": self.prev_city.input_value(),
            "state": self.prev_state.input_value(),
            "zip_code": self.prev_zip_code.input_value(),
            "country": self.prev_country.input_value(),
        }

    # ─── Toggle Helpers ───────────────────────────────────────

    def enable_portal_access(self):
        if not self.portal_access_toggle.is_checked():
            self.portal_access_toggle.check()

    def disable_portal_access(self):
        if self.portal_access_toggle.is_checked():
            self.portal_access_toggle.uncheck()

    # ─── Submit / Cancel ──────────────────────────────────────

    def submit_form(self):
        self.submit_button.click()

    def confirm_save(self):
        expect(self.confirm_dialog).to_be_visible(timeout=5000)
        self.confirm_save_button.click()

    def submit_and_confirm(self):
        self.submit_form()
        self.confirm_save()

    def cancel_form(self):
        self.cancel_button.click()

    # ─── Toaster Assertions ───────────────────────────────────

    def expect_success_toaster(self, message: str = "Client profile added successfully"):
        expect(self.toaster).to_have_text(message, timeout=10000)

    def expect_error_toaster(self, message: str):
        expect(self.toaster).to_have_text(message, timeout=10000)

    def get_toaster_text(self) -> str:
        expect(self.toaster).to_be_visible(timeout=10000)
        return self.toaster.inner_text()

    # ─── Tooltip ──────────────────────────────────────────────

    def get_portal_access_tooltip(self) -> str:
        self.portal_access_info_icon.hover()
        tooltip = self.page.locator("[role='tooltip']")
        expect(tooltip).to_be_visible()
        return tooltip.inner_text()
