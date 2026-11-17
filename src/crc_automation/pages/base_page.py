import allure
from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("Navigate to URL: {url}")
    def navigate(self, url: str, timeout: int = 60000):
        self.page.goto(url, wait_until="domcontentloaded", timeout=timeout)

    @allure.step("Wait for URL pattern: {pattern}")
    def wait_for_url(self, pattern: str, timeout: int = 10000):
        self.page.wait_for_url(pattern, timeout=timeout)
