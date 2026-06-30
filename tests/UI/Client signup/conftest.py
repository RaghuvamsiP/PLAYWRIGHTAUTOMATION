import json
import pathlib

import pytest
import allure
from playwright.sync_api import sync_playwright

# Where raw network / console artifacts are written for every run.
ARTIFACTS_DIR = pathlib.Path("reports/network")


@pytest.fixture(scope="session")
def unauthenticated_browser():
    """The public signup funnel must run with no stored CRC auth state."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture
def fresh_page(unauthenticated_browser, request):
    """
    A clean browser page (no auth) for the signup funnel that ALSO records,
    for every run:
      * a full HAR (with response bodies)  -> reports/network/<test>.har
      * all console errors / page errors   -> reports/network/<test>.console.json
      * every HTTP response with status>=400 (status, method, url, body)
                                           -> reports/network/<test>.failed.json
    All three are attached to the Allure report. This makes intermittent
    failures (e.g. a 500 after submitting checkout) debuggable after the fact.
    """
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    test_name = request.node.name
    har_path = ARTIFACTS_DIR / f"{test_name}.har"
    console_path = ARTIFACTS_DIR / f"{test_name}.console.json"
    failed_path = ARTIFACTS_DIR / f"{test_name}.failed.json"

    # record_har_content="embed" stores response bodies inside the HAR, so the
    # body of a failing /checkout (500) is preserved.
    context = unauthenticated_browser.new_context(
        record_har_path=str(har_path),
        record_har_content="embed",
    )
    # Block tracking/chat popups that overlay form controls.
    context.route("**/*userproof*", lambda route: route.abort())
    context.route("**/*intercom*", lambda route: route.abort())

    console_errors = []
    failed_responses = []

    def on_console(msg):
        # Capture console errors only (parser/CSP warnings are noise here).
        if msg.type == "error":
            console_errors.append(
                {"type": msg.type, "text": msg.text, "location": msg.location}
            )

    def on_pageerror(exc):
        console_errors.append({"type": "pageerror", "text": str(exc)})

    def on_response(resp):
        try:
            if resp.status >= 400:
                # Best-effort body capture; the HAR also has it as a fallback.
                try:
                    body = resp.text()[:5000]
                except Exception:
                    body = "<body unavailable on live response — see HAR>"
                failed_responses.append(
                    {
                        "status": resp.status,
                        "method": resp.request.method,
                        "url": resp.url,
                        "body": body,
                    }
                )
        except Exception:
            pass

    page = context.new_page()
    page.on("console", on_console)
    page.on("pageerror", on_pageerror)
    page.on("response", on_response)

    yield page

    # ── Teardown: persist + attach artifacts ─────────────────
    # Console errors
    if console_errors:
        console_path.write_text(json.dumps(console_errors, indent=2), encoding="utf-8")
        allure.attach(
            json.dumps(console_errors, indent=2),
            name="Console Errors / Warnings",
            attachment_type=allure.attachment_type.JSON,
        )

    # Failed (>=400) network responses
    if failed_responses:
        failed_path.write_text(json.dumps(failed_responses, indent=2), encoding="utf-8")
        allure.attach(
            json.dumps(failed_responses, indent=2),
            name="Failed Network Responses (status >= 400)",
            attachment_type=allure.attachment_type.JSON,
        )
        # Surface in the pytest console (-s) so failures are visible immediately.
        print("\n=== Failed network responses (>=400) ===")
        for r in failed_responses:
            print(f"  [{r['status']}] {r['method']} {r['url']}")
        print("========================================")

    # On failure: screenshot + URL
    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        allure.attach(
            page.screenshot(full_page=True),
            name="Screenshot on Failure",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            page.url,
            name="Page URL on Failure",
            attachment_type=allure.attachment_type.TEXT,
        )

    page.close()
    context.close()  # HAR is flushed to disk here.

    # Attach the HAR after it has been written.
    if har_path.exists():
        allure.attach.file(
            str(har_path),
            name="Network HAR",
            extension="har",
        )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Expose test outcome to the fresh_page fixture for failure screenshots."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
