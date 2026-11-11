"""
Household Signup Funnel Page Object
===================================
The QA funnel tenant (rag.qa-leads-new) offers an Individual/Household plan
toggle. Switching it to "Household Plan" re-prices every plan card and appends
`?household=1` to each plan's checkout link, which makes the checkout page
render a second set of fields for the additional family/household member.

    /start            → Lead form (same as the individual funnel)
    /show-plans       → Individual ⇄ Household toggle, then plan selection
    /checkout         → Primary client + ADDITIONAL client + address + payment
    /agreement        → Review & digital signature (jSignature)
    /checkout-success → "Set Up Password" hand-off
    SecureClientAccess→ Create password

Everything from /agreement onwards is identical to the individual funnel, so
this class extends SignupPage and only adds what the household variant needs.

Two checkout differences worth calling out, both discovered by walking the
live page:

  * SSN is collected as the FULL nine digits across three segment inputs
    (#ssn_part1/2/3), not the single last-four box the stage tenant uses.
  * A household acknowledgement checkbox at the bottom of the order summary
    (#household_acknowledgement_checkbox) must be ticked before the page will
    submit. Like the other custom-styled checkboxes on this funnel, the real
    <input> sits behind a styled span, so the label is what gets clicked.
"""

import allure
from playwright.sync_api import Page, expect

from config.urls import AppURLs
from pages.signup_page import SignupPage


class HouseholdSignupPage(SignupPage):
    def __init__(self, page: Page):
        super().__init__(page)

        # ── /show-plans – Individual ⇄ Household toggle ───────
        self.household_toggle = page.locator("#householdToggle")
        # The <input> is hidden behind the styled slider; click the label.
        self.household_switch = page.locator("label.household-switch")
        self.household_banner_yes = page.locator("#householdBannerYes")
        self.household_banner_close = page.locator("#householdBannerClose")

        # ── /checkout – primary client address ───────────────
        # The household checkout renders a SECOND address block for the
        # additional member, so the inherited role-based lookups ("State",
        # "Apt., suit, or unit (optional)") match two elements and trip
        # Playwright's strict mode. Re-bind them to their unique ids.
        self.street_input = page.locator("#street_address")
        self.apt_input = page.locator("#street_address_apt")
        self.state_select = page.locator("#state")

        # ── /checkout – primary client SSN (full 9 digits) ────
        self.ssn_part1 = page.locator("#ssn_part1")
        self.ssn_part2 = page.locator("#ssn_part2")
        self.ssn_part3 = page.locator("#ssn_part3")

        # ── /checkout – additional household member ──────────
        self.additional_first_name = page.locator("#additional_first_name")
        self.additional_last_name = page.locator("#additional_last_name")
        self.additional_email = page.locator("#additional_email")
        self.additional_phone = page.locator("#additional_phone")
        self.additional_dob = page.locator("#additional_dob")
        self.additional_ssn_part1 = page.locator("#additional_ssn_part1")
        self.additional_ssn_part2 = page.locator("#additional_ssn_part2")
        self.additional_ssn_part3 = page.locator("#additional_ssn_part3")
        self.use_same_address_checkbox = page.locator("#use_same_address")
        self.use_same_address_label = page.locator(
            "label.checkcontainer:has(#use_same_address)"
        )
        self.additional_street_input = page.locator("#additional_street_address")
        self.additional_apt_input = page.locator("#additional_street_address_apt")
        self.additional_city_input = page.locator("#additional_city")
        self.additional_state_select = page.locator("#additional_state")
        self.additional_zip_input = page.locator("#additional_zipcode")

        # ── /checkout – order summary + submit ───────────────
        # "Household Discount — Would you like to add a family or household
        # member and see special discount pricing?" in the Total Payment
        # block. Ticked by default when checkout is opened with ?household=1;
        # unticking it collapses the additional member's blocks and prices the
        # plan for a single client.
        self.household_discount_checkbox = page.locator("#household_checkbox")
        self.household_discount_label = page.locator(
            "label.checkcontainer:has(#household_checkbox)"
        )
        # The last checkbox on the page: "I understand that by choosing a
        # household discount plan, my additional member will receive a
        # separate signup email…". Required before checkout will submit.
        self.household_ack_checkbox = page.locator("#household_acknowledgement_checkbox")
        self.household_ack_label = page.locator(
            "label.checkcontainer:has(#household_acknowledgement_checkbox)"
        )
        # This tenant submits via input#submit-button (value="Checkout").
        self.household_submit_button = page.locator("#submit-button")

    # ════════════════════════════════════════════════════════
    # Step 1 – Lead form
    # ════════════════════════════════════════════════════════
    @allure.step("Open household signup start page")
    def navigate_to_start(self):
        """Same lead form as the individual funnel, different tenant host."""
        response = self.page.goto(
            AppURLs.HouseholdSignup.START, wait_until="domcontentloaded", timeout=60000
        )
        if response is not None and response.status >= 400:
            self._raise_on_error(response, "GET /start")

    @allure.step("Submit lead form")
    def submit_lead_form(self):
        """
        Submit and wait for /show-plans.

        The base implementation only waits for the URL, so when this tenant's
        POST /create-lead or the /show-plans page it redirects to 500s (both do,
        intermittently) the run dies 30s later on an unrelated locator. Watch
        both legs and fail fast with the offending response body.
        """
        with self.page.expect_response(
            lambda r: r.request.method == "GET" and "/show-plans/" in r.url,
            timeout=30000,
        ) as plans_info:
            with self.page.expect_response(
                lambda r: r.request.method == "POST" and "/create-lead" in r.url,
                timeout=30000,
            ) as lead_info:
                self.get_started_button.click()
            self._raise_on_error(lead_info.value, "POST /create-lead")
        self._raise_on_error(plans_info.value, "GET /show-plans")
        self.page.wait_for_url("**/show-plans/**", timeout=30000)

    # ════════════════════════════════════════════════════════
    # Step 2 – Household toggle + plan selection
    # ════════════════════════════════════════════════════════
    @allure.step("Enable the Household Plan toggle")
    def enable_household_toggle(self):
        """
        Flip Individual Plan → Household Plan.

        A "Household Discount" promo banner overlaps the toggle on load, so it
        is dismissed first. Falls back to a JS-driven toggle if the label click
        somehow doesn't register.
        """
        try:
            self.household_switch.wait_for(state="visible", timeout=30000)
        except Exception:
            raise AssertionError(
                "The Individual/Household toggle never rendered on "
                f"{self.page.url} — this tenant may not have the household "
                "plan feature enabled."
            )

        if self.household_banner_close.count() and self.household_banner_close.is_visible():
            self.household_banner_close.click()
            self.page.wait_for_timeout(500)

        self.household_switch.click()
        if not self.household_toggle.is_checked():
            self.page.evaluate(
                """() => {
                    const el = document.querySelector('#householdToggle');
                    el.checked = true;
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }"""
            )
        expect(self.household_toggle).to_be_checked()

        # Prices re-render and each plan link gains ?household=1; wait for that
        # rather than a fixed sleep so plan selection can't race the rewrite.
        self.page.wait_for_function(
            """() => Array.from(document.querySelectorAll('a[href*="/checkout/"]'))
                       .every(a => a.getAttribute('href').includes('household=1'))""",
            timeout=15000,
        )

    @allure.step("Select the first household plan")
    def select_first_plan(self):
        """Plans render left→right; the first card is index 0."""
        self.select_plan(0)
        assert "household=1" in self.page.url, (
            "Checkout was opened without the household flag — the toggle did "
            f"not carry through. URL: {self.page.url}"
        )

    # ════════════════════════════════════════════════════════
    # Step 3 – Checkout
    # ════════════════════════════════════════════════════════
    @staticmethod
    def _ssn_digits(ssn: str) -> str:
        digits = "".join(ch for ch in ssn if ch.isdigit())
        assert len(digits) == 9, f"Expected a 9-digit SSN, got {ssn!r}"
        return digits

    @allure.step("Fill full 9-digit SSN")
    def fill_full_ssn(self, ssn: str):
        """This tenant splits the SSN across three inputs: XXX-XX-XXXX."""
        d = self._ssn_digits(ssn)
        self.ssn_part1.fill(d[0:3])
        self.ssn_part2.fill(d[3:5])
        self.ssn_part3.fill(d[5:9])

    @allure.step("Fill additional member SSN")
    def fill_additional_ssn(self, ssn: str):
        d = self._ssn_digits(ssn)
        self.additional_ssn_part1.fill(d[0:3])
        self.additional_ssn_part2.fill(d[3:5])
        self.additional_ssn_part3.fill(d[5:9])

    @allure.step("Fill primary client address")
    def fill_address(self, street: str, city: str, state: str, zip_code: str,
                     apt: str = ""):
        """Same shape as the base funnel — the street box is still a Google
        Places Autocomplete — but every field is addressed by id so the
        additional member's duplicate address block can't be matched instead.
        """
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
            self.apt_input.fill(apt)

        # Set these AFTER the autocomplete selection so they are authoritative.
        self.city_input.fill(city)
        self._select_state("#state", state)
        self.zip_input.fill(zip_code)

    @allure.step("Fill primary client checkout details")
    def fill_primary_details(self, dob: str, ssn: str, street: str, city: str,
                             state: str, zip_code: str, apt: str = ""):
        """Contact name/email/phone arrive pre-filled from the lead form; only
        DOB, SSN and the address still need entering."""
        self.set_date_of_birth(dob)
        self.fill_full_ssn(ssn)
        self.fill_address(street, city, state, zip_code, apt)

    @allure.step("Fill additional household member: {first_name} {last_name}")
    def fill_additional_member(self, first_name: str, last_name: str, email: str,
                               phone: str, dob: str, ssn: str):
        self.additional_first_name.fill(first_name)
        self.additional_last_name.fill(last_name)
        self.additional_email.fill(email)
        # Masked input — a bulk .fill() is dropped, so type it (same as the
        # primary phone box on the lead form).
        self.additional_phone.click()
        self.page.keyboard.type(phone, delay=50)
        self._set_readonly_date("#additional_dob", dob)
        self.fill_additional_ssn(ssn)

    @allure.step("Fill additional member address")
    def fill_additional_address(self, street: str, city: str, state: str,
                                zip_code: str, apt: str = ""):
        """The additional member's street box is a plain input on this tenant
        (no Places autocomplete), so a straight .fill() is enough."""
        self.additional_street_input.fill(street)
        if apt:
            self.additional_apt_input.fill(apt)
        self.additional_city_input.fill(city)
        self._select_state("#additional_state", state)
        self.additional_zip_input.fill(zip_code)

    def _select_state(self, selector: str, state: str):
        """
        Pick a state, tolerating the page's late-loading state list.

        Both state dropdowns render disabled and holding nothing but their
        "Select State" placeholder; the tenant's country script populates and
        enables them a beat after load (and refreshes them again once a Places
        suggestion resolves). Selecting into that window is what makes a naive
        select_option flake, so wait for the list to be real first, and fall
        back to setting the value directly if the refresh stalls.
        """
        select = self.page.locator(selector)
        try:
            self.page.wait_for_function(
                """(sel) => {
                    const el = document.querySelector(sel);
                    return el && !el.disabled && el.options.length > 1;
                }""",
                selector,
                timeout=20000,
            )
            select.select_option(label=state)
        except Exception:
            self.page.evaluate(
                """([sel, value]) => {
                    const el = document.querySelector(sel);
                    el.disabled = false;
                    el.value = value;
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }""",
                [selector, state],
            )
        # Option values are the state names themselves (value="California").
        expect(select).to_have_value(state)

    def _set_readonly_date(self, selector: str, value: str):
        """Both DOB boxes are jQuery-UI datepickers — set them via JS."""
        self.page.evaluate(
            """([selector, value]) => {
                const el = document.querySelector(selector);
                el.removeAttribute('readonly');
                el.value = value;
                el.dispatchEvent(new Event('input',  { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }""",
            [selector, value],
        )

    @allure.step("Uncheck the Household Discount option")
    def uncheck_household_discount(self):
        """
        Untick "Would you like to add a family or household member and see
        special discount pricing?" in the Total Payment summary.

        The page responds by collapsing the additional member's contact and
        address blocks and re-pricing the plan for a single client, so this is
        what turns the household funnel into a single-client checkout.
        """
        if not self.household_discount_checkbox.is_checked():
            return
        self.household_discount_label.click()
        if self.household_discount_checkbox.is_checked():
            # The real <input> sits behind a styled checkmark; if the label
            # click didn't register, clear it directly and fire the event the
            # page's summary listens for.
            self.page.evaluate(
                """() => {
                    const el = document.querySelector('#household_checkbox');
                    el.checked = false;
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }"""
            )
        expect(self.household_discount_checkbox).not_to_be_checked()
        # Wait for the collapse rather than sleeping, so the submit can't race
        # the page still treating this as a two-client order.
        expect(self.additional_first_name).to_be_hidden()
        expect(self.additional_street_input).to_be_hidden()

    @allure.step("Accept the household acknowledgement (last checkbox)")
    def accept_household_acknowledgement(self):
        """Tick the final checkbox in the order summary. The <input> is hidden
        behind a styled checkmark, so click the label; fall back to JS.

        No-ops when the checkbox isn't rendered or has been collapsed along
        with the household discount, so the shared submit path serves both the
        household and single-client checkouts.
        """
        if self.household_ack_checkbox.count() == 0:
            return
        if not self.household_ack_checkbox.is_visible():
            return
        if self.household_ack_checkbox.is_checked():
            return
        self.household_ack_label.click()
        if not self.household_ack_checkbox.is_checked():
            self.page.evaluate(
                """() => {
                    const el = document.querySelector('#household_acknowledgement_checkbox');
                    el.checked = true;
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }"""
            )
        expect(self.household_ack_checkbox).to_be_checked()

    @allure.step("Submit household checkout")
    def submit_household_checkout(self):
        """
        Submit and wait for the agreement.

        This tenant POSTs /checkout and lets the server redirect to
        /agreement — the same shape as the standard funnel — so the inherited
        submit path (which fails fast with the response body if either leg
        returns >= 400) applies unchanged.
        """
        self.accept_household_acknowledgement()
        self._submit_checkout(self.household_submit_button)

    # ════════════════════════════════════════════════════════
    # Convenience: run the whole household funnel
    # ════════════════════════════════════════════════════════
    @allure.step("Complete the full household signup funnel")
    def complete_household_signup(self, *, first_name, last_name, email, phone,
                                  dob, ssn, street, city, state, zip_code,
                                  additional, card_number, expiry, cvv,
                                  password, apt=""):
        self.navigate_to_start()
        self.fill_lead_form(first_name, last_name, email, phone)
        self.submit_lead_form()

        self.enable_household_toggle()
        self.select_first_plan()

        self.fill_primary_details(dob, ssn, street, city, state, zip_code, apt)
        self.fill_additional_member(**additional["contact"])
        self.fill_additional_address(**additional["address"])
        self.fill_payment_details(card_number, expiry, cvv)
        self.submit_household_checkout()

        self.sign_agreement()
        self.go_to_set_password()
        self.set_password(password)
