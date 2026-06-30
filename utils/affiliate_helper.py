"""Reusable helper for creating affiliates in tests."""

from playwright.sync_api import Page
from pages.affiliate_page import AffiliatePage
from utils.fake_data import affiliate_data

STATUS_MAP = {
    "Active": "Active (recommended)",
    "Inactive": "Inactive",
    "Pending": "Pending",
}


def create_affiliate(page: Page, status_label: str, full_details: bool = False) -> tuple[dict, AffiliatePage]:
    """Navigate to Affiliates, open the Add dialog, fill the form, and submit.

    Returns:
        (data, affiliate_page) -- the generated data dict and the AffiliatePage instance.
    """
    ap = AffiliatePage(page)
    ap.navigate_to_affiliates()
    ap.open_add_dialog()

    data = affiliate_data(status_label)

    if full_details:
        ap.fill_full_details(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone=data["phone"],
            mobile=data["mobile"],
            company=data["company"],
            website=data["website"],
            fax=data["fax"],
            phone_ext=data["phone_ext"],
            address=data["address"],
            city=data["city"],
            state=data["state"],
            zip_code=data["zip_code"],
        )
    else:
        ap.fill_required_fields(data["first_name"], data["last_name"], data["email"], data["phone"])

    ap.select_status(STATUS_MAP[status_label])
    ap.submit_form()
    page.wait_for_timeout(3000)

    data["full_name"] = f"{data['first_name']} {data['last_name']}"
    return data, ap


def setup_affiliate(page: Page, status_label: str, full_details: bool = False) -> tuple[dict, AffiliatePage]:
    """Create an affiliate, wait for the toaster to dismiss, and navigate back to the list.

    Use this when the test needs a pre-existing affiliate ready in the table.

    Returns:
        (data, affiliate_page) -- the generated data dict and the AffiliatePage instance.
    """
    data, ap = create_affiliate(page, status_label, full_details=full_details)
    ap.wait_for_toaster_dismiss()
    ap.navigate_to_affiliates()
    return data, ap
