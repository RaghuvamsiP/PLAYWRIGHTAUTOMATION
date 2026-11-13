"""
Central configuration for all environments and shared constants.

Every value here can be overridden with an environment variable of the same
name, so CI can point the suite at another environment or set of credentials
without editing this file.
"""

import os
from pathlib import Path

# Repository root — anchor for every test-data path so tests do not depend
# on the directory pytest happens to be invoked from.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_DATA_DIR = PROJECT_ROOT / "test_data"
API_TEST_DATA_DIR = TEST_DATA_DIR / "api"

# Application URLs
BASE_URL = os.getenv("BASE_URL", "https://qa.creditrepaircloud.com")
API_BASE_URL = os.getenv("API_BASE_URL", "https://restful-booker.herokuapp.com")

# CRC platform APIs
AUTH_API_BASE_URL = os.getenv(
    "AUTH_API_BASE_URL", "https://prod-auth-migration.creditrepaircloud.com"
)
CRC_API_BASE_URL = os.getenv("CRC_API_BASE_URL", "https://api.creditrepaircloud.com")
LOGIN_API_PATH = "/api/v1/login"

# Public lead-capture / signup funnel (affiliate-specific subdomain)
LEADS_BASE_URL = os.getenv(
    "LEADS_BASE_URL", "https://amex4516.qa-leads-new.getcredithelpnow.com"
)
# QA funnel tenant that offers the Individual/Household plan toggle
HOUSEHOLD_LEADS_BASE_URL = os.getenv(
    "HOUSEHOLD_LEADS_BASE_URL", "https://hplan.qa-leads-new.getcredithelpnow.com"
)
# SecureClientAccess portal where the new client sets their password
SCA_BASE_URL = os.getenv("SCA_BASE_URL", "https://staging.secureclientaccess.com")

# Auth
LOGIN_URL = f"{BASE_URL}/login"
AUTH_FILE = str(PROJECT_ROOT / "tests" / "auth.json")

# Default test credentials (override via environment variables in CI)
DEFAULT_EMAIL = os.getenv("CRC_EMAIL", "pm@yopmail.com")
DEFAULT_PASSWORD = os.getenv("CRC_PASSWORD", "Test@1234")

# Browser
# Headed by default for local debugging; set HEADLESS=1 in CI.
HEADLESS = os.getenv("HEADLESS", "").lower() in ("1", "true", "yes")
