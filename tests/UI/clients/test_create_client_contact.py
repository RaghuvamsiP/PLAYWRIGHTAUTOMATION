"""
Comprehensive test suite for Create Client / Contact functionality.
Covers: form elements, dropdowns, input fields, toggles, toasters,
        validations, and contact creation with all available statuses.

Test order:
  POSITIVE  — Sections 1–11 (element visibility, defaults, happy-path creation,
               dropdowns, toggles, auto-suggest, portal, toasters, dialog actions)
  NEGATIVE  — Sections 12–15 (submit button state, mandatory field validation,
               input field validations, edge cases)
"""

import re
import pytest
from playwright.sync_api import Page, expect
from pages.create_client_page import CreateClientPage


# ════════════════════════════════════════════════════════════════
#  Helpers
# ════════════════════════════════════════════════════════════════

NO_PORTAL_STATUSES = ["Lead", "Prospect", "Lead/Inactive", "Inactive", "Suspended"]
PORTAL_STATUSES = ["Client", "Custom status 1"]


@pytest.fixture
def client_page(page: Page) -> CreateClientPage:
    """Navigate to Home page and open the Add Lead/Client dialog."""
    cp = CreateClientPage(page)
    cp.navigate_to_home()
    expect(page.get_by_text("Hello, Credit Hero!")).to_be_visible(timeout=60000)
    cp.open_add_client_from_home()
    return cp


def unique_email(prefix: str = "autotest") -> str:
    """Generate a unique email using timestamp to avoid collisions."""
    import time
    return f"{prefix}_{int(time.time())}@yopmail.com"


# ╔════════════════════════════════════════════════════════════════╗
# ║                     POSITIVE TESTS                            ║
# ╚════════════════════════════════════════════════════════════════╝


# ════════════════════════════════════════════════════════════════
#  1. DIALOG / FORM ELEMENT VISIBILITY
# ════════════════════════════════════════════════════════════════

class TestDialogElements:
    """Verify all form elements are present and visible in the Add Lead/Client dialog."""

    def test_dialog_title_is_visible(self, client_page: CreateClientPage):
        expect(client_page.dialog_heading).to_be_visible()
        expect(client_page.dialog_heading).to_contain_text("Add Lead/Client")

    def test_personal_info_fields_visible(self, client_page: CreateClientPage):
        expect(client_page.first_name).to_be_visible()
        expect(client_page.middle_name).to_be_visible()
        expect(client_page.last_name).to_be_visible()
        expect(client_page.suffix).to_be_visible()
        expect(client_page.email_address).to_be_visible()
        expect(client_page.ssn_last4).to_be_visible()
        expect(client_page.date_of_birth).to_be_visible()

    def test_suffix_placeholder(self, client_page: CreateClientPage):
        expect(client_page.suffix).to_have_attribute("placeholder", "Jr,Sr,etc..")

    def test_address_fields_visible(self, client_page: CreateClientPage):
        expect(client_page.mailing_address).to_be_visible()
        expect(client_page.apt_suite).to_be_visible()
        expect(client_page.city).to_be_visible()
        expect(client_page.state).to_be_visible()
        expect(client_page.zip_code).to_be_visible()
        expect(client_page.country).to_be_visible()

    def test_country_field_is_disabled_with_default_value(self, client_page: CreateClientPage):
        expect(client_page.country).to_be_disabled()
        expect(client_page.country).to_have_value("United States")

    def test_phone_fields_visible(self, client_page: CreateClientPage):
        expect(client_page.phone_mobile).to_be_visible()
        expect(client_page.phone_alternate).to_be_visible()
        expect(client_page.phone_work).to_be_visible()
        expect(client_page.fax).to_be_visible()

    def test_status_section_visible(self, client_page: CreateClientPage):
        client_page.status_dropdown.scroll_into_view_if_needed()
        expect(client_page.status_dropdown).to_be_visible()
        expect(client_page.start_date).to_be_visible()
        expect(client_page.assigned_to).to_be_visible()

    def test_referred_by_field_visible(self, client_page: CreateClientPage):
        expect(client_page.referred_by).to_be_visible()

    def test_portal_access_toggle_visible(self, client_page: CreateClientPage):
        expect(client_page.portal_access_toggle).to_be_visible()

    def test_no_email_checkbox_visible_and_unchecked_by_default(self, client_page: CreateClientPage):
        expect(client_page.no_email_checkbox).to_be_visible()
        expect(client_page.no_email_checkbox).not_to_be_checked()

    def test_previous_address_checkbox_visible_and_unchecked(self, client_page: CreateClientPage):
        expect(client_page.previous_address_checkbox).to_be_visible()
        expect(client_page.previous_address_checkbox).not_to_be_checked()

    def test_cancel_button_visible(self, client_page: CreateClientPage):
        expect(client_page.cancel_button).to_be_visible()
        expect(client_page.cancel_button).to_be_enabled()

    def test_submit_button_visible(self, client_page: CreateClientPage):
        expect(client_page.submit_button).to_be_visible()


# ════════════════════════════════════════════════════════════════
#  2. DEFAULT VALUES & FIELD STATE
# ════════════════════════════════════════════════════════════════

class TestDefaultValues:
    """Verify default field values and initial states."""

    def test_status_defaults_to_client(self, client_page: CreateClientPage):
        client_page.status_dropdown.scroll_into_view_if_needed()
        expect(client_page.status_dropdown).not_to_have_value("undefined", timeout=10000)
        expect(client_page.status_dropdown).to_have_value("Client")

    def test_start_date_defaults_to_today(self, client_page: CreateClientPage):
        client_page.start_date.scroll_into_view_if_needed()
        expect(client_page.start_date).not_to_have_value("")

    def test_assigned_to_has_default_value(self, client_page: CreateClientPage):
        client_page.assigned_to.scroll_into_view_if_needed()
        chip = client_page.dialog.get_by_role("button", name="Personal Monthly")
        expect(chip).to_be_visible()

    def test_submit_button_disabled_initially(self, client_page: CreateClientPage):
        expect(client_page.submit_button).to_be_disabled()

    def test_portal_access_toggle_off_by_default(self, client_page: CreateClientPage):
        expect(client_page.portal_access_toggle).not_to_be_checked()


# ════════════════════════════════════════════════════════════════
#  3. CLIENT CREATION — HAPPY PATH
# ════════════════════════════════════════════════════════════════

class TestCreateClientHappyPath:
    """Positive tests for successful client creation."""

    def test_create_client_with_required_fields_only(self, client_page: CreateClientPage):
        email = unique_email("req_only")
        client_page.fill_required_fields("AutoFirst", "AutoLast", email)
        client_page.submit_and_confirm()
        client_page.expect_success_toaster()

    def test_create_client_without_email(self, client_page: CreateClientPage):
        client_page.fill_required_fields_no_email("NoEmail", "Client")
        client_page.submit_and_confirm()
        client_page.expect_success_toaster()

    def test_create_client_with_full_personal_info(self, client_page: CreateClientPage):
        email = unique_email("full_info")
        client_page.fill_personal_info(
            first_name="John",
            middle_name="Michael",
            last_name="Doe",
            suffix="Jr",
            email=email,
            ssn="1234",
            dob="01/15/1990"
        )
        client_page.submit_and_confirm()
        client_page.expect_success_toaster()

    def test_create_client_with_address(self, client_page: CreateClientPage):
        email = unique_email("with_addr")
        client_page.fill_required_fields("Address", "Test", email)
        client_page.fill_address(
            address="123 Main Street",
            city="Los Angeles",
            state="California",
            zip_code="90001",
            apt="Suite 100"
        )
        client_page.submit_and_confirm()
        client_page.expect_success_toaster()

    def test_create_client_with_previous_address(self, client_page: CreateClientPage):
        email = unique_email("prev_addr")
        client_page.fill_required_fields("PrevAddr", "Test", email)
        client_page.fill_previous_address(
            address="456 Old Street",
            city="San Francisco",
            state="California",
            zip_code="94101",
            apt="Apt 2B"
        )
        client_page.submit_and_confirm()
        client_page.expect_success_toaster()

    def test_create_client_with_phone_numbers(self, client_page: CreateClientPage):
        email = unique_email("phones")
        client_page.fill_required_fields("Phone", "Test", email)
        client_page.fill_phones(
            mobile="9091234567",
            alternate="9097654321",
            work="2135551234",
            fax="2135559999"
        )
        client_page.submit_and_confirm()
        client_page.expect_success_toaster()

    def test_create_client_with_portal_access_enabled(self, client_page: CreateClientPage):
        email = unique_email("portal")
        client_page.fill_required_fields("Portal", "Access", email)
        client_page.enable_portal_access()
        expect(client_page.portal_access_toggle).to_be_checked()
        client_page.submit_and_confirm()
        client_page.expect_success_toaster()

    def test_create_client_with_all_fields(self, client_page: CreateClientPage):
        email = unique_email("all_fields")
        client_page.fill_personal_info(
            first_name="Complete",
            middle_name="M",
            last_name="Client",
            suffix="Sr",
            email=email,
            ssn="5678",
            dob="06/15/1985"
        )
        client_page.fill_address(
            address="789 Full Ave",
            city="New York",
            state="New York",
            zip_code="10001",
            apt="Floor 5"
        )
        client_page.fill_previous_address(
            address="321 Old Blvd",
            city="Boston",
            state="Massachusetts",
            zip_code="02101"
        )
        client_page.fill_phones(
            mobile="2125551111",
            alternate="2125552222",
            work="2125553333",
            fax="2125554444"
        )
        client_page.select_status("Client")
        client_page.enable_portal_access()
        client_page.submit_and_confirm()
        client_page.expect_success_toaster()


# ════════════════════════════════════════════════════════════════
#  4. CONTACT CREATION WITH ALL STATUSES (with email)
# ════════════════════════════════════════════════════════════════

class TestCreateContactWithAllStatuses:
    """Create contacts with each available status to verify all statuses work end-to-end."""

    @pytest.mark.parametrize("status", CreateClientPage.STATUSES)
    def test_create_contact_with_status(self, page: Page, status: str):
        cp = CreateClientPage(page)
        cp.navigate_to_home()
        expect(page.get_by_text("Hello, Credit Hero!")).to_be_visible(timeout=60000)
        cp.open_add_client_from_home()

        email = unique_email(f"status_{status.lower().replace('/', '_')}")
        cp.fill_required_fields("Status", "Test", email)
        cp.select_status(status)
        expect(cp.status_dropdown).to_have_value(status)
        cp.submit_and_confirm()
        cp.expect_success_toaster()


# ════════════════════════════════════════════════════════════════
#  5. NO-EMAIL CONTACT CREATION PER STATUS
# ════════════════════════════════════════════════════════════════

class TestNoEmailContactCreation:
    """Without email (using 'Doesn't have email' checkbox), contacts can be
    created for Lead, Prospect, Lead/Inactive, Inactive, Suspended statuses.
    Client and Custom status 1 also allow creation without email."""

    @pytest.mark.parametrize("status", NO_PORTAL_STATUSES)
    def test_create_contact_without_email_non_client_status(self, page: Page, status: str):
        """Creating a contact without email should succeed for non-client statuses."""
        cp = CreateClientPage(page)
        cp.navigate_to_home()
        expect(page.get_by_text("Hello, Credit Hero!")).to_be_visible(timeout=60000)
        cp.open_add_client_from_home()

        cp.fill_required_fields_no_email("NoEmail", status.replace("/", ""))
        cp.select_status(status)
        expect(cp.submit_button).to_be_enabled()
        cp.submit_and_confirm()
        cp.expect_success_toaster()

    @pytest.mark.parametrize("status", PORTAL_STATUSES)
    def test_create_contact_without_email_client_status(self, page: Page, status: str):
        """Creating a contact without email should also succeed for client-type statuses."""
        cp = CreateClientPage(page)
        cp.navigate_to_home()
        expect(page.get_by_text("Hello, Credit Hero!")).to_be_visible(timeout=60000)
        cp.open_add_client_from_home()

        cp.fill_required_fields_no_email("NoEmail", status.replace(" ", ""))
        cp.select_status(status)
        expect(cp.submit_button).to_be_enabled()
        cp.submit_and_confirm()
        cp.expect_success_toaster()

    def test_no_email_checkbox_enables_submit_without_email(self, client_page: CreateClientPage):
        """Checking 'Doesn't have email' should enable submit with only first + last name."""
        client_page.first_name.fill("NoEmail")
        client_page.last_name.fill("Check")
        expect(client_page.submit_button).to_be_disabled()
        client_page.no_email_checkbox.check()
        expect(client_page.submit_button).to_be_enabled()


# ════════════════════════════════════════════════════════════════
#  6. DROPDOWNS — STATUS, STATE, REFERRED BY
# ════════════════════════════════════════════════════════════════

class TestStatusDropdown:
    """Verify the Status dropdown options and selection behavior."""

    def test_status_dropdown_has_all_options(self, client_page: CreateClientPage):
        options = client_page.get_status_options()
        for expected_status in CreateClientPage.STATUSES:
            assert expected_status in options, f"Status '{expected_status}' not found in dropdown"

    def test_select_each_status_option(self, client_page: CreateClientPage):
        for status in CreateClientPage.STATUSES:
            client_page.select_status(status)
            expect(client_page.status_dropdown).to_have_value(status)

    def test_status_dropdown_option_count(self, client_page: CreateClientPage):
        options = client_page.get_status_options()
        assert len(options) == len(CreateClientPage.STATUSES), (
            f"Expected {len(CreateClientPage.STATUSES)} statuses, got {len(options)}"
        )


class TestStateDropdown:
    """Verify the State dropdown behavior."""

    def test_state_dropdown_opens_and_has_options(self, client_page: CreateClientPage):
        client_page.state.click()
        options = client_page.page.locator("li[role='option']")
        expect(options.first).to_be_visible()
        count = options.count()
        assert count > 0, "State dropdown has no options"
        client_page.page.keyboard.press("Escape")

    def test_select_state_california(self, client_page: CreateClientPage):
        client_page.select_state("California")
        expect(client_page.state).to_have_value("California")

    def test_select_previous_state(self, client_page: CreateClientPage):
        client_page.previous_address_checkbox.check()
        client_page.select_previous_state("Texas")
        expect(client_page.prev_state).to_have_value("Texas")


class TestReferredByDropdown:
    """Verify the Referred By dropdown behavior."""

    def test_referred_by_dropdown_opens_and_has_options(self, client_page: CreateClientPage):
        client_page.referred_by.click()
        options = client_page.page.locator("li[role='option']")
        expect(options.first).to_be_visible(timeout=5000)
        count = options.count()
        assert count > 0, "Referred By dropdown has no options"
        client_page.page.keyboard.press("Escape")

    def test_select_referred_by_sample_affiliate(self, client_page: CreateClientPage):
        client_page.select_referred_by("Sample Affiliate")
        expect(client_page.referred_by).to_have_value("Sample Affiliate")


# ════════════════════════════════════════════════════════════════
#  7. CHECKBOX & TOGGLE BEHAVIOR
# ════════════════════════════════════════════════════════════════

class TestCheckboxAndToggle:
    """Verify checkbox and toggle interactions."""

    def test_no_email_checkbox_can_be_checked_and_unchecked(self, client_page: CreateClientPage):
        expect(client_page.no_email_checkbox).not_to_be_checked()
        client_page.no_email_checkbox.check()
        expect(client_page.no_email_checkbox).to_be_checked()
        client_page.no_email_checkbox.uncheck()
        expect(client_page.no_email_checkbox).not_to_be_checked()

    def test_previous_address_checkbox_reveals_address_fields(self, client_page: CreateClientPage):
        expect(client_page.prev_mailing_address).to_be_hidden()
        client_page.previous_address_checkbox.check()
        expect(client_page.prev_mailing_address).to_be_visible()
        expect(client_page.prev_apt_suite).to_be_visible()
        expect(client_page.prev_city).to_be_visible()
        expect(client_page.prev_state).to_be_visible()
        expect(client_page.prev_zip_code).to_be_visible()
        expect(client_page.prev_country).to_be_visible()

    def test_previous_address_checkbox_hides_fields_on_uncheck(self, client_page: CreateClientPage):
        client_page.previous_address_checkbox.check()
        expect(client_page.prev_mailing_address).to_be_visible()
        client_page.previous_address_checkbox.uncheck()
        expect(client_page.prev_mailing_address).to_be_hidden()

    def test_previous_country_is_disabled(self, client_page: CreateClientPage):
        client_page.previous_address_checkbox.check()
        expect(client_page.prev_country).to_be_disabled()
        expect(client_page.prev_country).to_have_value("United States")

    def test_portal_access_toggle_on_off(self, client_page: CreateClientPage):
        expect(client_page.portal_access_toggle).not_to_be_checked()
        client_page.enable_portal_access()
        expect(client_page.portal_access_toggle).to_be_checked()
        client_page.disable_portal_access()
        expect(client_page.portal_access_toggle).not_to_be_checked()

    def test_portal_access_tooltip_text(self, client_page: CreateClientPage):
        tooltip_text = client_page.get_portal_access_tooltip()
        assert "email address" in tooltip_text.lower() or "portal" in tooltip_text.lower(), (
            f"Unexpected tooltip text: {tooltip_text}"
        )


# ════════════════════════════════════════════════════════════════
#  8. PORTAL ACCESS PER STATUS
# ════════════════════════════════════════════════════════════════

class TestPortalAccessPerStatus:
    """Portal access toggle should NOT be enabled for Lead, Prospect, Lead/Inactive,
    Inactive, Suspended. It should auto-enable for Client and Custom status 1."""

    @pytest.mark.parametrize("status", NO_PORTAL_STATUSES)
    def test_portal_not_checked_for_non_client_status(self, client_page: CreateClientPage, status: str):
        """Portal toggle must be unchecked when a non-client status is selected."""
        client_page.select_status(status)
        client_page.page.wait_for_timeout(500)
        expect(client_page.portal_access_toggle).not_to_be_checked()

    @pytest.mark.parametrize("status", NO_PORTAL_STATUSES)
    def test_portal_cannot_be_enabled_for_non_client_status(self, client_page: CreateClientPage, status: str):
        """Manually checking the portal toggle should not stick for non-client statuses."""
        client_page.select_status(status)
        client_page.page.wait_for_timeout(500)
        client_page.portal_access_toggle.click()
        client_page.page.wait_for_timeout(500)
        expect(client_page.portal_access_toggle).not_to_be_checked()

    @pytest.mark.parametrize("status", PORTAL_STATUSES)
    def test_portal_auto_enabled_for_client_status(self, client_page: CreateClientPage, status: str):
        """Portal toggle should automatically enable when Client or Custom status is selected."""
        client_page.select_status(status)
        client_page.page.wait_for_timeout(500)
        expect(client_page.portal_access_toggle).to_be_checked()

    def test_portal_unchecks_when_switching_client_to_lead(self, client_page: CreateClientPage):
        """Switching from Client to Lead should auto-uncheck portal access."""
        client_page.select_status("Client")
        expect(client_page.portal_access_toggle).to_be_checked()
        client_page.select_status("Lead")
        client_page.page.wait_for_timeout(500)
        expect(client_page.portal_access_toggle).not_to_be_checked()

    def test_portal_rechecks_when_switching_lead_to_client(self, client_page: CreateClientPage):
        """Switching from Lead back to Client should auto-check portal access."""
        client_page.select_status("Lead")
        expect(client_page.portal_access_toggle).not_to_be_checked()
        client_page.select_status("Client")
        client_page.page.wait_for_timeout(500)
        expect(client_page.portal_access_toggle).to_be_checked()

    def test_portal_stays_unchecked_across_non_client_statuses(self, client_page: CreateClientPage):
        """Cycling through all non-client statuses should keep portal unchecked."""
        for status in NO_PORTAL_STATUSES:
            client_page.select_status(status)
            client_page.page.wait_for_timeout(300)
            expect(client_page.portal_access_toggle).not_to_be_checked()


# ════════════════════════════════════════════════════════════════
#  9. AUTO-SUGGEST ADDRESS (Google Places Autocomplete)
# ════════════════════════════════════════════════════════════════

class TestAutoSuggestAddress:
    """Verify Google Places autocomplete fills address fields when a suggestion is selected."""

    def test_autosuggest_dropdown_appears_on_typing(self, client_page: CreateClientPage):
        client_page.mailing_address.press_sequentially("12517 Venice Blvd", delay=100)
        expect(client_page.pac_items.first).to_be_visible(timeout=10000)
        count = client_page.pac_items.count()
        assert count > 0, "No auto-suggest options appeared"

    def test_autosuggest_fills_mailing_address(self, client_page: CreateClientPage):
        client_page.type_and_select_autosuggest_address("12517 Venice Blvd")
        values = client_page.get_current_address_values()
        assert values["mailing_address"] != "", "Mailing Address was not auto-filled"

    def test_autosuggest_fills_city(self, client_page: CreateClientPage):
        client_page.type_and_select_autosuggest_address("12517 Venice Blvd")
        values = client_page.get_current_address_values()
        assert values["city"] != "", "City was not auto-filled"

    def test_autosuggest_fills_state(self, client_page: CreateClientPage):
        client_page.type_and_select_autosuggest_address("12517 Venice Blvd")
        values = client_page.get_current_address_values()
        assert values["state"] != "", "State was not auto-filled"

    def test_autosuggest_fills_zip_code(self, client_page: CreateClientPage):
        client_page.type_and_select_autosuggest_address("12517 Venice Blvd")
        values = client_page.get_current_address_values()
        assert values["zip_code"] != "", "Zip Code was not auto-filled"

    def test_autosuggest_fills_all_address_fields(self, client_page: CreateClientPage):
        """Select '12517 Venice Blvd' and verify all address fields are populated correctly."""
        client_page.type_and_select_autosuggest_address("12517 Venice Blvd")
        values = client_page.get_current_address_values()

        assert "Venice" in values["mailing_address"] or "12517" in values["mailing_address"], (
            f"Mailing Address unexpected: {values['mailing_address']}"
        )
        assert values["city"] != "", f"City was not filled"
        assert values["state"] != "", f"State was not filled"
        assert values["zip_code"] != "", f"Zip Code was not filled"
        assert values["country"] == "United States", f"Country changed: {values['country']}"

    def test_autosuggest_country_stays_united_states(self, client_page: CreateClientPage):
        client_page.type_and_select_autosuggest_address("12517 Venice Blvd")
        expect(client_page.country).to_have_value("United States")
        expect(client_page.country).to_be_disabled()

    def test_autosuggest_select_different_suggestion(self, client_page: CreateClientPage):
        """Select the second suggestion and verify fields are populated."""
        client_page.mailing_address.press_sequentially("12517 Venice Blvd", delay=100)
        expect(client_page.pac_items.first).to_be_visible(timeout=10000)
        if client_page.pac_items.count() > 1:
            client_page.pac_items.nth(1).click()
            client_page.page.wait_for_timeout(1000)
            values = client_page.get_current_address_values()
            assert values["mailing_address"] != "", "Address not filled for 2nd suggestion"
            assert values["city"] != "", "City not filled for 2nd suggestion"

    def test_create_client_with_autosuggest_address(self, client_page: CreateClientPage):
        """End-to-end: create a client using auto-suggest address and verify success."""
        email = unique_email("autosuggest")
        client_page.fill_required_fields("AutoAddr", "Test", email)
        client_page.type_and_select_autosuggest_address("12517 Venice Blvd")
        values = client_page.get_current_address_values()
        assert values["city"] != "", "City should be auto-filled before submit"
        client_page.submit_and_confirm()
        client_page.expect_success_toaster()


class TestPreviousAddressAutoSuggest:
    """Verify Google Places autocomplete works on Previous Mailing Address field."""

    def test_prev_autosuggest_dropdown_appears(self, client_page: CreateClientPage):
        client_page.previous_address_checkbox.check()
        client_page.prev_mailing_address.press_sequentially("350 Fifth Avenue", delay=100)
        expect(client_page.pac_items.first).to_be_visible(timeout=10000)
        count = client_page.pac_items.count()
        assert count > 0, "No auto-suggest options appeared for previous address"

    def test_prev_autosuggest_fills_all_fields(self, client_page: CreateClientPage):
        """Select a suggestion for Previous Address and verify all fields are populated."""
        client_page.type_and_select_prev_autosuggest_address("350 Fifth Avenue")
        values = client_page.get_previous_address_values()

        assert values["mailing_address"] != "", "Previous Mailing Address not filled"
        assert values["city"] != "", "Previous City not filled"
        assert values["state"] != "", "Previous State not filled"
        assert values["zip_code"] != "", "Previous Zip Code not filled"
        assert values["country"] == "United States", f"Previous Country changed: {values['country']}"

    def test_prev_autosuggest_fills_city(self, client_page: CreateClientPage):
        client_page.type_and_select_prev_autosuggest_address("350 Fifth Avenue")
        values = client_page.get_previous_address_values()
        assert values["city"] != "", "Previous City was not auto-filled"

    def test_prev_autosuggest_fills_state(self, client_page: CreateClientPage):
        client_page.type_and_select_prev_autosuggest_address("350 Fifth Avenue")
        values = client_page.get_previous_address_values()
        assert values["state"] != "", "Previous State was not auto-filled"

    def test_prev_autosuggest_fills_zip_code(self, client_page: CreateClientPage):
        client_page.type_and_select_prev_autosuggest_address("350 Fifth Avenue")
        values = client_page.get_previous_address_values()
        assert values["zip_code"] != "", "Previous Zip Code was not auto-filled"

    def test_prev_autosuggest_country_stays_disabled(self, client_page: CreateClientPage):
        client_page.type_and_select_prev_autosuggest_address("350 Fifth Avenue")
        expect(client_page.prev_country).to_have_value("United States")
        expect(client_page.prev_country).to_be_disabled()

    def test_both_addresses_autosuggest_independent(self, client_page: CreateClientPage):
        """Verify current and previous address auto-suggest work independently."""
        client_page.type_and_select_autosuggest_address("12517 Venice Blvd")
        current = client_page.get_current_address_values()

        client_page.type_and_select_prev_autosuggest_address("350 Fifth Avenue")
        previous = client_page.get_previous_address_values()

        assert current["mailing_address"] != "", "Current address not filled"
        assert previous["mailing_address"] != "", "Previous address not filled"
        assert current["mailing_address"] != previous["mailing_address"], (
            "Current and previous addresses should be different"
        )

    def test_create_client_with_both_autosuggest_addresses(self, client_page: CreateClientPage):
        """End-to-end: create client with both current & previous auto-suggest addresses."""
        email = unique_email("both_addr")
        client_page.fill_required_fields("BothAddr", "Test", email)
        client_page.type_and_select_autosuggest_address("12517 Venice Blvd")
        client_page.type_and_select_prev_autosuggest_address("350 Fifth Avenue")
        client_page.submit_and_confirm()
        client_page.expect_success_toaster()


# ════════════════════════════════════════════════════════════════
#  10. TOASTER NOTIFICATIONS
# ════════════════════════════════════════════════════════════════

class TestToasterNotifications:
    """Verify toaster messages appear and auto-dismiss."""

    def test_success_toaster_appears_on_client_creation(self, client_page: CreateClientPage):
        email = unique_email("toaster_success")
        client_page.fill_required_fields("Toaster", "Test", email)
        client_page.submit_and_confirm()
        toaster_text = client_page.get_toaster_text()
        assert "Client profile added successfully" in toaster_text

    def test_success_toaster_auto_dismisses(self, client_page: CreateClientPage):
        email = unique_email("toaster_dismiss")
        client_page.fill_required_fields("Dismiss", "Test", email)
        client_page.submit_and_confirm()
        expect(client_page.toaster).to_be_visible(timeout=10000)
        expect(client_page.toaster).to_be_hidden(timeout=10000)


# ════════════════════════════════════════════════════════════════
#  11. CONFIRMATION DIALOG & DIALOG ACTIONS
# ════════════════════════════════════════════════════════════════

class TestConfirmationDialog:
    """Verify the confirmation dialog that appears before saving."""

    def test_confirmation_dialog_appears_on_submit(self, client_page: CreateClientPage):
        email = unique_email("confirm_dlg")
        client_page.fill_required_fields("Confirm", "Dialog", email)
        client_page.submit_form()
        expect(client_page.confirm_dialog).to_be_visible(timeout=5000)

    def test_confirmation_dialog_has_save_button(self, client_page: CreateClientPage):
        email = unique_email("save_btn")
        client_page.fill_required_fields("Save", "Btn", email)
        client_page.submit_form()
        expect(client_page.confirm_save_button).to_be_visible()


class TestDialogCancelClose:
    """Verify dialog can be closed via Cancel button and X button."""

    def test_cancel_button_closes_dialog(self, client_page: CreateClientPage):
        client_page.first_name.fill("WillCancel")
        client_page.cancel_button.click()
        expect(client_page.dialog).to_be_hidden(timeout=5000)

    def test_close_x_button_closes_dialog(self, client_page: CreateClientPage):
        client_page.first_name.fill("WillClose")
        close_btn = client_page.dialog_heading.locator("button")
        close_btn.click()
        expect(client_page.dialog).to_be_hidden(timeout=5000)

    def test_dialog_reopens_with_empty_fields(self, client_page: CreateClientPage):
        client_page.first_name.fill("Temp")
        client_page.cancel_button.click()
        expect(client_page.dialog).to_be_hidden(timeout=5000)
        client_page.open_add_client_from_home()
        expect(client_page.first_name).to_have_value("")


# ╔════════════════════════════════════════════════════════════════╗
# ║               NEGATIVE / VALIDATION TESTS                     ║
# ╚════════════════════════════════════════════════════════════════╝


# ════════════════════════════════════════════════════════════════
#  12. SUBMIT BUTTON STATE VALIDATION
# ════════════════════════════════════════════════════════════════

class TestSubmitButtonState:
    """Verify the Add Lead/Client button enables only when required fields are filled."""

    def test_button_disabled_with_only_first_name(self, client_page: CreateClientPage):
        client_page.first_name.fill("Test")
        expect(client_page.submit_button).to_be_disabled()

    def test_button_disabled_with_first_and_last_name_only(self, client_page: CreateClientPage):
        client_page.first_name.fill("Test")
        client_page.last_name.fill("User")
        expect(client_page.submit_button).to_be_disabled()

    def test_button_enabled_with_first_last_and_email(self, client_page: CreateClientPage):
        client_page.first_name.fill("Test")
        client_page.last_name.fill("User")
        client_page.email_address.fill("test@yopmail.com")
        expect(client_page.submit_button).to_be_enabled()

    def test_button_enabled_with_no_email_checkbox(self, client_page: CreateClientPage):
        client_page.first_name.fill("Test")
        client_page.last_name.fill("User")
        client_page.no_email_checkbox.check()
        expect(client_page.submit_button).to_be_enabled()

    def test_button_disabled_after_clearing_required_field(self, client_page: CreateClientPage):
        client_page.first_name.fill("Test")
        client_page.last_name.fill("User")
        client_page.email_address.fill("test@yopmail.com")
        expect(client_page.submit_button).to_be_enabled()
        client_page.first_name.fill("")
        expect(client_page.submit_button).to_be_disabled()


# ════════════════════════════════════════════════════════════════
#  13. MANDATORY FIELD VALIDATION
# ════════════════════════════════════════════════════════════════

class TestMandatoryFieldValidation:
    """Validate that the form cannot be submitted without mandatory fields.
    Required: First Name, Last Name, and either Email or 'No email' checkbox."""

    def test_submit_disabled_with_empty_form(self, client_page: CreateClientPage):
        expect(client_page.submit_button).to_be_disabled()

    def test_submit_disabled_without_first_name(self, client_page: CreateClientPage):
        client_page.last_name.fill("User")
        client_page.email_address.fill("test@yopmail.com")
        expect(client_page.submit_button).to_be_disabled()

    def test_submit_disabled_without_last_name(self, client_page: CreateClientPage):
        client_page.first_name.fill("Test")
        client_page.email_address.fill("test@yopmail.com")
        expect(client_page.submit_button).to_be_disabled()

    def test_submit_disabled_without_email_and_no_checkbox(self, client_page: CreateClientPage):
        """First + Last provided but no email and checkbox unchecked — submit stays disabled."""
        client_page.first_name.fill("Test")
        client_page.last_name.fill("User")
        expect(client_page.submit_button).to_be_disabled()

    def test_submit_enabled_with_all_mandatory_fields(self, client_page: CreateClientPage):
        client_page.first_name.fill("Test")
        client_page.last_name.fill("User")
        client_page.email_address.fill("test@yopmail.com")
        expect(client_page.submit_button).to_be_enabled()

    def test_submit_enabled_with_no_email_checkbox(self, client_page: CreateClientPage):
        client_page.first_name.fill("Test")
        client_page.last_name.fill("User")
        client_page.no_email_checkbox.check()
        expect(client_page.submit_button).to_be_enabled()

    def test_submit_disables_after_clearing_first_name(self, client_page: CreateClientPage):
        client_page.fill_required_fields("Test", "User", "test@yopmail.com")
        expect(client_page.submit_button).to_be_enabled()
        client_page.first_name.fill("")
        expect(client_page.submit_button).to_be_disabled()

    def test_submit_disables_after_clearing_last_name(self, client_page: CreateClientPage):
        client_page.fill_required_fields("Test", "User", "test@yopmail.com")
        expect(client_page.submit_button).to_be_enabled()
        client_page.last_name.fill("")
        expect(client_page.submit_button).to_be_disabled()

    def test_submit_disables_after_clearing_email(self, client_page: CreateClientPage):
        client_page.fill_required_fields("Test", "User", "test@yopmail.com")
        expect(client_page.submit_button).to_be_enabled()
        client_page.email_address.fill("")
        expect(client_page.submit_button).to_be_disabled()

    def test_unchecking_no_email_disables_submit_if_email_empty(self, client_page: CreateClientPage):
        """Unchecking 'Doesn't have email' without providing an email should disable submit."""
        client_page.first_name.fill("NoEmail")
        client_page.last_name.fill("Toggle")
        client_page.no_email_checkbox.check()
        expect(client_page.submit_button).to_be_enabled()
        client_page.no_email_checkbox.uncheck()
        expect(client_page.submit_button).to_be_disabled()

    def test_ssn_validation_error_toaster(self, client_page: CreateClientPage):
        """Submitting invalid SSN (not exactly 4 digits) should show error toaster."""
        client_page.fill_required_fields_no_email("SSN", "Validation")
        client_page.ssn_last4.fill("12345")
        ssn_value = client_page.ssn_last4.input_value()
        client_page.submit_and_confirm()
        if len(ssn_value) != 4:
            client_page.expect_error_toaster("Please enter Last 4 digits of the SS#")


# ════════════════════════════════════════════════════════════════
#  14. INPUT FIELD VALIDATIONS
# ════════════════════════════════════════════════════════════════

class TestInputFieldValidations:
    """Validate field-level constraints: formatting, masking, max lengths."""

    def test_phone_mobile_formats_to_us_pattern(self, client_page: CreateClientPage):
        client_page.phone_mobile.fill("9091929394")
        expect(client_page.phone_mobile).to_have_value(re.compile(r"^\(\d{3}\)\s\d{3}-\d{4}$"))

    def test_phone_alternate_formats_to_us_pattern(self, client_page: CreateClientPage):
        client_page.phone_alternate.scroll_into_view_if_needed()
        client_page.phone_alternate.fill("8081234567")
        expect(client_page.phone_alternate).to_have_value(re.compile(r"^\(\d{3}\)\s\d{3}-\d{4}$"))

    def test_phone_work_formats_to_us_pattern(self, client_page: CreateClientPage):
        client_page.phone_work.scroll_into_view_if_needed()
        client_page.phone_work.fill("7071234567")
        expect(client_page.phone_work).to_have_value(re.compile(r"^\(\d{3}\)\s\d{3}-\d{4}$"))

    def test_fax_formats_to_us_pattern(self, client_page: CreateClientPage):
        client_page.fax.scroll_into_view_if_needed()
        client_page.fax.fill("6061234567")
        expect(client_page.fax).to_have_value(re.compile(r"^\(\d{3}\)\s\d{3}-\d{4}$"))

    def test_ssn_field_accepts_max_4_digits(self, client_page: CreateClientPage):
        client_page.ssn_last4.fill("12345")
        value = client_page.ssn_last4.input_value()
        assert len(value) <= 4, f"SSN field accepted {len(value)} chars, expected max 4"

    def test_ssn_invalid_length_shows_error_on_submit(self, client_page: CreateClientPage):
        client_page.fill_required_fields_no_email("SSN", "Error")
        client_page.ssn_last4.fill("12345")
        ssn_value = client_page.ssn_last4.input_value()
        client_page.submit_and_confirm()
        if len(ssn_value) != 4:
            client_page.expect_error_toaster("Please enter Last 4 digits of the SS#")

    def test_date_of_birth_accepts_valid_date(self, client_page: CreateClientPage):
        client_page.date_of_birth.fill("01/15/1990")
        expect(client_page.date_of_birth).to_have_value("01/15/1990")

    def test_start_date_can_be_changed(self, client_page: CreateClientPage):
        client_page.start_date.scroll_into_view_if_needed()
        client_page.start_date.fill("")
        client_page.start_date.fill("12/25/2025")
        expect(client_page.start_date).to_have_value("12/25/2025")


# ════════════════════════════════════════════════════════════════
#  15. NEGATIVE / EDGE CASES
# ════════════════════════════════════════════════════════════════

class TestNegativeAndEdgeCases:
    """Negative tests and boundary conditions."""

    def test_cannot_submit_empty_form(self, client_page: CreateClientPage):
        expect(client_page.submit_button).to_be_disabled()

    def test_cannot_submit_with_only_first_name(self, client_page: CreateClientPage):
        client_page.first_name.fill("OnlyFirst")
        expect(client_page.submit_button).to_be_disabled()

    def test_cannot_submit_with_only_last_name(self, client_page: CreateClientPage):
        client_page.last_name.fill("OnlyLast")
        expect(client_page.submit_button).to_be_disabled()

    def test_first_name_with_special_characters(self, client_page: CreateClientPage):
        client_page.first_name.fill("O'Brien-Smith")
        expect(client_page.first_name).to_have_value("O'Brien-Smith")

    def test_email_field_with_spaces(self, client_page: CreateClientPage):
        client_page.email_address.fill("  test@yopmail.com  ")
        value = client_page.email_address.input_value()
        assert "@" in value

    def test_create_client_with_minimum_data_no_email(self, client_page: CreateClientPage):
        client_page.fill_required_fields_no_email("Min", "Data")
        expect(client_page.submit_button).to_be_enabled()

    def test_clear_email_after_filling_disables_submit(self, client_page: CreateClientPage):
        client_page.fill_required_fields("Test", "User", "test@yopmail.com")
        expect(client_page.submit_button).to_be_enabled()
        client_page.email_address.fill("")
        expect(client_page.submit_button).to_be_disabled()
