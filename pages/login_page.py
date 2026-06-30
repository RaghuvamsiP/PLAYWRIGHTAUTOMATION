import re
from datetime import datetime

import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from config.urls import AppURLs


class LoginPage(BasePage):
    RECAPTCHA_SELECTOR = "form iframe[title='reCAPTCHA']"

    def __init__(self, page: Page):
        super().__init__(page)
        # Form fields
        self.email_input = page.get_by_placeholder("Email or User ID")
        self.password_input = page.get_by_placeholder("Password")
        self.login_button = page.get_by_role("button", name="Login")

        # Labels with asterisk
        self.email_label = page.locator("text=Email or User ID*").first
        self.password_label = page.locator("text=Password*").first

        # Headings & text
        self.page_heading = page.get_by_role("heading", name="Hello again!")
        self.team_member_label = page.get_by_text("Team Member Login")
        self.dont_have_account_text = page.get_by_text("Don't have an account?")

        # Links
        self.logo = page.locator("img[src='/assets/images/cloud_logo.png']")
        self.logo_link = page.locator("a", has=self.logo)
        self.forgot_password_link = page.get_by_text("Forgot password?")
        self.sign_up_link = page.get_by_role("link", name="Sign Up")
        self.training_link = page.get_by_role("link", name="Join Our Free Training Sessions!")

        # Footer
        self.footer_security_text = page.get_by_text("Secure Area", exact=False)
        self.footer_copyright_text = page.get_by_text("Credit Repair Cloud. All rights reserved.", exact=False)

        # Error toast
        self.error_toast = page.get_by_role("alert")

        # reCAPTCHA
        self.recaptcha = page.locator(self.RECAPTCHA_SELECTOR)

        # Chatbot
        self.chatbot_button = page.get_by_role("button", name="Open Intercom Messenger")

    @allure.step("Navigate to login page")
    def navigate_to_login(self):
        self.navigate(AppURLs.Auth.LOGIN)

    @allure.step("Login with email: {email}")
    def login(self, email: str, password: str):
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.login_button.click()

    @allure.step("Wait for home page to load")
    def wait_for_home_page(self):
        self.page.wait_for_url(f"**{AppURLs.Auth.HOME}", timeout=15000)

    @allure.step("Check if on home page")
    def is_on_home_page(self) -> bool:
        return AppURLs.Auth.HOME in self.page.url

    @allure.step("Logout via header dropdown")
    def logout(self):
        self.page.get_by_text("Personal (admin)").click()
        self.page.get_by_role("link", name="Log Out").click()

    @allure.step("Get copyright year from footer")
    def get_footer_copyright_year(self) -> str | None:
        text = self.footer_copyright_text.inner_text()
        match = re.search(r"©\s*\d{4}-(\d{4})", text)
        return match.group(1) if match else None

    @allure.step("Check if reCAPTCHA is visible")
    def is_recaptcha_visible(self, timeout: int = 10000) -> bool:
        try:
            self.recaptcha.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False
