"""
Create a client from the Clients module, filling every field in the Add Lead/Client dialog.

Logs in as the household-plan QA account (hplan@yopmail.com) on a clean browser,
so it does not use the stored pm@yopmail.com session from the root conftest.
"""

import random
import re
import time

import allure
import pytest
from playwright.sync_api import Page, expect

from pages.create_client_page import CreateClientPage
from pages.login_page import LoginPage

HPLAN_EMAIL = "hplan@yopmail.com"
HPLAN_PASSWORD = "Test@1234"

# Options shown for this account (verified on QA)
HPLAN_STATUSES = ["Lead", "Prospect", "Lead/Inactive", "Client", "Inactive", "Suspended",
                  "Custom Client 1", "Custom Client 2"]
ASSIGNED_TO = "HouseHold User"
REFERRED_BY = "Sample Affiliate"
AGREEMENT = "Custom Agreement"
PORTAL_LANGUAGE = "English"


@pytest.fixture
def hplan_client_page(fresh_page: Page) -> CreateClientPage:
    """Log in as hplan, open the Clients module and the Add Lead/Client dialog."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()
    login.login(HPLAN_EMAIL, HPLAN_PASSWORD)
    login.wait_for_home_page()

    cp = CreateClientPage(fresh_page)
    cp.open_clients_module()
    cp.open_add_client_from_clients_page()
    expect(cp.dialog_heading).to_be_visible()
    return cp


def build_client_data() -> dict:
    run_id = int(time.time())
    return {
        "first_name": "Auto",
        "middle_name": "QA",
        "last_name": f"Client{run_id}",
        "suffix": "Jr",
        "email": f"auto.client{run_id}@yopmail.com",
        "phone_mobile": "3105550101",
        "phone_alternate": "3105550102",
        "phone_work": "3105550103",
        "fax": "3105550104",
        "ssn": f"{random.randint(100, 665)}{random.randint(10, 99)}{random.randint(1000, 9999)}",
        "dob": "01/15/1990",
        "address": "12517 Venice Blvd",
        "apt": "Suite 100",
        "city": "Los Angeles",
        "state": "California",
        "zip_code": "90066",
        "prev_address": "350 5th Ave",
        "prev_apt": "Apt 21",
        "prev_city": "New York",
        "prev_state": "New York",
        "prev_zip_code": "10118",
        "status": "Client",
    }


@pytest.mark.ui
@pytest.mark.smoke
@allure.feature("Clients")
@allure.title("Create a client with all fields from the Clients module (hplan)")
def test_create_client_with_all_fields(hplan_client_page: CreateClientPage):
    cp = hplan_client_page
    data = build_client_data()

    with allure.step("Verify default field states"):
        expect(cp.submit_button).to_be_disabled()
        expect(cp.country).to_be_disabled()
        expect(cp.country).to_have_value("United States")
        expect(cp.suffix).to_have_attribute("placeholder", "Jr,Sr,etc..")

    with allure.step("Fill Personal Information"):
        cp.fill_personal_info(
            first_name=data["first_name"],
            middle_name=data["middle_name"],
            last_name=data["last_name"],
            suffix=data["suffix"],
            email=data["email"],
        )
        expect(cp.no_email_checkbox).not_to_be_checked()
        cp.fill_phones(
            mobile=data["phone_mobile"],
            alternate=data["phone_alternate"],
            work=data["phone_work"],
            fax=data["fax"],
        )

    with allure.step("Fill Credit Information"):
        cp.fill_ssn(data["ssn"])
        cp.show_ssn_button.click()
        expect(cp.ssn_part3).to_have_value(data["ssn"][5:])
        cp.date_of_birth.fill(data["dob"])
        expect(cp.date_of_birth).to_have_value(data["dob"])

    with allure.step("Fill current Mailing Address"):
        cp.fill_address(
            address=data["address"],
            apt=data["apt"],
            city=data["city"],
            state=data["state"],
            zip_code=data["zip_code"],
        )

    with allure.step("Fill Previous Address"):
        cp.fill_previous_address(
            address=data["prev_address"],
            apt=data["prev_apt"],
            city=data["prev_city"],
            state=data["prev_state"],
            zip_code=data["prev_zip_code"],
        )

    with allure.step("Verify address values"):
        current = cp.get_current_address_values()
        assert current["mailing_address"] == data["address"]
        assert current["city"] == data["city"]
        assert current["state"] == data["state"]
        assert current["zip_code"] == data["zip_code"]
        previous = cp.get_previous_address_values()
        assert previous["mailing_address"] == data["prev_address"]
        assert previous["city"] == data["prev_city"]
        assert previous["state"] == data["prev_state"]
        assert previous["zip_code"] == data["prev_zip_code"]

    with allure.step("Fill Profile Details"):
        assert cp.get_status_options() == HPLAN_STATUSES
        cp.select_status(data["status"])
        expect(cp.status_dropdown).to_have_value(data["status"])
        expect(cp.start_date).not_to_have_value("")
        cp.select_assigned_to(ASSIGNED_TO)
        cp.select_referred_by(REFERRED_BY)
        expect(cp.referred_by).to_have_value(REFERRED_BY)

    with allure.step("Fill Portal Settings"):
        cp.enable_portal_access()
        expect(cp.portal_access_toggle).to_be_checked()
        expect(cp.portal_settings_heading).to_be_visible()
        expect(cp.resend_login_button).to_be_disabled()
        expect(cp.client_user_id).to_have_value(data["email"])
        expect(cp.agreement).to_have_value(AGREEMENT)
        expect(cp.portal_language).to_have_value(PORTAL_LANGUAGE)

    with allure.step("Submit and verify client is created"):
        expect(cp.submit_button).to_be_enabled()
        cp.submit_form()
        if cp.confirm_save_button.is_visible():
            cp.confirm_save_button.click()
        cp.expect_success_toaster()

    with allure.step("Verify client appears in the Clients list"):
        full_name = f"{data['first_name']} {data['last_name']}"
        print(f"\nCreated client: {full_name} ({data['email']})")
        cp.navigate_to_clients()
        search = cp.page.get_by_label("Search name or email")
        search.fill(data["email"])
        search.press("Enter")
        # The grid truncates long names (e.g. "Auto Client17939 Jr"), so match the prefix;
        # the email search already narrows the grid to this one client.
        name_pattern = re.compile(rf"^{data['first_name']} Client\d+")
        expect(cp.page.get_by_role("link", name=name_pattern)).to_be_visible(timeout=30000)
        details_row = cp.client_grid_rows.filter(has_text=ASSIGNED_TO)
        expect(details_row).to_have_count(1)
        expect(details_row).to_contain_text(data["status"])
