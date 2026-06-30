import os
from playwright.sync_api import sync_playwright

AUTH_FILE = "tests/auth.json"


def create_auth():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://qa.creditrepaircloud.com/login", timeout=60000)

        page.get_by_placeholder("Email or User ID").fill("pm@yopmail.com")
        page.get_by_placeholder("Password").fill("Test@1234")
        page.locator("button[type='submit']").click()

        page.wait_for_url("**/app/home")

        context.storage_state(path=AUTH_FILE)

        browser.close()




