# CLAUDE.md

Guidance for Claude Code working in this repository. See [README.md](README.md)
for the full picture; this file covers what is easy to get wrong here.

## Environment

Windows. The venv interpreter is `venv/Scripts/python.exe` — always invoke
pytest through it (`venv/Scripts/python.exe -m pytest ...`), not a bare
`pytest`. Git Bash is available alongside PowerShell.

No linter or formatter is installed. Do not `pip install` one into the venv
without asking; write a throwaway AST script in the scratchpad instead.

The filesystem is case-insensitive (`core.ignorecase=true`), so a case-only
rename needs two steps:

```bash
git mv tests/API tests/_tmp && git mv tests/_tmp tests/api
```

## Layout rules

- Importable code lives in `src/crc_automation/`. Tests live in `tests/`.
  Never add a helper, payload builder or page object under `tests/`.
- Imports are absolute from the package: `from crc_automation.pages.login_page
  import LoginPage`. `pythonpath = ["src"]` in `pyproject.toml` makes this work
  without installing anything.
- `test_data/` is data only — no `.py` files.
- Exploratory or one-off scripts go in `sandbox/`, which `norecursedirs`
  excludes from the default run.

## Conventions that matter

**Never add `page.wait_for_timeout()`.** Use `expect()`, which retries. Four
deliberate exceptions remain, each with a comment saying why no deterministic
signal exists; do not copy them as precedent. `expect(locator, "message")`
takes a custom message, so converting an `assert` loses nothing.

**Never hardcode or compute paths.** Import the anchors:

```python
from crc_automation.config.settings import (
    PROJECT_ROOT, TEST_DATA_DIR, API_TEST_DATA_DIR, FILES_DIR, CREDENTIALS_DIR,
)
```

`Path(__file__).resolve().parents[N]` math is how the suite got broken before —
the count silently goes wrong when a file moves to a different depth.

**Do not open data files at module import** unless `parametrize` needs the
contents. An import-time `open()` that fails aborts collection for the entire
suite, not just that module.

**Selectors and interaction waits belong in page objects.** Tests call methods.
If a test needs a wait after an action, add it to the page object method
instead (see `get_validation_errors`, `wait_for_toaster`,
`wait_for_dialog_closed`).

**Never hardcode a URL or credential in a test.** Environment-specific values
live in `environments/<env>.env` and are read through `settings.py`. Add a new
key to every profile, then read it with `os.getenv` (optional) or
`settings.require()` (mandatory). `require()` fails with a message naming the
profile, which is what makes a missing stage value obvious instead of a 401.

Copying a test file to retarget another environment is the thing this
configuration exists to prevent. `tests/api/rate_limit` used to hold three
near-identical copies; it is now one file driven by the profile. Do not
reintroduce that pattern.

## Running tests

```bash
venv/Scripts/python.exe -m pytest --collect-only -q    # expect 468
venv/Scripts/python.exe -m pytest sandbox --collect-only -q -o addopts=""   # expect 5
venv/Scripts/python.exe -m compileall -q . -x "venv|__pycache__"
```

Collection plus compile is the normal verification loop after a refactor, and
is usually enough.

**Executing UI or live-API tests is not routine — ask first.** They use real
credentials and create real records (clients, affiliates, letters, wallet
transactions). Specifically:

- `tests/api/clients` and `tests/api/letter_library` default to
  **production**: they authenticate against
  `prod-auth-migration.creditrepaircloud.com` and call
  `api.creditrepaircloud.com`. `test_report_import.py` creates a client there.
- `tests/api/rate_limit` floods endpoints and creates records. It runs against
  whatever ENV is set, so `ENV=prod` points it at production on purpose.
- `tests/api/cloudmail` uses QA internal hosts but spends real wallet balance.
- `tests/api/alerts` calls the third-party array.io API.
- UI tests drive a browser against the QA app and create records there.

The only tests safe to run unprompted are ones reading local fixtures, such as
`sandbox/test_credit_limit.py`.

UI tests are headed by default; `HEADLESS=1` hides the browser.

## Gotchas

- The root `conftest.py` defines `browser` / `context` / `page`, overriding
  `pytest-playwright`. Its CLI flags (`--headed`, `--browser`, `--video`,
  `--tracing`, `--slowmo`) therefore do nothing. Use `HEADLESS` instead, and do
  not suggest those flags.
- `context` is **session-scoped** — UI tests share one logged-in context.
  Changing that to function scope would reset state between tests.
- Fixtures read failures via `getattr(request.node, "rep_call", None)`. The
  attribute is absent when a test errors in setup, so never drop the `getattr`.
- `.claude/settings.local.json` is session permission state. Leave it out of
  commits.
- `tests/api/booking` targets `restful-booker.herokuapp.com`, a public practice
  API, not a CRC service.

## Git

Current work is on `docs/readme-and-claude-md`; `master` is the main branch.
Commit only when asked. Keep refactor commits (renames) separate from
behavioural changes so `git` rename detection keeps the diff readable.
