from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from config.urls import AppURLs


class AffiliatePage(BasePage):
    """Page object for the Affiliate Partners page and Add/Edit Affiliate dialogs."""

    STATUSES = ["Active (recommended)", "Inactive", "Pending"]
    NO_PORTAL_STATUSES = ["Inactive", "Pending"]
    PORTAL_STATUSES = ["Active (recommended)"]

    def __init__(self, page: Page):
        super().__init__(page)

        # -- Affiliates List Page --
        self.page_heading = page.get_by_role("heading", name="Affiliate Partners")
        self.add_affiliate_button = page.get_by_role("button", name="Add New Affiliate")
        self.table_search = page.get_by_placeholder("Search...")

        # -- Export / Import --
        self.export_import_button = page.get_by_role("button", name="Export/Import")
        self.export_menu_item = page.get_by_role("menuitem", name="Export")
        self.import_menu_item = page.get_by_role("menuitem", name="Import")

        # Step 1 dialog: choose & upload a CSV file
        self.import_dialog = page.get_by_role("dialog", name="Import Affiliates From CSV File")
        self.choose_file_button = self.import_dialog.get_by_role("button", name="Choose File")
        self.import_file_input = self.import_dialog.locator("input#choose-file[type='file']")
        self.import_upload_button = self.import_dialog.get_by_role("button", name="Import", exact=True)

        # Step 2 dialog: map fields, pick records and confirm
        self.import_as_active_radio = self.import_dialog.get_by_role("radio", name="Import All as Active Affiliate")
        self.import_as_inactive_radio = self.import_dialog.get_by_role("radio", name="Import All as Inactive Affiliate")
        self.select_all_records_checkbox = self.import_dialog.get_by_role("checkbox", name="select all desserts")
        self.import_affiliates_button = self.import_dialog.get_by_role("button", name="Import Affiliates")
        self.import_cancel_button = self.import_dialog.get_by_role("button", name="Cancel")

        # -- Dialog --
        self.dialog = page.locator("div[role='dialog']")
        self.dialog_heading = self.dialog.locator("h2")

        # -- File Upload --
        self.file_input = self.dialog.locator("input[type='file']")
        self.upload_label = self.dialog.get_by_text("Upload/Edit Image")

        # -- Personal Info --
        self.first_name = self.dialog.get_by_label("First Name*")
        self.last_name = self.dialog.get_by_label("Last Name*")
        self.email_address = self.dialog.get_by_label("Email Address*")
        self.phone = self.dialog.get_by_label("Phone*")
        self.phone_ext = self.dialog.get_by_label("Ext. (Optional)")
        self.phone_mobile = self.dialog.get_by_label("Phone (Mobile)")
        self.company_name = self.dialog.get_by_label("Company Name")
        self.company_website = self.dialog.get_by_label("Company Website")
        self.fax = self.dialog.get_by_label("Fax")

        # -- Dropdowns --
        self.status_dropdown = self.dialog.get_by_role("combobox").first
        self.assigned_to_dropdown = self.dialog.get_by_label("Assigned To")
        self.state_dropdown = self.dialog.get_by_label("State")

        # -- Address --
        self.mailing_address = self.dialog.get_by_label("Mailing Address")
        self.city = self.dialog.get_by_label("City")
        self.zip_code = self.dialog.get_by_label("Zip Code")
        self.country = self.dialog.get_by_label("Country")

        # -- Checkboxes & Toggles --
        self.master_contact_checkbox = self.dialog.get_by_label("Add to master contact list")
        self.portal_access_toggle = self.dialog.get_by_label("Off / On")

        # -- Google Places Auto-suggest --
        self.pac_items = page.locator(".pac-container:visible .pac-item")

        # -- Action Buttons --
        self.cancel_button = self.dialog.get_by_role("button", name="Cancel")
        self.submit_button = self.dialog.get_by_role("button", name="Add Affiliate")
        self.update_button = self.dialog.get_by_role("button", name="Update Affiliate")

        # -- Toaster --
        self.toaster = page.locator(".MuiAlert-message:visible")

        # -- Delete Confirmation Dialog --
        self.delete_dialog_heading = page.get_by_role("heading", name="Inactive/Delete affiliate")
        self.delete_button = page.get_by_role("button", name="Delete this affiliate")
        self.inactivate_button = page.get_by_role("button", name="Inactivate this affiliate")

        # -- Validation Errors --
        self.error_messages = self.dialog.locator(".MuiFormHelperText-root")

    # ─── Navigation ───────────────────────────────────────────

    def navigate_to_affiliates(self):
        self.navigate(AppURLs.Affiliates.LIST)
        expect(self.page_heading).to_be_visible(timeout=15000)

    # ─── Export / Import CSV ──────────────────────────────────

    def open_import_dialog(self):
        """Click Export/Import → Import to open the 'Import Affiliates From CSV File' dialog."""
        self.export_import_button.click()
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
        # Step-2 dialog: the records preview + 'Import Affiliates' button
        expect(self.import_affiliates_button).to_be_visible(timeout=15000)

    def close_import_dialog(self):
        """Close the import dialog (Cancel) without importing any records."""
        self.import_cancel_button.click()
        expect(self.import_dialog).to_be_hidden(timeout=10000)

    def confirm_import(self, as_active: bool = True, select_all: bool = True):
        """On the preview step, pick the status, optionally select all records, and import."""
        if as_active:
            self.import_as_active_radio.check()
        else:
            self.import_as_inactive_radio.check()
        if select_all:
            self.select_all_records_checkbox.check()
        self.import_affiliates_button.click()

    def import_affiliates_from_csv(self, file_path: str, as_active: bool = True, select_all: bool = True):
        """End-to-end CSV import: open dialog → upload → submit → confirm."""
        self.open_import_dialog()
        self.upload_csv(file_path)
        self.submit_uploaded_csv()
        self.confirm_import(as_active=as_active, select_all=select_all)

    # ─── Open Dialogs ─────────────────────────────────────────

    def open_add_dialog(self):
        self.add_affiliate_button.click()
        expect(self.dialog).to_be_visible(timeout=10000)

    def open_edit_dialog_for(self, affiliate_name: str):
        """Click the 3-dot menu for a given affiliate and select Edit."""
        row = self.page.locator(f"[role='row']:has-text('{affiliate_name}')")
        row.locator("[data-testid='MoreVertIcon']").click()
        self.page.get_by_role("menuitem", name="Edit").click()
        expect(self.dialog).to_be_visible(timeout=10000)

    def open_delete_dialog_for(self, affiliate_name: str):
        """Click the 3-dot menu for a given affiliate and select Delete."""
        row = self.page.locator(f"[role='row']:has-text('{affiliate_name}')")
        row.locator("[data-testid='MoreVertIcon']").click()
        self.page.get_by_role("menuitem", name="Delete").click()
        expect(self.delete_dialog_heading).to_be_visible(timeout=10000)

    # ─── Form Fill Helpers ────────────────────────────────────

    def fill_required_fields(self, first_name: str, last_name: str, email: str, phone: str):
        self.first_name.fill(first_name)
        self.last_name.fill(last_name)
        self.email_address.fill(email)
        self.phone.fill(phone)

    def fill_full_details(self, first_name: str, last_name: str, email: str, phone: str,
                          mobile: str = None, company: str = None, website: str = None,
                          fax: str = None, phone_ext: str = None,
                          address: str = None, city: str = None,
                          state: str = None, zip_code: str = None):
        self.fill_required_fields(first_name, last_name, email, phone)
        if phone_ext:
            self.phone_ext.fill(phone_ext)
        if mobile:
            self.phone_mobile.fill(mobile)
        if company:
            self.company_name.fill(company)
        if website:
            self.company_website.fill(website)
        if fax:
            self.fax.fill(fax)
        if address:
            self.mailing_address.fill(address)
        if city:
            self.city.fill(city)
        if state:
            self.select_state(state)
        if zip_code:
            self.zip_code.fill(zip_code)

    # ─── Dropdown Helpers ─────────────────────────────────────

    def select_status(self, status_name: str):
        self.status_dropdown.click()
        self.page.wait_for_timeout(300)
        options = self.page.locator("li[role='option']")
        expect(options.first).to_be_visible(timeout=5000)
        for opt in options.all():
            if opt.inner_text().strip().startswith(status_name.split(" ")[0]):
                opt.click()
                self.page.wait_for_timeout(300)
                return
        # Fallback: exact match
        self.page.get_by_role("option", name=status_name, exact=True).click()

    def select_state(self, state_name: str):
        self.state_dropdown.click()
        self.page.get_by_role("option", name=state_name, exact=True).click()

    def get_status_options(self) -> list[str]:
        self.status_dropdown.click()
        self.page.wait_for_timeout(300)
        options = self.page.locator("li[role='option']")
        expect(options.first).to_be_visible(timeout=5000)
        texts = options.all_text_contents()
        self.page.keyboard.press("Escape")
        return texts

    # ─── Auto-suggest Address ─────────────────────────────────

    def type_and_select_autosuggest_address(self, address_text: str, suggestion_index: int = 0):
        self.mailing_address.fill("")
        self.mailing_address.press_sequentially(address_text, delay=100)
        expect(self.pac_items.first).to_be_visible(timeout=10000)
        self.pac_items.nth(suggestion_index).click()
        self.page.wait_for_timeout(1000)

    def get_address_values(self) -> dict:
        return {
            "mailing_address": self.mailing_address.input_value(),
            "city": self.city.input_value(),
            "state": self.state_dropdown.input_value(),
            "zip_code": self.zip_code.input_value(),
            "country": self.country.input_value(),
        }

    # ─── Portal Toggle ────────────────────────────────────────

    def is_portal_checked(self) -> bool:
        return self.portal_access_toggle.is_checked()

    # ─── Image Upload ─────────────────────────────────────────

    def upload_profile_image(self, file_path: str):
        self.file_input.set_input_files(file_path)
        self.page.wait_for_timeout(1000)

    # ─── Submit / Update / Cancel ─────────────────────────────

    def submit_form(self):
        self.submit_button.click()

    def update_form(self):
        self.update_button.click()

    def cancel_dialog(self):
        self.cancel_button.click()

    # ─── Delete Actions ───────────────────────────────────────

    def confirm_delete(self):
        self.delete_button.click()

    def confirm_inactivate(self):
        self.inactivate_button.click()

    # ─── Toaster ──────────────────────────────────────────────

    def get_toaster_text(self) -> str:
        expect(self.toaster).to_be_visible(timeout=10000)
        return self.toaster.inner_text()

    def wait_for_toaster_dismiss(self):
        expect(self.toaster).to_be_visible(timeout=10000)
        expect(self.toaster).to_be_hidden(timeout=15000)

    # ─── Table Helpers ────────────────────────────────────────

    def is_affiliate_in_table(self, name: str) -> bool:
        self.page.wait_for_timeout(1000)
        return self.page.locator(f"[role='row']:has-text('{name}')").count() > 0

    def click_affiliate_name_in_table(self, name: str):
        """Click on an affiliate's name link in the table to open the Edit dialog."""
        row = self.page.locator(f"[role='row']:has-text('{name}')").first
        name_cell = row.locator("[role='cell'], [role='gridcell']").first
        name_cell.locator("a").click()
        expect(self.dialog).to_be_visible(timeout=10000)

    def get_affiliate_row_data(self, name: str) -> dict:
        """Return the cell values for a given affiliate row."""
        row = self.page.locator(f"[role='row']:has-text('{name}')").first
        cells = row.locator("[role='cell'], [role='gridcell']").all()
        if len(cells) >= 8:
            return {
                "name": cells[0].inner_text().strip(),
                "company": cells[1].inner_text().strip(),
                "email": cells[2].inner_text().strip(),
                "clients_referred": cells[3].inner_text().strip(),
                "phone": cells[4].inner_text().strip(),
                "date_added": cells[5].inner_text().strip(),
                "status": cells[6].inner_text().strip(),
                "login": cells[7].inner_text().strip(),
            }
        return {}

    # ─── Validation Errors ────────────────────────────────────

    def get_validation_errors(self) -> list[str]:
        errors = self.error_messages.all()
        return [e.inner_text().strip() for e in errors if e.inner_text().strip()]
