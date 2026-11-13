"""
Central configuration, resolved per environment.

Values are looked up in this order, first hit wins:

1. A real environment variable (what CI sets)
2. `.env` in the repo root — your personal overrides, git-ignored
3. `environments/<ENV>.env` — the committed profile for that environment
4. The fallback in this file

Pick the environment with ENV, which defaults to qa:

    pytest                     # qa
    ENV=stage pytest           # stage
    ENV=prod pytest -m smoke   # prod

Nothing in the test code refers to an environment by name — switching is
entirely a matter of which profile gets loaded.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# settings.py lives at <root>/src/crc_automation/config/, so the repo
# root is four levels up.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
TEST_DATA_DIR = PROJECT_ROOT / "test_data"
API_TEST_DATA_DIR = TEST_DATA_DIR / "api"
UI_TEST_DATA_DIR = TEST_DATA_DIR / "ui"
CREDENTIALS_DIR = API_TEST_DATA_DIR / "credentials"
# Binary fixtures (PDF / images) used by upload tests.
FILES_DIR = TEST_DATA_DIR / "files"

ENVIRONMENTS_DIR = PROJECT_ROOT / "environments"


def _load_environment() -> str:
    """Load `.env` then the selected profile, without clobbering real env vars."""
    env = os.getenv("ENV", "qa").strip().lower()
    profile = ENVIRONMENTS_DIR / f"{env}.env"

    if not profile.is_file():
        available = sorted(p.stem for p in ENVIRONMENTS_DIR.glob("*.env"))
        raise RuntimeError(
            f"ENV={env!r} has no profile at {profile}. "
            f"Available environments: {', '.join(available) or '(none)'}"
        )

    # override=False everywhere, so a variable already set in the shell or by
    # CI always wins, and `.env` always beats the committed profile.
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    load_dotenv(profile, override=False)
    return env


ENV = _load_environment()

# ── Application URLs ──────────────────────────────────────────────
BASE_URL = os.getenv("BASE_URL", "https://qa.creditrepaircloud.com")

# CRC platform APIs
AUTH_API_BASE_URL = os.getenv(
    "AUTH_API_BASE_URL", "https://qa-auth-migration.creditrepaircloud.com"
)
CRC_API_BASE_URL = os.getenv("CRC_API_BASE_URL", "https://qa-api.creditrepaircloud.com")
OAUTH_BASE_URL = os.getenv("OAUTH_BASE_URL", "https://qa-oauth.creditrepaircloud.com")
LOGIN_API_PATH = "/api/v1/login"

# Public lead-capture / signup funnel (affiliate-specific subdomain)
LEADS_BASE_URL = os.getenv("LEADS_BASE_URL", "")
# Funnel tenant that offers the Individual/Household plan toggle
HOUSEHOLD_LEADS_BASE_URL = os.getenv("HOUSEHOLD_LEADS_BASE_URL", "")
# SecureClientAccess portal where the new client sets their password
SCA_BASE_URL = os.getenv("SCA_BASE_URL", "")

# CloudMail services
CLOUDMAIL_LETTERS_BASE_URL = os.getenv("CLOUDMAIL_LETTERS_BASE_URL", "")
CLOUDMAIL_BASE_URL = os.getenv("CLOUDMAIL_BASE_URL", "")

# Practice API used by tests/api/booking — not a CRC service.
API_BASE_URL = os.getenv("API_BASE_URL", "https://restful-booker.herokuapp.com")

# ── Auth ──────────────────────────────────────────────────────────
LOGIN_URL = f"{BASE_URL}/login"

# Runtime artifact (git-ignored), not part of the test tree. Kept per
# environment so switching ENV does not reuse another environment's session.
AUTH_DIR = PROJECT_ROOT / ".auth"
AUTH_FILE = str(AUTH_DIR / f"storage_state.{ENV}.json")

# Credentials. Keep real secrets in `.env` or CI, not in a committed profile.
DEFAULT_EMAIL = os.getenv("CRC_EMAIL", "")
DEFAULT_PASSWORD = os.getenv("CRC_PASSWORD", "")

# ── Browser ───────────────────────────────────────────────────────
# Headed by default for local debugging; set HEADLESS=1 in CI.
HEADLESS = os.getenv("HEADLESS", "").lower() in ("1", "true", "yes")


def require(name: str) -> str:
    """Return a setting's value, or fail with a message naming the profile.

    Use for values a test cannot run without, so the failure says what to set
    rather than surfacing as a confusing 401 or a request to an empty host.
    """
    value = os.getenv(name, "")
    if not value:
        raise RuntimeError(
            f"{name} is not set for ENV={ENV!r}. Add it to environments/{ENV}.env, "
            f"to your .env, or export it before running."
        )
    return value
