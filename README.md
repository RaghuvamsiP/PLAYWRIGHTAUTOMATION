# CRC Automation

Playwright + pytest automation for Credit Repair Cloud — UI tests against the
QA web app and the public signup funnels, plus API tests against the CRC
platform and CloudMail services.

- **468 tests** in the suite, plus 5 exploratory scripts in `sandbox/`
- Page Object Model for UI, shared request contexts for API
- Allure reporting, session-scoped login so most tests skip the login screen

---

## Setup

Requires Python 3.10+ (developed on 3.14). Node is not needed — Playwright
ships its own browsers.

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
```

`requirements.txt` is just `-e .`; the real dependency list lives in
`pyproject.toml`. The editable install is optional — `pythonpath = ["src"]`
in `pyproject.toml` lets pytest import `crc_automation` straight from `src/`.

---

## Running tests

```bash
pytest
```

That runs everything under `tests/`. `sandbox/` is excluded.

```bash
pytest tests/api
pytest tests/ui/login
pytest tests/ui/affiliates/test_affiliate_module.py::TestPortalAccessPerStatus
pytest -m smoke
pytest -k portal
pytest -n 4
pytest sandbox
```

UI tests run **headed by default** so you can watch them. For CI:

```bash
HEADLESS=1 pytest
```

Markers: `smoke` (15), `sanity` (21), `ui` (13), `negative` (3),
`regression` (1), `no_balance_restore` (1). `api` is declared in
`pyproject.toml` but not applied to any test yet.

---

## Project structure

```
pyproject.toml              Package metadata, dependencies, pytest config
conftest.py                 Root fixtures + the report hook
src/crc_automation/         The framework (importable package)
    config/
        settings.py         URLs, credentials, paths — all env-overridable
        urls.py             AppURLs registry, grouped by app section
    pages/                  Page objects, one per screen/dialog
        base_page.py        BasePage: navigate(), wait_for_url()
    api/                    API-side helpers
        auth.py             login_and_get_token(), get_company_id()
        payloads/           Request body builders
        clients/            Client creation helpers
        report_providers.py Credit report provider configs
    utils/
        auth_helper.py      Creates the stored login session
        affiliate_helper.py create_affiliate() / setup_affiliate()
        fake_data.py        Faker-backed test data
test_data/
    api/                    JSON payloads + CSV imports
        credentials/        Credential CSVs for provider sweeps
    files/                  PDF and image upload fixtures
    ui/                     CSV import fixtures
tests/
    api/{alerts,booking,clients,cloudmail,letter_library,rate_limit}/
    ui/{affiliates,client_signup,clients,login}/
sandbox/                    Exploratory scripts, not part of the suite
reports/                    Allure results, HAR captures (git-ignored)
.auth/                      Stored login session (git-ignored)
```

Anything importable lives under `src/`. `tests/` contains only tests.

---

## Environments

Pick the target with `ENV`. It defaults to `qa`, and no test code mentions an
environment by name — switching only changes which profile is loaded.

```bash
pytest                      # qa
ENV=stage pytest            # stage
ENV=prod pytest -m smoke    # prod
```

Values resolve in this order, first hit wins:

1. A real environment variable — what CI sets
2. `.env` in the repo root — your personal overrides, git-ignored
3. `environments/<ENV>.env` — the committed, non-secret profile
4. The fallback in `settings.py`

So `.env` always beats the committed profile, which is where personal
accounts and secrets belong. Copy `.env.example` to get started.

An unknown `ENV` fails immediately and lists the profiles that do exist. A
value a test needs but has not been given fails through `require()` with a
message naming the file to set it in, rather than surfacing later as a 401.

The stored login session is kept per environment
(`.auth/storage_state.<env>.json`), so switching never reuses another
environment's cookies.

### Settings

Every setting reads an environment variable, so nothing needs editing to
retarget a run.

| Variable | Default | Used for |
| --- | --- | --- |
| `ENV` | `qa` | Which profile to load: `qa`, `stage`, `prod` |
| `BASE_URL` | per profile | The web app |
| `HEADLESS` | unset (headed) | `1`/`true`/`yes` to hide the browser |
| `CRC_EMAIL` / `CRC_PASSWORD` | `pm@yopmail.com` | Main UI login |
| `AUTH_API_BASE_URL` | `prod-auth-migration...` | Login API host |
| `CRC_API_BASE_URL` | `api.creditrepaircloud.com` | Platform API host |
| `CRC_CLIENTS_EMAIL` / `CRC_CLIENTS_PASSWORD` | service account | `tests/api/clients` |
| `CRC_SUPPORT_EMAIL` / `CRC_SUPPORT_PASSWORD` | **none — required** | `tests/api/letter_library` |
| `CRC_PDF_USER_EMAIL` / `CRC_PDF_USER_PASSWORD` | `pdf@yopmail.com` | `tests/ui/clients` |
| `LEADS_BASE_URL` | `amex4516.qa-leads-new...` | Signup funnel |
| `HOUSEHOLD_LEADS_BASE_URL` | `hplan.qa-leads-new...` | Household funnel |
| `SCA_BASE_URL` | `staging.secureclientaccess.com` | Client portal |
| `API_BASE_URL` | `restful-booker.herokuapp.com` | `tests/api/booking` practice API |
| `CHS_CSV_PATH` | `test_data/api/credentials/chs_credentials.csv` | Credential sweep input |

The Letter Library tests fail fast with a clear message if their two variables
are unset; everything else has a working default.

### Login session

UI tests reuse a stored Playwright storage state at `.auth/storage_state.json`
instead of logging in per test. The root `conftest.py` regenerates it
automatically when it is missing or older than two hours, which opens a browser
and logs in once.

---

## Fixtures

| Fixture | Scope | Where | Gives you |
| --- | --- | --- | --- |
| `page` | function | root | A tab in the shared logged-in session |
| `context` | session | root | Logged-in browser context, tracker popups blocked |
| `browser` | session | root | Chromium, refreshes auth first |
| `fresh_page` | function | `ui/login`, `ui/client_signup` | A page with **no** auth — for login and signup tests |
| `pdf_user_page` | function | `ui/clients` | A tab logged in as the PDF user |
| `api_request` | session | `tests/api` | Bare `APIRequestContext` |
| `request_context` | session | `api/cloudmail` | Bare context for CloudMail hosts |
| `token` | session | `api/clients`, `api/letter_library` | Bearer token from the login API |
| `auth_api` | session | `api/clients`, `api/letter_library` | Request context with `Authorization` set |
| `company_id` | session | `api/clients` | Company ID for report requests |

On failure the page fixtures attach a screenshot and the URL to Allure. The
`client_signup` fixture additionally records a HAR, console errors, and every
response with status >= 400.

---

## Writing tests

**Wait with assertions, not sleeps.** `expect()` retries until the condition
holds or it times out. `page.wait_for_timeout()` is a last resort, and the four
remaining uses each carry a comment explaining why no deterministic signal
exists.

```python
# no
page.wait_for_timeout(500)
assert page_obj.is_portal_checked(), "Portal should be ON"

# yes
expect(page_obj.portal_access_toggle, "Portal should be ON").to_be_checked()
```

`expect(locator, "message")` keeps your assertion text in the failure output.

**Keep selectors in page objects.** Tests call methods; they should not build
locators. Waits that belong to an interaction belong in the page object too —
`get_validation_errors()` waits for the first message itself, so tests do not
have to.

**Never hardcode paths.** Import the anchors from settings, which resolve from
the repo root regardless of where pytest was invoked:

```python
from crc_automation.config.settings import API_TEST_DATA_DIR, FILES_DIR

PAYLOAD = API_TEST_DATA_DIR / "send_letter_payload.json"
```

**Do not read data files at import time** unless `parametrize` needs it. A
missing file then fails collection and aborts the whole run rather than one
test.

---

## Reports

Allure results are written to `reports/allure-results` on every run
(`--clean-alluredir` wipes the previous one). To view:

```bash
allure serve reports/allure-results
```

This needs the Allure CLI, which installs separately from the Python package.

---

## Sandbox

`sandbox/` holds exploratory and one-off scripts — credential sweeps, alert
dumps, a manual letter-generation walkthrough. They are excluded from the
default run via `norecursedirs` but still work with `pytest sandbox`. Put
throwaway investigation here rather than in `tests/`.

---

## Known gaps

- Credential CSVs are committed to this repository, and `environments/qa.env`
  still carries the QA test passwords that used to be hardcoded in
  `settings.py`. Rotate them, then move them into `.env` and delete them from
  the committed profile.
- `stage.env` and `prod.env` have blanks where a host or tenant could not be
  confirmed from the existing code. A test needing one fails with a message
  naming the file.
- `tests/api/alerts` carries a hardcoded Array.io server token.
- The custom `browser` / `context` / `page` fixtures override the ones from
  `pytest-playwright`, so its CLI flags (`--headed`, `--browser`, `--video`,
  `--tracing`, `--slowmo`) do not apply to UI tests. Use `HEADLESS` instead.
- `smartcredit_credentials.csv` and `smartcredit_credentials_bulk.csv` are two
  different credential sets; those names are provisional.
