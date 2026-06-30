"""
Login Page Tests — Credit Repair Cloud QA
==========================================
Scenarios:
  1. Valid login & redirect to home
  2. Login → Logout flow
  3. UI elements visibility (fields, buttons, titles, links)
  4. reCAPTCHA with invalid credentials
  5. reCAPTCHA after invalid → valid credentials
  6. Footer visibility
  7. Copyright year validation
  8. Validation messages / toaster with invalid details
  9. Link & button redirections (except login)
  10. Max character length for userid & password
  11. Asterisk on required fields
  12. Chatbot presence
  13. Successful login redirects to Home
"""

from datetime import datetime

import allure
import pytest
from faker import Faker
from playwright.sync_api import expect

from pages.login_page import LoginPage
from config.settings import BASE_URL, DEFAULT_EMAIL, DEFAULT_PASSWORD
from config.urls import AppURLs

fake = Faker()

ERROR_TOAST_TEXT = "Sorry wrong Email/User ID or Password try again"


# ═══════════════════════════════════════════════
# POSITIVE / SMOKE TESTS
# ═══════════════════════════════════════════════

@allure.feature("Login Page")
@allure.story("Authentication")
@allure.title("Valid credentials login redirects to Home page")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
def test_valid_login_redirects_to_home(fresh_page):
    """Scenario 1 & 13: User logs in with valid credentials and lands on Home page."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()
    login.login(DEFAULT_EMAIL, DEFAULT_PASSWORD)
    login.wait_for_home_page()

    on_home = login.is_on_home_page()
    assert on_home, (
        f"Expected to be on home page after valid login, "
        f"but current URL is: {fresh_page.url}"
    )


@allure.feature("Login Page")
@allure.story("Authentication")
@allure.title("User can logout after successful login")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
def test_login_and_logout(fresh_page):
    """Scenario 2: Login → click Personal (admin) → Log Out → verify back on login page."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()
    login.login(DEFAULT_EMAIL, DEFAULT_PASSWORD)
    login.wait_for_home_page()

    login.logout()

    fresh_page.wait_for_url(f"**{AppURLs.Auth.LOGIN}", timeout=15000)
    assert AppURLs.Auth.LOGIN in fresh_page.url, (
        f"Expected to be redirected to login page after logout, "
        f"but current URL is: {fresh_page.url}"
    )


@allure.feature("Login Page")
@allure.story("UI Elements")
@allure.title("Base URL redirects to login page and heading is visible")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
def test_page_heading_visible(fresh_page):
    """Scenario 3: Opening base URL redirects to /app/login and 'Hello again!' heading is displayed."""
    login = LoginPage(fresh_page)
    login.navigate(BASE_URL)

    fresh_page.wait_for_url(f"**{AppURLs.Auth.LOGIN}", timeout=10000)
    assert AppURLs.Auth.LOGIN in fresh_page.url, (
        f"Base URL ({BASE_URL}) did not redirect to login page. "
        f"Current URL: {fresh_page.url}"
    )

    try:
        expect(login.page_heading).to_be_visible()
    except AssertionError:
        raise AssertionError(
            "'Hello again!' heading is not visible on the login page. "
            f"Current URL: {fresh_page.url}"
        )


@allure.feature("Login Page")
@allure.story("UI Elements")
@allure.title("Page title is 'Credit Repair Cloud'")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.sanity
def test_page_title(fresh_page):
    """Scenario 3: Verify page title."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    expect(fresh_page).to_have_title("Credit Repair Cloud")


@allure.feature("Login Page")
@allure.story("UI Elements")
@allure.title("'Team Member Login' label is visible")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.sanity
def test_team_member_label_visible(fresh_page):
    """Scenario 3: Verify 'Team Member Login' label is displayed."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    try:
        expect(login.team_member_label).to_be_visible()
    except AssertionError:
        raise AssertionError(
            "'Team Member Login' label is not visible on the login page. "
            f"Current URL: {fresh_page.url}"
        )


@allure.feature("Login Page")
@allure.story("UI Elements")
@allure.title("Email and Password fields are visible and enabled")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
def test_email_and_password_fields_visible_and_enabled(fresh_page):
    """Scenario 3: Verify email & password fields are visible and enabled."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    try:
        expect(login.email_input).to_be_visible()
        expect(login.email_input).to_be_enabled()
    except AssertionError:
        raise AssertionError(
            "Email input field is not visible or not enabled. "
            f"Current URL: {fresh_page.url}"
        )

    try:
        expect(login.password_input).to_be_visible()
        expect(login.password_input).to_be_enabled()
    except AssertionError:
        raise AssertionError(
            "Password input field is not visible or not enabled. "
            f"Current URL: {fresh_page.url}"
        )


@allure.feature("Login Page")
@allure.story("UI Elements")
@allure.title("Login button is visible and enabled")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
def test_login_button_visible_and_enabled(fresh_page):
    """Scenario 3: Verify Login button is visible and enabled."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    try:
        expect(login.login_button).to_be_visible()
        expect(login.login_button).to_be_enabled()
    except AssertionError:
        raise AssertionError(
            "Login button is not visible or not enabled. "
            f"Current URL: {fresh_page.url}"
        )


@allure.feature("Login Page")
@allure.story("UI Elements")
@allure.title("CRC logo is visible")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.sanity
def test_logo_visible(fresh_page):
    """Scenario 3: Verify CRC logo is displayed."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    try:
        expect(login.logo).to_be_visible()
    except AssertionError:
        raise AssertionError(
            "CRC logo is not visible on the login page. "
            f"Current URL: {fresh_page.url}"
        )


@allure.feature("Login Page")
@allure.story("UI Elements")
@allure.title("'Forgot password?' link is visible")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.sanity
def test_forgot_password_link_visible(fresh_page):
    """Scenario 3: Verify 'Forgot password?' link is visible."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    try:
        expect(login.forgot_password_link).to_be_visible()
    except AssertionError:
        raise AssertionError(
            "'Forgot password?' link is not visible. "
            f"Current URL: {fresh_page.url}"
        )


@allure.feature("Login Page")
@allure.story("UI Elements")
@allure.title("'Sign Up' link is visible")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.sanity
def test_sign_up_link_visible(fresh_page):
    """Scenario 3: Verify 'Sign Up' link is visible."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    try:
        expect(login.sign_up_link).to_be_visible()
    except AssertionError:
        raise AssertionError(
            "'Sign Up' link is not visible on the login page. "
            f"Current URL: {fresh_page.url}"
        )


@allure.feature("Login Page")
@allure.story("UI Elements")
@allure.title("'Don't have an account?' text is visible")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.sanity
def test_dont_have_account_text_visible(fresh_page):
    """Scenario 3: Verify 'Don't have an account?' text is displayed."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    try:
        expect(login.dont_have_account_text).to_be_visible()
    except AssertionError:
        raise AssertionError(
            "'Don't have an account?' text is not visible. "
            f"Current URL: {fresh_page.url}"
        )


@allure.feature("Login Page")
@allure.story("UI Elements")
@allure.title("'Join Our Free Training Sessions!' link is visible")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.sanity
def test_training_link_visible(fresh_page):
    """Scenario 3: Verify training sessions link is visible."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    try:
        expect(login.training_link).to_be_visible()
    except AssertionError:
        raise AssertionError(
            "'Join Our Free Training Sessions!' link is not visible. "
            f"Current URL: {fresh_page.url}"
        )


@allure.feature("Login Page")
@allure.story("Footer")
@allure.title("Footer security text and copyright are visible")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.sanity
def test_footer_visible(fresh_page):
    """Scenario 6: Verify footer with security text and copyright is visible."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    try:
        expect(login.footer_security_text).to_be_visible()
    except AssertionError:
        raise AssertionError(
            "Footer 'Secure Area' text is not visible. "
            f"Current URL: {fresh_page.url}"
        )

    try:
        expect(login.footer_copyright_text).to_be_visible()
    except AssertionError:
        raise AssertionError(
            "Footer copyright text is not visible. "
            f"Current URL: {fresh_page.url}"
        )


@allure.feature("Login Page")
@allure.story("Footer")
@allure.title("Copyright year in footer matches current year")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.sanity
def test_copyright_year_is_current(fresh_page):
    """Scenario 7: Verify copyright year in footer matches the current year."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    current_year = str(datetime.now().year)
    footer_year = login.get_footer_copyright_year()

    assert footer_year == current_year, (
        f"Copyright year in footer is '{footer_year}', "
        f"but expected current year '{current_year}'."
    )


@allure.feature("Login Page")
@allure.story("Link Redirections")
@allure.title("'Sign Up' link points to pricing page")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.sanity
def test_sign_up_link_href(fresh_page):
    """Scenario 9: Verify 'Sign Up' link href points to pricing page."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    expect(login.sign_up_link).to_have_attribute(
        "href", "https://www.creditrepaircloud.com/pricing"
    )


@allure.feature("Login Page")
@allure.story("Link Redirections")
@allure.title("'Sign Up' link opens pricing page in a new tab")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.sanity
def test_sign_up_link_opens_in_new_tab(fresh_page):
    """Scenario 9: Clicking 'Sign Up' opens the pricing page in a new browser tab."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    with fresh_page.context.expect_page() as new_page_info:
        login.sign_up_link.click()

    new_tab = new_page_info.value
    new_tab.wait_for_load_state("domcontentloaded")

    assert "creditrepaircloud.com/pricing" in new_tab.url, (
        f"'Sign Up' link did not open pricing page in new tab. "
        f"New tab URL: {new_tab.url}"
    )
    new_tab.close()


@allure.feature("Login Page")
@allure.story("Link Redirections")
@allure.title("Training link points to training sessions page")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.sanity
def test_training_link_href(fresh_page):
    """Scenario 9: Verify training link href points to training sessions."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    expect(login.training_link).to_have_attribute(
        "href", "https://www.creditrepaircloud.com/training-sessions"
    )


@allure.feature("Login Page")
@allure.story("Link Redirections")
@allure.title("Logo links to main CRC website")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.sanity
def test_logo_link_href(fresh_page):
    """Scenario 9: Verify logo link href points to main website."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    expect(login.logo_link).to_have_attribute(
        "href", "https://www.creditrepaircloud.com/"
    )



@allure.feature("Login Page")
@allure.story("Form Validation")
@allure.title("Asterisk (*) is shown for Email and Password fields")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.sanity
def test_asterisk_on_required_fields(fresh_page):
    """Scenario 11: Verify asterisk (*) indicator is present for required fields."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    try:
        expect(login.email_label).to_be_visible()
    except AssertionError:
        raise AssertionError(
            "Asterisk (*) is not shown for the Email/User ID field. "
            "Expected label to contain 'Email or User ID*'."
        )

    try:
        expect(login.password_label).to_be_visible()
    except AssertionError:
        raise AssertionError(
            "Asterisk (*) is not shown for the Password field. "
            "Expected label to contain 'Password*'."
        )


@allure.feature("Login Page")
@allure.story("UI Elements")
@allure.title("Chatbot (Intercom) is present at bottom right")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.sanity
def test_chatbot_is_present(fresh_page):
    """Scenario 12: Verify chatbot button is visible at the bottom right of login page."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    try:
        expect(login.chatbot_button).to_be_visible(timeout=10000)
    except AssertionError:
        raise AssertionError(
            "Chatbot (Intercom Messenger) button is not visible at the bottom right of the login page. "
            f"Current URL: {fresh_page.url}"
        )


@allure.feature("Login Page")
@allure.story("Keyboard Interaction")
@allure.title("Login using Tab and Enter keys only")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.sanity
def test_login_using_keyboard_tab_and_enter(fresh_page):
    """User types email, Tabs to password, types password, presses Enter to submit."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    login.email_input.click()
    fresh_page.keyboard.type(DEFAULT_EMAIL)
    fresh_page.keyboard.press("Tab")
    fresh_page.keyboard.type(DEFAULT_PASSWORD)
    fresh_page.keyboard.press("Enter")

    login.wait_for_home_page()

    on_home = login.is_on_home_page()
    assert on_home, (
        "Login via keyboard (Tab + Enter) did not redirect to home page. "
        f"Current URL: {fresh_page.url}"
    )


@allure.feature("Login Page")
@allure.story("Keyboard Interaction")
@allure.title("Login by copy-pasting email and password")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.sanity
def test_login_using_copy_paste(fresh_page):
    """User copy-pastes email and password into the fields and logs in."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    # Paste email via clipboard
    fresh_page.evaluate(
        "text => navigator.clipboard.writeText(text)", DEFAULT_EMAIL
    )
    login.email_input.click()
    fresh_page.keyboard.press("ControlOrMeta+v")

    # Paste password via clipboard
    fresh_page.evaluate(
        "text => navigator.clipboard.writeText(text)", DEFAULT_PASSWORD
    )
    login.password_input.click()
    fresh_page.keyboard.press("ControlOrMeta+v")

    login.login_button.click()
    login.wait_for_home_page()

    on_home = login.is_on_home_page()
    assert on_home, (
        "Login via copy-paste did not redirect to home page. "
        f"Current URL: {fresh_page.url}"
    )


# ═══════════════════════════════════════════════
# NEGATIVE TESTS
# ═══════════════════════════════════════════════

@allure.feature("Login Page")
@allure.story("Validation Messages")
@allure.title("Error toast shown for empty credentials")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
def test_error_toast_empty_credentials(fresh_page):
    """Scenario 8: Submitting empty form shows error toast."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()
    login.login_button.click()

    try:
        expect(login.error_toast).to_be_visible(timeout=5000)
    except AssertionError:
        raise AssertionError(
            "Error toast did not appear after clicking Login with empty credentials. "
            f"Current URL: {fresh_page.url}"
        )

    expect(login.error_toast).to_have_text(ERROR_TOAST_TEXT)


@allure.feature("Login Page")
@allure.story("Validation Messages")
@allure.title("Error toast shown for random invalid credentials")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
def test_error_toast_invalid_credentials(fresh_page):
    """Scenario 8: Login with faker-generated invalid credentials shows error toast."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    invalid_email = fake.email()
    invalid_password = fake.password(length=10)
    login.login(invalid_email, invalid_password)

    try:
        expect(login.error_toast).to_be_visible(timeout=5000)
    except AssertionError:
        raise AssertionError(
            f"Error toast did not appear after login with invalid credentials "
            f"({invalid_email}). Current URL: {fresh_page.url}"
        )

    expect(login.error_toast).to_have_text(ERROR_TOAST_TEXT)


@allure.feature("Login Page")
@allure.story("Validation Messages")
@allure.title("Error toast shown for valid email with wrong password")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
def test_error_toast_wrong_password(fresh_page):
    """Scenario 8: Valid email + wrong password shows error toast."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    wrong_password = fake.password(length=12)
    login.login(DEFAULT_EMAIL, wrong_password)

    try:
        expect(login.error_toast).to_be_visible(timeout=5000)
    except AssertionError:
        raise AssertionError(
            f"Error toast did not appear after login with valid email '{DEFAULT_EMAIL}' "
            f"and wrong password. Current URL: {fresh_page.url}"
        )

    expect(login.error_toast).to_have_text(ERROR_TOAST_TEXT)


@allure.feature("Login Page")
@allure.story("Validation Messages")
@allure.title("Error toast shown for empty password")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.sanity
def test_error_toast_empty_password(fresh_page):
    """Scenario 8: Email without password shows error toast."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()
    login.email_input.fill(DEFAULT_EMAIL)
    login.login_button.click()

    try:
        expect(login.error_toast).to_be_visible(timeout=5000)
    except AssertionError:
        raise AssertionError(
            "Error toast did not appear after submitting email without password. "
            f"Current URL: {fresh_page.url}"
        )

    expect(login.error_toast).to_have_text(ERROR_TOAST_TEXT)


@allure.feature("Login Page")
@allure.story("Validation Messages")
@allure.title("Error toast shown for empty email")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.sanity
def test_error_toast_empty_email(fresh_page):
    """Scenario 8: Password without email shows error toast."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()
    login.password_input.fill(fake.password(length=10))
    login.login_button.click()

    try:
        expect(login.error_toast).to_be_visible(timeout=5000)
    except AssertionError:
        raise AssertionError(
            "Error toast did not appear after submitting password without email. "
            f"Current URL: {fresh_page.url}"
        )

    expect(login.error_toast).to_have_text(ERROR_TOAST_TEXT)


@allure.feature("Login Page")
@allure.story("reCAPTCHA")
@allure.title("reCAPTCHA appears after login with invalid credentials")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.sanity
def test_recaptcha_on_invalid_credentials(fresh_page):
    """Scenario 4: reCAPTCHA is triggered after a failed login attempt with invalid details."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    login.login(fake.email(), fake.password(length=10))

    try:
        expect(login.error_toast).to_be_visible(timeout=5000)
    except AssertionError:
        raise AssertionError(
            "Error toast did not appear after invalid login attempt. "
            f"Current URL: {fresh_page.url}"
        )

    recaptcha_shown = login.is_recaptcha_visible()
    assert recaptcha_shown, (
        "reCAPTCHA did not appear after failed login with invalid credentials. "
        "Expected reCAPTCHA to be triggered as a security measure. "
        f"Current URL: {fresh_page.url}"
    )


@allure.feature("Login Page")
@allure.story("reCAPTCHA")
@allure.title("reCAPTCHA blocks form after invalid attempt, even with valid credentials next")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.sanity
def test_recaptcha_blocks_after_invalid_then_valid(fresh_page):
    """Scenario 5: After a failed login, reCAPTCHA blocks further submissions."""
    login = LoginPage(fresh_page)
    login.navigate_to_login()

    # Step 1: Attempt with invalid credentials
    login.login(fake.email(), fake.password(length=10))

    try:
        expect(login.error_toast).to_be_visible(timeout=5000)
    except AssertionError:
        raise AssertionError(
            "Error toast did not appear after first invalid login attempt. "
            f"Current URL: {fresh_page.url}"
        )

    recaptcha_shown = login.is_recaptcha_visible()
    assert recaptcha_shown, (
        "reCAPTCHA did not appear after first failed login. "
        "Cannot verify reCAPTCHA blocking behavior. "
        f"Current URL: {fresh_page.url}"
    )

    # Step 2: Attempt with valid credentials (should be blocked by reCAPTCHA)
    login.email_input.clear()
    login.password_input.clear()
    login.login(DEFAULT_EMAIL, DEFAULT_PASSWORD)

    try:
        expect(login.error_toast).to_be_visible(timeout=5000)
    except AssertionError:
        raise AssertionError(
            "Error toast did not appear after second attempt (expected 'valid captcha' error). "
            f"Current URL: {fresh_page.url}"
        )

    expect(login.error_toast).to_have_text("Please enter valid captcha")
    on_home = login.is_on_home_page()
    assert not on_home, (
        "BUG: Form should not submit while reCAPTCHA is pending. "
        f"User was redirected to: {fresh_page.url}"
    )
