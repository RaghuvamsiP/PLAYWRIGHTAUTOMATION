"""
Central configuration for all environments and shared constants.
"""

# Application URLs
BASE_URL = "https://qa.creditrepaircloud.com"
API_BASE_URL = "https://restful-booker.herokuapp.com"

# Public lead-capture / signup funnel (affiliate-specific subdomain)
LEADS_BASE_URL = "https://sscs7600.stage-leads-new.getcredithelpnow.com"
# SecureClientAccess portal where the new client sets their password
SCA_BASE_URL = "https://staging.secureclientaccess.com"

# Auth
LOGIN_URL = f"{BASE_URL}/login"
AUTH_FILE = "tests/auth.json"

# Default test credentials (override via environment variables in CI)
DEFAULT_EMAIL = "pm@yopmail.com"
DEFAULT_PASSWORD = "Test@1234"
