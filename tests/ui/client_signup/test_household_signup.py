"""
Household Signup Funnel E2E Test — Get Credit Help Now (QA tenant)
=================================================================
End-to-end happy path through the public signup funnel with the
Individual/Household plan toggle enabled:

  1. Open /start and submit the lead form
  2. Enable the Household Plan toggle and select the FIRST plan
  3. Fill every checkout field — primary client, additional household
     member, payment — tick the last checkbox, and submit
  4. Sign the service agreement
  5. Set the SecureClientAccess portal password (Test@1234)

Fresh, unique emails are generated per run (one for the primary client, one
for the additional member) so re-running the test does not collide with an
already-registered account.
"""

import random
import time

import pytest
from faker import Faker

from crc_automation.pages.household_signup_page import HouseholdSignupPage

fake = Faker("en_US")

PORTAL_PASSWORD = "Test@1234"
FIRST_NAME = "HH"
CARD_EXPIRY = "12/30"  # any future MM/YY

# Standard payment-gateway test cards; one is chosen at random per execution.
CARDS = [
    "4111111111111111",
    "5555555555554444",
    "378282246310005",
    "6011111111111117",
]


def _unique_email(prefix: str) -> str:
    """e.g. hh-1788835440@yopmail.com — unique disposable-inbox address."""
    return f"{prefix}-{int(time.time())}@yopmail.com"


def _dynamic_phone() -> str:
    """Random NANP number within the reserved 555-0100..0199 test range."""
    return f"4155550{random.randint(100, 199)}"


def _cvv_for(card: str) -> str:
    """Amex (15-digit, starts 34/37) uses a 4-digit CVV; everything else 3."""
    return "1234" if card.startswith(("34", "37")) else "123"


@pytest.mark.smoke
@pytest.mark.ui
def test_complete_household_signup_flow(fresh_page):
    signup = HouseholdSignupPage(fresh_page)

    email = _unique_email("hh")
    last_name = fake.last_name()
    phone = _dynamic_phone()
    ssn = fake.ssn()                # random, format-valid US SSN per run
    card = random.choice(CARDS)     # random test card per execution
    cvv = _cvv_for(card)

    # ── Step 1: Submit the lead form ─────────────────────────
    signup.navigate_to_start()
    signup.fill_lead_form(FIRST_NAME, last_name, email, phone)
    signup.submit_lead_form()
    assert "/show-plans" in fresh_page.url, (
        f"Lead form did not advance to plan selection. URL: {fresh_page.url}"
    )

    # ── Step 2: Enable the household toggle, take the 1st plan ─
    signup.enable_household_toggle()
    signup.select_first_plan()
    assert "/checkout" in fresh_page.url, (
        f"Plan selection did not advance to checkout. URL: {fresh_page.url}"
    )

    # ── Step 3: Fill every detail, tick the last checkbox, submit ─
    signup.fill_primary_details(
        dob="01/15/1990",
        ssn=ssn,
        street="123 Main Street",
        city="Los Angeles",
        state="California",
        zip_code="90001",
    )
    signup.fill_additional_member(
        first_name="Member",
        last_name=fake.last_name(),
        email=_unique_email("hha"),
        phone=_dynamic_phone(),
        dob="02/20/1992",
        ssn=fake.ssn(),             # the member needs their own SSN
    )
    signup.fill_additional_address(
        street="456 Oak Avenue",
        city="San Diego",
        state="California",
        zip_code="92101",
    )
    signup.fill_payment_details(card_number=card, expiry=CARD_EXPIRY, cvv=cvv)
    # accept_household_acknowledgement() ticks the last checkbox before submit.
    signup.submit_household_checkout()
    assert "/agreement" in fresh_page.url, (
        f"Checkout did not advance to the agreement. URL: {fresh_page.url}"
    )

    # ── Step 4: Sign the agreement ───────────────────────────
    signup.sign_agreement()
    assert "/checkout-success" in fresh_page.url, (
        f"Agreement was not accepted. URL: {fresh_page.url}"
    )

    # ── Step 5: Set the portal password ──────────────────────
    signup.go_to_set_password()
    signup.set_password(PORTAL_PASSWORD)
    # This QA tenant hands off to its own SecureClientAccess host, so assert on
    # the portal home path rather than a hard-coded environment URL.
    assert "secureclientaccess.com/home" in fresh_page.url, (
        f"Password setup did not land on the SecureClientAccess home. "
        f"URL: {fresh_page.url}"
    )


@pytest.mark.smoke
@pytest.mark.ui
def test_singleclient_household_signup_flow(fresh_page):
    """
    Same funnel, but the household discount is declined at checkout.

    The Household Plan toggle is still enabled on /show-plans, so checkout
    opens in household mode with the "Household Discount" option ticked. Here
    it is unticked, which collapses the additional member's contact and
    address blocks — leaving a single-client order — and the remaining steps
    (agreement → set portal password) are unchanged.
    """
    signup = HouseholdSignupPage(fresh_page)

    email = _unique_email("sc")
    last_name = fake.last_name()
    phone = _dynamic_phone()
    ssn = fake.ssn()
    card = random.choice(CARDS)
    cvv = _cvv_for(card)

    # ── Step 1: Submit the lead form ─────────────────────────
    signup.navigate_to_start()
    signup.fill_lead_form(FIRST_NAME, last_name, email, phone)
    signup.submit_lead_form()
    assert "/show-plans" in fresh_page.url, (
        f"Lead form did not advance to plan selection. URL: {fresh_page.url}"
    )

    # ── Step 2: Enable the household toggle, take the 1st plan ─
    signup.enable_household_toggle()
    signup.select_first_plan()
    assert "/checkout" in fresh_page.url, (
        f"Plan selection did not advance to checkout. URL: {fresh_page.url}"
    )

    # ── Step 3: Decline the discount, fill the single client, submit ─
    # Unticking the discount hides the additional client and address blocks
    # (asserted inside uncheck_household_discount), so only the primary
    # client's details are entered below.
    signup.uncheck_household_discount()
    signup.fill_primary_details(
        dob="01/15/1990",
        ssn=ssn,
        street="123 Main Street",
        city="Los Angeles",
        state="California",
        zip_code="90001",
    )
    signup.fill_payment_details(card_number=card, expiry=CARD_EXPIRY, cvv=cvv)
    signup.submit_household_checkout()
    assert "/agreement" in fresh_page.url, (
        f"Checkout did not advance to the agreement. URL: {fresh_page.url}"
    )

    # ── Step 4: Sign the agreement ───────────────────────────
    signup.sign_agreement()
    assert "/checkout-success" in fresh_page.url, (
        f"Agreement was not accepted. URL: {fresh_page.url}"
    )

    # ── Step 5: Set the portal password ──────────────────────
    signup.go_to_set_password()
    signup.set_password(PORTAL_PASSWORD)
    assert "secureclientaccess.com/home" in fresh_page.url, (
        f"Password setup did not land on the SecureClientAccess home. "
        f"URL: {fresh_page.url}"
    )
