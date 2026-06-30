"""
Checkout SSN Field — Validation Tests
=====================================
Validates the Social Security Number field on the (billing) checkout page.

The SSN is three boxes — XXX-XX-XXXX (maxlength 3 / 2 / 4 = 9 digits total).
The page validates it on the "Checkout" click (not on blur):

  * Empty SSN   -> #errorMessage: "Please enter your social security number"
                   and all three boxes get the 'error' class.
  * Partial SSN -> #errorMessage: "Please enter your full social security
                   number. Bureaus will reject your submission without a full
                   SSN" and the incomplete box(es) get the 'error' class.
  * Full 9-digit SSN -> validation passes (boxes cleared of 'error').

Each scenario is a separate (parametrized) test so it appears as its own row
in the Allure report. SSN validation runs client-side BEFORE any server call,
so these tests never submit to the backend (immune to the funnel's 500s).
"""

import time

import allure
import pytest
from playwright.sync_api import expect

from pages.signup_page import SignupPage

FIRST_NAME = "SSCS CB"
EMPTY_MSG = SignupPage.SSN_ERROR_EMPTY
PARTIAL_MSG = SignupPage.SSN_ERROR_PARTIAL


def _unique_email() -> str:
    return f"sscs.cb.{int(time.time())}@yopmail.com"


def _reach_checkout_with_prerequisites(signup: SignupPage, page, attempts: int = 4):
    """Drive lead -> plan -> checkout, then fill everything EXCEPT the SSN so
    that SSN validation is the gate exercised on Checkout.

    The lead/plan/checkout pages intermittently 500 on this QA env, so retry
    the whole navigation a few times — this is only test setup, not the SSN
    behaviour under test.
    """
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            signup.navigate_to_start()
            signup.fill_lead_form(FIRST_NAME, "Tester", _unique_email(), "4155550132")
            signup.submit_lead_form()
            signup.select_plan(index=0)
            assert "/checkout" in page.url, f"Did not reach checkout. URL: {page.url}"
            # First/Last/Email/Phone are pre-filled from the lead; add DOB +
            # address so the form's "all required fields" gate passes and SSN
            # is what's validated.
            signup.set_date_of_birth("01/15/1990")
            signup.fill_address("123 Main Street", "Los Angeles", "California", "90001")
            return
        except Exception as e:  # noqa: BLE001 — retry transient server/nav blips
            last_error = e
            allure.attach(
                f"Setup attempt {attempt}/{attempts} failed at {page.url}\n{e}",
                name=f"Setup retry {attempt}",
                attachment_type=allure.attachment_type.TEXT,
            )
    raise AssertionError(
        f"Could not reach checkout after {attempts} attempts (QA funnel "
        f"intermittently 500s). Last error: {last_error}"
    )


@pytest.fixture
def checkout(fresh_page):
    """Reach the checkout page with everything filled except the SSN."""
    signup = SignupPage(fresh_page)
    _reach_checkout_with_prerequisites(signup, fresh_page)
    return signup


# ════════════════════════════════════════════════════════════
# Max length — each box accepts only its fixed number of digits
# ════════════════════════════════════════════════════════════
@allure.feature("Signup Funnel")
@allure.story("Checkout — SSN Validation")
@allure.title("SSN box {box} accepts at most {expected!r} (max length)")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
@pytest.mark.negative
@pytest.mark.parametrize(
    "box, typed, expected",
    [
        pytest.param(1, "1234567", "123", id="box1-max-3"),
        pytest.param(2, "9999", "99", id="box2-max-2"),
        pytest.param(3, "1234567", "1234", id="box3-max-4"),
    ],
)
def test_ssn_box_max_length(checkout, box, typed, expected):
    """Only 9 digits total are allowed — each box caps at 3 / 2 / 4 digits."""
    signup = checkout
    assert signup.type_into_ssn_segment(box, typed) == expected, (
        f"SSN box {box} should cap input at '{expected}' but accepted more"
    )


# ════════════════════════════════════════════════════════════
# Empty SSN
# ════════════════════════════════════════════════════════════
@allure.feature("Signup Funnel")
@allure.story("Checkout — SSN Validation")
@allure.title("Empty SSN shows the 'enter your SSN' message")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.negative
def test_ssn_empty_shows_message(checkout):
    signup = checkout
    signup.clear_ssn()
    signup.click_checkout_expecting_validation()  # includes 4s settle wait

    expect(signup.error_message).to_contain_text(EMPTY_MSG)
    assert signup.ssn_segment_has_error(1), "Box 1 should be flagged for empty SSN"
    assert signup.ssn_segment_has_error(2), "Box 2 should be flagged for empty SSN"
    assert signup.ssn_segment_has_error(3), "Box 3 should be flagged for empty SSN"


# ════════════════════════════════════════════════════════════
# Partial SSN — each box empty in turn (same message every time)
# ════════════════════════════════════════════════════════════
@allure.feature("Signup Funnel")
@allure.story("Checkout — SSN Validation")
@allure.title("Partial SSN ({case}) shows the 'full SSN required' message")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.negative
@pytest.mark.parametrize(
    "case, p1, p2, p3, empty_box",
    [
        pytest.param("box 1 empty", "", "45", "6789", 1, id="box1-empty"),
        pytest.param("box 2 empty", "123", "", "6789", 2, id="box2-empty"),
        pytest.param("box 3 empty", "123", "45", "", 3, id="box3-empty"),
    ],
)
def test_ssn_partial_shows_message(checkout, case, p1, p2, p3, empty_box):
    signup = checkout
    signup.set_ssn_parts(p1, p2, p3)
    signup.click_checkout_expecting_validation()  # includes 4s settle wait

    # Same partial message regardless of which box is incomplete.
    expect(signup.error_message).to_contain_text(PARTIAL_MSG)
    assert signup.ssn_segment_has_error(empty_box), (
        f"The empty box (#{empty_box}) should be flagged for partial SSN ({case})"
    )


# ════════════════════════════════════════════════════════════
# Full valid 9-digit SSN
# ════════════════════════════════════════════════════════════
@allure.feature("Signup Funnel")
@allure.story("Checkout — SSN Validation")
@allure.title("Full 9-digit SSN passes validation")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
def test_ssn_full_valid_passes(checkout):
    signup = checkout
    signup.set_ssn_parts("123", "45", "6789")
    signup.click_checkout_expecting_validation()  # includes 4s settle wait

    # validateSsn() passes and clears the 'error' class on every box.
    assert not signup.ssn_segment_has_error(1), "Box 1 should be valid"
    assert not signup.ssn_segment_has_error(2), "Box 2 should be valid"
    assert not signup.ssn_segment_has_error(3), "Box 3 should be valid"
    # And no SSN-specific message is shown (the form moves on past the SSN).
    msg = signup.get_error_message()
    assert EMPTY_MSG not in msg and PARTIAL_MSG not in msg, (
        f"A full 9-digit SSN should not raise an SSN error, but got: {msg!r}"
    )
