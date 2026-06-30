"""
Signup Funnel E2E Test — Get Credit Help Now
============================================
End-to-end happy path through the public signup funnel:

  1. Open /start and submit the lead form
  2. Select a plan
  3. Fill the checkout form (contact, DOB, SSN, address) and confirm
  4. Sign the service agreement
  5. Set the SecureClientAccess portal password (Test@1234)

A fresh, unique email is generated per run so re-running the test does
not collide with an already-registered account.
"""

import time

import pytest
from faker import Faker

from pages.signup_page import SignupPage
from config.urls import AppURLs

fake = Faker("en_US")

PORTAL_PASSWORD = "Test@1234"


FIRST_NAME = "IND"

# Deep-link FREE checkout URL (no payment); bypasses /start and plan selection.
DIRECT_CHECKOUT_URL = "https://sscs7600.stage-leads-new.getcredithelpnow.com/checkout-INDPlan2"



def _unique_email() -> str:
    """e.g. ind.1780480641@yopmail.com — unique disposable-inbox address."""
    return f"ind.{int(time.time())}@yopmail.com"


@pytest.mark.smoke
@pytest.mark.ui
def test_complete_signup_flow(fresh_page):
    signup = SignupPage(fresh_page)

    email = _unique_email()
    first_name = FIRST_NAME
    last_name = fake.last_name()
    phone = "4155550132"  # NANP-valid test number
    ssn = fake.ssn()       # random, format-valid US SSN (AAA-GG-SSSS) per run

    # Step 1: Submit lead form
    signup.navigate_to_start()
    signup.fill_lead_form(first_name, last_name, email, phone)
    signup.submit_lead_form()
    assert "/show-plans" in fresh_page.url, (
        f"Lead form did not advance to plan selection. URL: {fresh_page.url}"
    )

    # Step 2: Select a random plan
    chosen_index = signup.select_random_plan()  # 1–3 plans; pick one at random
    assert "/checkout" in fresh_page.url, (
        f"Plan selection (index {chosen_index}) did not advance to checkout. "
        f"URL: {fresh_page.url}"
    )

    # Step 3: Fill checkout form and confirm
    signup.fill_checkout_form(
        dob="01/15/1990",
        ssn=ssn,
        street="123 Main Street",
        city="Los Angeles",
        state="California",
        zip_code="90001",
    )
    signup.confirm_plan()
    assert "/agreement" in fresh_page.url, (
        f"Checkout did not advance to the agreement. URL: {fresh_page.url}"
    )

    # Step 4: Sign the agreement
    signup.sign_agreement()
    assert "/checkout-success" in fresh_page.url, (
        f"Agreement was not accepted. URL: {fresh_page.url}"
    )

    # Step 5: Set the portal password
    signup.go_to_set_password()
    signup.set_password(PORTAL_PASSWORD)
    assert fresh_page.url.startswith(AppURLs.Signup.SCA_HOME), (
        f"Password setup did not land on the SecureClientAccess home. "
        f"URL: {fresh_page.url}"
    )


@pytest.mark.smoke
@pytest.mark.ui
def test_complete_direct_free_checkout_flow(fresh_page):
    """Deep-link FREE checkout: skip the lead form and plan selection by
    navigating straight to DIRECT_CHECKOUT_URL. There is no payment step; the
    contact fields are entered on the checkout page itself, and the remaining
    steps (agreement → set portal password) are common."""
    signup = SignupPage(fresh_page)

    email = _unique_email()
    first_name = FIRST_NAME
    last_name = fake.last_name()
    phone = "4155550132"  # NANP-valid test number
    ssn = fake.ssn()       # random, format-valid US SSN per run

    # Step 1: Open the deep-link checkout page directly
    signup.navigate_to_checkout(DIRECT_CHECKOUT_URL)

    # Step 2: Fill checkout (contact + address); no payment on this variant
    signup.fill_checkout_contact(first_name, last_name, email, phone)
    signup.fill_checkout_form(
        dob="01/15/1990",
        ssn=ssn,
        street="123 Main Street",
        city="Los Angeles",
        state="California",
        zip_code="90001",
    )
    signup.submit_direct_checkout()
    assert "/agreement" in fresh_page.url, (
        f"Checkout did not advance to the agreement. URL: {fresh_page.url}"
    )

    # Step 3: Sign the agreement
    signup.sign_agreement()
    assert "/checkout-success" in fresh_page.url, (
        f"Agreement was not accepted. URL: {fresh_page.url}"
    )

    # Step 4: Set the portal password
    signup.go_to_set_password()
    signup.set_password(PORTAL_PASSWORD)
    assert fresh_page.url.startswith(AppURLs.Signup.SCA_HOME), (
        f"Password setup did not land on the SecureClientAccess home. "
        f"URL: {fresh_page.url}"
    )
