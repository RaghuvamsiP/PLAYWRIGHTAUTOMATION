"""
Centralized URL registry for the Credit Repair Cloud QA application.

Usage in page objects / tests:
    from config.urls import AppURLs
    page.goto(AppURLs.Auth.LOGIN)
    page.goto(AppURLs.Clients.LIST)
"""

from config.settings import BASE_URL, LEADS_BASE_URL, SCA_BASE_URL


class AppURLs:
    """
    Nested class structure groups URLs by module/section.
    This gives IDE autocomplete, prevents typos, and makes
    refactoring easy when routes change.
    """

    # ──────────────────────────────────────────────
    # Authentication
    # ──────────────────────────────────────────────
    class Auth:
        LOGIN   = f"{BASE_URL}/app/login"
        HOME    = f"{BASE_URL}/app/home"
        HISTORY = f"{BASE_URL}/app/history"

    # ──────────────────────────────────────────────
    # Public Signup / Lead-Capture Funnel
    # ──────────────────────────────────────────────
    class Signup:
        START           = f"{LEADS_BASE_URL}/start"
        SHOW_PLANS      = f"{LEADS_BASE_URL}/show-plans"
        CHECKOUT        = f"{LEADS_BASE_URL}/checkout"
        AGREEMENT       = f"{LEADS_BASE_URL}/agreement"
        CHECKOUT_SUCCESS = f"{LEADS_BASE_URL}/checkout-success"
        # SecureClientAccess portal (separate host)
        SCA_HOME        = f"{SCA_BASE_URL}/home"

    # ──────────────────────────────────────────────
    # Main Navigation Tabs
    # ──────────────────────────────────────────────
    class Clients:
        LIST      = f"{BASE_URL}/app/clients"
        DASHBOARD = f"{BASE_URL}/app/clients/{{client_id}}/dashboard"  # use .format(client_id=...)

    class Schedule:
        PAGE = f"{BASE_URL}/app/schedule"

    class MyCompany:
        PROFILE              = f"{BASE_URL}/app/my-company"
        BILLING_AND_PAYMENTS = f"{BASE_URL}/app/my-company/billing-and-payments"
        CREDIT_MONITORING    = f"{BASE_URL}/app/my-company/cms"
        AFFILIATE_PAYMENTS   = f"{BASE_URL}/app/my-company/affiliate-payments/active-inactive-list"

    class LetterLibrary:
        PAGE = f"{BASE_URL}/app/mediacenter"

    class Affiliates:
        LIST = f"{BASE_URL}/app/affiliate"

    class Furnishers:
        LIST = f"{BASE_URL}/app/furnishers"

    class Dashboard:
        PAGE = f"{BASE_URL}/app/dashboard"

    # ──────────────────────────────────────────────
    # Quick Links (accessible from Home page)
    # ──────────────────────────────────────────────
    class QuickLinks:
        ACTIVITY_LOG      = f"{BASE_URL}/app/everything/progress"
        FIRST_WORK        = f"{BASE_URL}/app/everything/pendingclients"
        ALL_TASKS         = f"{BASE_URL}/app/everything/alltasks"
        ALL_MESSAGES      = f"{BASE_URL}/app/everything/allmessages"
        ALL_CLOUDMAIL     = f"{BASE_URL}/app/everything/allcloudmailsent"
        ALL_FILES         = f"{BASE_URL}/app/everything/alldocuments"
        CONTACTS          = f"{BASE_URL}/app/home/contacts"
