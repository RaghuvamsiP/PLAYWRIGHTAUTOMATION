"""
Signup / Lead-Capture Funnel Page Object
========================================
Covers the public "Get Credit Help Now" signup funnel end-to-end:

    /start            → Lead form (name, email, phone)
    /show-plans       → Plan selection
    /checkout         → Contact info, DOB, SSN, address
    /agreement        → Review & digital signature (jSignature)
    /checkout-success → "Set Up Password" hand-off
    SecureClientAccess→ Create password

A few fields on this funnel need special handling (discovered while
building this flow), so they get dedicated helper methods instead of a
plain `.fill()`:

  * Date of Birth  – a readonly jQuery-UI datepicker; we set it via JS.
  * Social Security – three separate inputs (XXX-XX-XXXX).
  * Street Address – a Google Places Autocomplete box.
  * Signature      – a jSignature HTML5 canvas; we draw on it with real
                     mouse moves and then sync the hidden form fields.
"""

import math
import random

import allure
from playwright.sync_api import Page, expect

from pages.base_page import BasePage
from config.urls import AppURLs


class SignupPage(BasePage):
    # SSN validation messages shown in #errorMessage on the checkout page.
    SSN_ERROR_EMPTY = "Please enter your social security number"
    SSN_ERROR_PARTIAL = (
        "Please enter your full social security number. "
        "Bureaus will reject your submission without a full SSN"
    )

    def __init__(self, page: Page):
        super().__init__(page)

        # ── /start – lead form ───────────────────────────────
        self.first_name_input = page.locator("#inputform")
        self.last_name_input = page.locator("input[name='lastname']")
        self.email_input = page.locator("#home_email")
        self.phone_input = page.get_by_placeholder("(000) 000-0000")
        self.get_started_button = page.get_by_role("button", name="Get Started for $0 Today")

        # ── /show-plans ──────────────────────────────────────
        self.plan_get_started_links = page.get_by_role("link", name="Get Started")

        # ── /checkout – contact + address ────────────────────
        # Direct-checkout variants (e.g. /checkout-1TFFLetter) skip the /start
        # lead form, so the contact fields are rendered on the checkout page
        # itself and start empty. (On the standard funnel they are pre-filled.)
        self.checkout_first_name = page.locator("#first_name")
        self.checkout_last_name = page.locator("#last_name")
        self.checkout_email = page.locator("#email")
        self.checkout_phone = page.locator("#client_pn")
        self.dob_input = page.locator("#dob")
        # Checkout now collects only the LAST FOUR of the SSN: a single numeric
        # field (#last_four_ssn, maxlength=4, type=password) rather than the old
        # three XXX-XX-XXXX segment inputs.
        self.ssn_last_four = page.locator("#last_four_ssn")
        self.street_input = page.get_by_placeholder("Enter a location")
        self.city_input = page.locator("#city")
        self.state_select = page.get_by_role("combobox", name="State")
        self.zip_input = page.locator("#zipcode")
        self.confirm_plan_button = page.get_by_role("button", name="Confirm Plan & Continue")

        # ── /checkout – payment (billing variant) ────────────
        # Card number & CVV are Spreedly-hosted cross-origin iframes; the iframe
        # id has a dynamic numeric suffix, so match on its stable prefix.
        # Cardholder name field id varies by checkout variant: the standard
        # funnel uses #card_holder_name; the direct deep-link checkout uses
        # #full_name. Match whichever is present.
        self.cardholder_input = page.locator("#card_holder_name, #full_name")
        self.card_number_frame = page.frame_locator('iframe[id^="spreedly-number-frame"]')
        self.card_number_field = self.card_number_frame.get_by_role("textbox", name="Card Number")
        self.expiry_input = page.locator("#expiry_date")
        self.cvv_frame = page.frame_locator('iframe[id^="spreedly-cvv-frame"]')
        self.cvv_field = self.cvv_frame.get_by_role("spinbutton", name="CVV")
        # Credit-monitoring consent — a custom-styled checkbox required before
        # Checkout will submit. The real <input> is hidden behind a styled span,
        # so we click the label/checkmark, not the input itself.
        self.credit_monitoring_checkbox = page.locator("#credit_monitoring_checkbox")
        self.credit_monitoring_label = page.locator(
            "label.checkcontainer:has(#credit_monitoring_checkbox)"
        )
        self.checkout_button = page.get_by_role("button", name="Checkout", exact=True)
        # Direct deep-link checkout pages submit via #submit-button — its label
        # varies ("Checkout" on paid variants, "Confirm Plan and Continue" on
        # the free variant), so target the stable id rather than the text.
        self.direct_submit_button = page.locator("#submit-button")

        # Inline form-level validation message (jQuery #errorMessage container).
        self.error_message = page.locator("#errorMessage")

        # ── /agreement ───────────────────────────────────────
        self.signature_canvas = page.locator("canvas.jSignature")
        self.agreement_submit_button = page.get_by_role("button", name="Submit")

        # ── /checkout-success ────────────────────────────────
        self.set_up_password_link = page.get_by_role("link", name="Set Up Password")

        # ── SecureClientAccess – create password ─────────────
        self.new_password_input = page.get_by_role("textbox", name="New Password*", exact=True)
        self.confirm_password_input = page.get_by_role("textbox", name="Confirm new password*")
        self.set_password_button = page.get_by_role("button", name="Set Password")

    # ════════════════════════════════════════════════════════
    # Step 1 – Lead form
    # ════════════════════════════════════════════════════════
    @allure.step("Open signup start page")
    def navigate_to_start(self):
        response = self.page.goto(
            AppURLs.Signup.START, wait_until="domcontentloaded", timeout=60000
        )
        # The start page itself intermittently 500s on this QA env — fail fast
        # with the body instead of a confusing "fill timed out" later.
        if response is not None and response.status >= 400:
            self._raise_on_error(response, "GET /start")

    @allure.step("Fill lead form for {first_name} {last_name}")
    def fill_lead_form(self, first_name: str, last_name: str, email: str, phone: str):
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.email_input.fill(email)
        # The phone box is an input-mask: bulk .fill() gets dropped and the mask
        # reports the field as non-editable, so focus it and type via the keyboard.
        self.phone_input.click()
        self.page.keyboard.type(phone, delay=50)

    @allure.step("Submit lead form")
    def submit_lead_form(self):
        self.get_started_button.click()
        self.page.wait_for_url("**/show-plans/**", timeout=30000)

    # ════════════════════════════════════════════════════════
    # Step 2 – Select a plan
    # ════════════════════════════════════════════════════════
    @allure.step("Select plan #{index} (0-based)")
    def select_plan(self, index: int = 1):
        """Plans are rendered left→right; index is 0-based."""
        self.plan_get_started_links.nth(index).click()
        self.page.wait_for_url("**/checkout/**", timeout=30000)

    @allure.step("Count available plans")
    def plan_count(self) -> int:
        """Number of plans on /show-plans (the funnel shows between 1 and 3)."""
        self.plan_get_started_links.first.wait_for(state="visible", timeout=30000)
        return self.plan_get_started_links.count()

    @allure.step("Select a random plan")
    def select_random_plan(self) -> int:
        """
        Pick a random plan from whatever is on offer (1–3 plans) and proceed.
        Returns the 0-based index that was selected.
        """
        count = self.plan_count()
        assert 1 <= count <= 3, f"Expected between 1 and 3 plans, but found {count}"
        index = random.randrange(count)
        allure.attach(
            f"Plans available: {count}; randomly selected index: {index}",
            name="Plan selection",
            attachment_type=allure.attachment_type.TEXT,
        )
        self.select_plan(index)
        return index

    # ════════════════════════════════════════════════════════
    # Step 3 – Checkout / contact info
    # ════════════════════════════════════════════════════════
    @allure.step("Open checkout directly: {url}")
    def navigate_to_checkout(self, url: str):
        """Go straight to a checkout page (e.g. /checkout-1TFFLetter), bypassing
        the lead form and plan selection. Fail fast with the body if it errors."""
        response = self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
        if response is not None and response.status >= 400:
            self._raise_on_error(response, f"GET {url}")

    @allure.step("Fill checkout contact info for {first_name} {last_name}")
    def fill_checkout_contact(self, first_name: str, last_name: str,
                              email: str, phone: str):
        """Fill the contact fields rendered on a direct-checkout page.

        The phone box is an input-mask: a bulk .fill() gets dropped, so focus it
        and type via the keyboard (same handling as the lead form).
        """
        self.checkout_first_name.fill(first_name)
        self.checkout_last_name.fill(last_name)
        self.checkout_email.fill(email)
        self.checkout_phone.click()
        self.page.keyboard.type(phone, delay=50)

    @allure.step("Set date of birth: {dob}")
    def set_date_of_birth(self, dob: str):
        """#dob is a readonly datepicker input — set its value via JS and fire events."""
        self.page.evaluate(
            """(value) => {
                const el = document.querySelector('#dob');
                el.removeAttribute('readonly');
                el.value = value;
                el.dispatchEvent(new Event('input',  { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }""",
            dob,
        )

    @allure.step("Fill SSN (last 4)")
    def fill_ssn(self, ssn: str):
        """
        Checkout only collects the LAST FOUR SSN digits. Accepts a full 9-digit
        SSN (with or without dashes) or a 4-digit value; either way only the last
        four digits are entered.
        """
        digits = ssn.replace("-", "").strip()
        self.ssn_last_four.fill(digits[-4:])

    # ── SSN validation helpers ───────────────────────────────
    @allure.step("Set SSN last-four box: '{value}'")
    def set_ssn(self, value: str = ""):
        """Set the last-four SSN box directly (empty value clears it)."""
        self.ssn_last_four.fill(value)

    def clear_ssn(self):
        self.set_ssn("")

    def ssn_has_error(self) -> bool:
        """True if the last-four SSN box currently carries the 'error' class."""
        return self.ssn_last_four.evaluate(
            "el => el.classList.contains('error')"
        )

    def type_into_ssn(self, text: str) -> str:
        """Type into the SSN box (respecting its maxlength) and return its value."""
        self.ssn_last_four.fill("")
        self.ssn_last_four.press_sequentially(text)
        return self.ssn_last_four.input_value()

    @allure.step("Click Checkout (expecting client-side validation to block)")
    def click_checkout_expecting_validation(self, settle_ms: int = 4000):
        """
        Click Checkout without waiting for navigation — used for validation tests.
        Waits `settle_ms` (default 4s) afterwards so each validation message has
        time to render before it is asserted.
        """
        self.checkout_button.click()
        self.page.wait_for_timeout(settle_ms)

    def get_error_message(self) -> str:
        return self.error_message.inner_text().strip()

    @allure.step("Fill address")
    def fill_address(self, street: str, city: str, state: str, zip_code: str, apt: str = ""):
        # Street is a Google Places Autocomplete. Type it, then dismiss the
        # suggestion dropdown so it doesn't overwrite the fields we set next.
        self.street_input.click()
        self.street_input.press_sequentially(street)
        try:
            suggestion = self.page.locator(".pac-item").first
            suggestion.wait_for(state="visible", timeout=4000)
            suggestion.click()
        except Exception:
            # Autocomplete unavailable (e.g. offline) — just dismiss it.
            self.page.keyboard.press("Escape")

        if apt:
            self.page.get_by_role("textbox", name="Apt., suit, or unit (optional)").fill(apt)

        # Set these AFTER the autocomplete selection so they are authoritative.
        self.city_input.fill(city)
        self.state_select.select_option(label=state)
        self.zip_input.fill(zip_code)

    @allure.step("Fill checkout form")
    def fill_checkout_form(self, dob: str, ssn: str, street: str, city: str,
                           state: str, zip_code: str, apt: str = ""):
        self.set_date_of_birth(dob)
        self.fill_ssn(ssn)
        self.fill_address(street, city, state, zip_code, apt)

    @allure.step("Fill payment / card details")
    def fill_payment_details(self, card_number: str, expiry: str, cvv: str,
                             cardholder: str = ""):
        """
        Fill the Spreedly-hosted payment fields on the billing checkout variant.
          card_number – digits only (e.g. '4111111111111111')
          expiry      – 'MM/YY' (e.g. '12/30')
          cvv         – 3 digits (4 for Amex)
          cardholder  – optional; the form auto-fills this from the lead name.
        """
        if cardholder:
            self.cardholder_input.fill(cardholder)

        # Card number lives in a cross-origin Spreedly iframe — type into it.
        self.card_number_field.click()
        self.card_number_field.press_sequentially(card_number, delay=30)

        # Expiration is a normal masked input on the parent page.
        self.expiry_input.click()
        self.page.keyboard.type(expiry, delay=50)

        # CVV is a second cross-origin Spreedly iframe.
        self.cvv_field.click()
        self.cvv_field.press_sequentially(cvv, delay=30)

    @allure.step("Accept credit-monitoring consent")
    def accept_credit_monitoring(self):
        """Tick the '$15.00 credit monitoring account' consent checkbox.

        The <input> is visually hidden behind a styled checkmark, so a plain
        .check() can't reach it — click the surrounding label (which toggles
        the input via its label association). Fall back to a JS-driven toggle
        if the click somehow doesn't register.

        No-ops if the checkbox isn't present, so this is safe to call from the
        shared submit path for both checkout variants.
        """
        if self.credit_monitoring_checkbox.count() == 0:
            return
        if self.credit_monitoring_checkbox.is_checked():
            return
        self.credit_monitoring_label.click()
        if not self.credit_monitoring_checkbox.is_checked():
            # Fallback: set checked directly and fire the change event the
            # page's validation listens for.
            self.page.evaluate(
                """() => {
                    const el = document.querySelector('#credit_monitoring_checkbox');
                    el.checked = true;
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }"""
            )
        expect(self.credit_monitoring_checkbox).to_be_checked()

    @allure.step("Confirm plan and continue")
    def confirm_plan(self):
        """Submit the no-payment checkout ('Confirm Plan & Continue' button)."""
        self._submit_checkout(self.confirm_plan_button)

    @allure.step("Submit checkout (with payment)")
    def submit_checkout(self):
        """Submit the billing checkout ('Checkout' button)."""
        self._submit_checkout(self.checkout_button)

    @allure.step("Submit direct checkout")
    def submit_direct_checkout(self):
        """Submit a deep-link checkout page (e.g. /checkout-1TFFLetter, paid, or
        /checkout-LaunchSpecialFREECreditRepair, free).

        Unlike the standard funnel — which POSTs /checkout and lets the server
        redirect to /agreement — these variants POST JSON to /customer-checkout
        and, on success (HTTP 200), do a client-side redirect to
        /agreement/<agreement>/<customer_id>/<plan_id>. A validation failure
        comes back as 422 with the message in the JSON body, so fail fast on it.
        """
        self.accept_credit_monitoring()
        with self.page.expect_response(
            lambda r: r.request.method == "POST" and "/customer-checkout" in r.url,
            timeout=30000,
        ) as checkout_info:
            self.direct_submit_button.click()
        self._raise_on_error(checkout_info.value, "POST /customer-checkout")
        self.page.wait_for_url("**/agreement/**", timeout=30000)

    def _submit_checkout(self, button):
        # Both checkout variants require the credit-monitoring consent before
        # the page will submit.
        self.accept_credit_monitoring()
        # Submitting fires POST /checkout and then loads GET /agreement. Both can
        # intermittently 500, so listen for the /agreement page load first (outer)
        # and the /checkout POST (inner) before clicking, to avoid any race, and
        # fail fast with the response body on whichever breaks.
        with self.page.expect_response(
            lambda r: r.request.method == "GET" and "/agreement/" in r.url,
            timeout=30000,
        ) as agreement_info:
            with self.page.expect_response(
                lambda r: r.request.method == "POST" and r.url.rstrip("/").endswith("/checkout"),
                timeout=30000,
            ) as checkout_info:
                button.click()
            self._raise_on_error(checkout_info.value, "POST /checkout")
        self._raise_on_error(agreement_info.value, "GET /agreement")
        self.page.wait_for_url("**/agreement/**", timeout=30000)

    # ════════════════════════════════════════════════════════
    # Step 4 – Review & sign agreement
    # ════════════════════════════════════════════════════════
    @allure.step("Draw and submit digital signature")
    def sign_agreement(self):
        """
        The signature is a jSignature HTML5 canvas. We draw a stroke with real
        mouse moves (synthetic events don't register), then copy the signature
        data into the hidden form fields the backend reads, and submit.
        """
        self.signature_canvas.scroll_into_view_if_needed()
        box = self.signature_canvas.bounding_box()
        assert box, "Signature canvas not found / not visible"

        start_x = box["x"] + 30
        mid_y = box["y"] + box["height"] / 2
        steps = 60

        self.page.mouse.move(start_x, mid_y)
        self.page.mouse.down()
        for i in range(1, steps + 1):
            x = box["x"] + 30 + (i / steps) * (box["width"] - 60)
            y = mid_y + 35 * math.sin(i / 4)
            self.page.mouse.move(x, y)
        self.page.mouse.up()

        # Sync the jSignature data into the hidden inputs the server validates.
        self.page.evaluate(
            """() => {
                const $ = window.jQuery;
                const c = $('canvas.jSignature').first();
                const base30 = c.jSignature('getData', 'base30');
                const image  = c.jSignature('getData', 'image');
                const b30 = Array.isArray(base30) ? base30.join(',') : base30;
                const img = Array.isArray(image)  ? image.join(',')  : image;
                const h30 = document.querySelector('#signature_content30');
                const hc  = document.querySelector('#signature_content');
                if (h30) { h30.value = b30; h30.dispatchEvent(new Event('change', { bubbles: true })); }
                if (hc)  { hc.value  = img; hc.dispatchEvent(new Event('change', { bubbles: true })); }
            }"""
        )

        # The submit fires POST /saveAgreement and, on success, loads the GET
        # /checkout-success page. Both endpoints intermittently 500 on this
        # funnel, so listen for both (nested, before clicking) and fail fast with
        # the body on whichever breaks — instead of a misleading later timeout.
        with self.page.expect_response(
            lambda r: r.request.method == "GET" and "/checkout-success/" in r.url,
            timeout=30000,
        ) as success_info:
            with self.page.expect_response(
                lambda r: r.request.method == "POST" and r.url.rstrip("/").endswith("/saveAgreement"),
                timeout=30000,
            ) as save_info:
                self.agreement_submit_button.click()
            self._raise_on_error(save_info.value, "POST /saveAgreement")
        self._raise_on_error(success_info.value, "GET /checkout-success")

        self.page.wait_for_url("**/checkout-success/**", timeout=30000)

    def _raise_on_error(self, response, label: str):
        """Attach the body and raise a clear AssertionError if response is >= 400."""
        if response.status < 400:
            return
        try:
            body = response.text()[:5000]
        except Exception:
            body = "<body unavailable — see HAR>"
        allure.attach(
            f"{label}\n{response.url}\nStatus: {response.status}\n\n{body}",
            name=f"Error response: {label}",
            attachment_type=allure.attachment_type.TEXT,
        )
        raise AssertionError(
            f"{label} returned {response.status}. "
            f"Response body (truncated): {body[:500]}"
        )

    # ════════════════════════════════════════════════════════
    # Step 5 – Set password (SecureClientAccess)
    # ════════════════════════════════════════════════════════
    @allure.step("Go to Set Up Password page")
    def go_to_set_password(self):
        self.set_up_password_link.click()
        self.page.wait_for_url("**secureclientaccess.com/**", timeout=30000)

    @allure.step("Set portal password")
    def set_password(self, password: str):
        self.new_password_input.fill(password)
        self.confirm_password_input.fill(password)
        expect(self.set_password_button).to_be_enabled()
        self.set_password_button.click()
        # Lands on the SCA portal home once the password is accepted.
        self.page.wait_for_url("**secureclientaccess.com/home", timeout=30000)

    # ════════════════════════════════════════════════════════
    # Convenience: run the whole funnel
    # ════════════════════════════════════════════════════════
    @allure.step("Complete the full signup funnel")
    def complete_signup(self, *, first_name, last_name, email, phone,
                        dob, ssn, street, city, state, zip_code,
                        password, plan_index=1, apt=""):
        self.navigate_to_start()
        self.fill_lead_form(first_name, last_name, email, phone)
        self.submit_lead_form()
        self.select_plan(plan_index)
        self.fill_checkout_form(dob, ssn, street, city, state, zip_code, apt)
        self.confirm_plan()
        self.sign_agreement()
        self.go_to_set_password()
        self.set_password(password)
