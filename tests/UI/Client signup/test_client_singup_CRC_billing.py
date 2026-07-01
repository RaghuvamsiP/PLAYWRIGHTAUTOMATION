"""
Signup Funnel E2E Tests — CRC Billing (paid checkout with card)
===============================================================
Both tests below exercise a PAYMENT checkout (Spreedly-hosted card fields).
A random test card is picked from CARDS for each execution, and a fresh
unique email is generated per run so re-runs don't collide.

1) test_complete_billing_signup_flow — the full funnel:
     /start (lead form) → select plan → checkout (contact + address +
     payment) → agreement → set portal password.

2) test_complete_direct_checkout_flow — a deep-link variant that skips the
   lead form and plan selection by navigating straight to a checkout URL
   (CHECKOUT_URL). Because the lead step is bypassed, the contact fields
   (and cardholder name) are entered on the checkout page itself; the
   remaining steps (agreement → set portal password) are common.
"""

import random
import time

import pytest
from faker import Faker

from pages.signup_page import SignupPage
from config.urls import AppURLs

fake = Faker("en_US")

PORTAL_PASSWORD = "Test@1234"
FIRST_NAME = "SSCS CB"
CARD_EXPIRY = "12/30"  # any future MM/YY

# Deep-link checkout URL for the direct-checkout test (bypasses /start).
CHECKOUT_URL = "https://sscs7600.stage-leads-new.getcredithelpnow.com/checkout-NoFWFletter"

# Standard payment-gateway test cards (Visa, Mastercard, Amex, Discover,
# Diners, JCB). One is chosen at random per execution.
CARDS = [
    "4111111111111111",
    "5555555555554444",
    "378282246310005",
    "6011111111111117",
    "30569309025904",
    "3569990010030400",
]


def _b36(n: int) -> str:
    """Compact base-36 encoding of an int (keeps the unique suffix short)."""
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    out = ""
    while n:
        n, r = divmod(n, 36)
        out = chars[r] + out
    return out or "0"


def _unique_email() -> str:
    """e.g. cb-qz4k9p@yopmail.com — short, unique disposable-inbox address."""
    return f"cb-{_b36(int(time.time()))}@yopmail.com"


def _dynamic_phone() -> str:
    """Random NANP number within the reserved 555-0100..0199 test range."""
    return f"4155550{random.randint(100, 199)}"


def _cvv_for(card: str) -> str:
    """Amex (15-digit, starts 34/37) uses a 4-digit CVV; everything else 3."""
    return "1234" if card.startswith(("34", "37")) else "123"


@pytest.mark.smoke
@pytest.mark.ui
def test_complete_billing_signup_flow(fresh_page):
    signup = SignupPage(fresh_page)

    email = _unique_email()
    first_name = FIRST_NAME
    last_name = fake.last_name()
    phone = _dynamic_phone()       # random NANP test number per run
    ssn = fake.ssn()               # random, format-valid US SSN per run
    card = random.choice(CARDS)    # random test card per execution
    cvv = _cvv_for(card)

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

    # Step 3: Fill checkout (contact + address + payment)
    signup.fill_checkout_form(
        dob="01/15/1990",
        ssn=ssn,
        street="123 Main Street",
        city="Los Angeles",
        state="California",
        zip_code="90001",
    )
    signup.fill_payment_details(card_number=card, expiry=CARD_EXPIRY, cvv=cvv)
    signup.submit_checkout()
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
def test_complete_direct_checkout_flow(fresh_page):
    """Deep-link checkout: skip the lead form and plan selection by navigating
    straight to CHECKOUT_URL. Contact fields (and cardholder name) are entered
    on the checkout page itself; the remaining steps are common."""
    signup = SignupPage(fresh_page)

    email = _unique_email()
    first_name = "SSCS 1TFF"
    last_name = fake.last_name()
    phone = _dynamic_phone()       # random NANP test number per run
    ssn = fake.ssn()               # random, format-valid US SSN per run
    card = random.choice(CARDS)    # random test card per execution
    cvv = _cvv_for(card)

    # Step 1: Open the deep-link checkout page directly
    signup.navigate_to_checkout(CHECKOUT_URL)

    # Step 2: Fill checkout (contact + address + payment)
    signup.fill_checkout_contact(first_name, last_name, email, phone)
    signup.fill_checkout_form(
        dob="01/15/1990",
        ssn=ssn,
        street="123 Main Street",
        city="Los Angeles",
        state="California",
        zip_code="90001",
    )
    # Direct checkout skips the lead step, so the cardholder name is not
    # auto-filled — pass it explicitly or Spreedly tokenization will fail.
    signup.fill_payment_details(
        card_number=card,
        expiry=CARD_EXPIRY,
        cvv=cvv,
        cardholder=f"{first_name} {last_name}",
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
