CLIENT_ID = None 
TEAM_ID = 1
CRO_ID = None
AUDIT_TEMPLATE_ID = "1"

CREDIT_HERO_SCORE_NAME = "CreditHeroScore"
CREDIT_HERO_SCORE_USERNAME = "paco_21@live.com"
CREDIT_HERO_SCORE_PASSWORD = "Ziggy2026"


CREDIT_HERO_SCORE = {
    "name": CREDIT_HERO_SCORE_NAME,
    "process": {
        "clientId": CLIENT_ID,
        "provider": CREDIT_HERO_SCORE_NAME,
        "userName": CREDIT_HERO_SCORE_USERNAME,
        "password": CREDIT_HERO_SCORE_PASSWORD,
        "ssn": "",
        "phone_number": "",
        "isSubmit": 1,
        "isContinueWithDuplicate": 0,
        "isReimport": 0,
        "isReportImportedPreviously": 0,
        "simpleAudit": 0,
        "lastImportDate": "",
        "generateSimpleAudit": 0,
        "auditTemplateId": AUDIT_TEMPLATE_ID,
        "teamId": TEAM_ID,
        "croId": CRO_ID,
    },
    "credit_access": {
        "report_provider": CREDIT_HERO_SCORE_NAME,
        "notes": "",
        "user_name": CREDIT_HERO_SCORE_USERNAME,
        "password": CREDIT_HERO_SCORE_PASSWORD,
        "auditTemplate": AUDIT_TEMPLATE_ID,
    },
    "fetch": {
        "path": "/api/report/chs/fetch",
        "format": "json",
        "clientId": CLIENT_ID,
        "provider": CREDIT_HERO_SCORE_NAME,
        "teamId": TEAM_ID,
        "simpleAudit": 0,
        "auditTemplateId": AUDIT_TEMPLATE_ID,
        "isPendingReport": 0,
        "pendingReportId": 0,
        "generateSimpleAudit": 0,
        "isReimport": 0,
        "requestId": "",
    },
}

PROVIDER_2 = {
    "name": "Provider2",
    "process": {},
    "credit_access": {},
    "fetch": {"path": "/api/report/provider2/fetch"},
}

PROVIDER_3 = {
    "name": "Provider3",
    "process": {},
    "credit_access": {},
    "fetch": {"path": "/api/report/provider3/fetch"},
}

PROVIDER_4 = {
    "name": "Provider4",
    "process": {},
    "credit_access": {},
    "fetch": {"path": "/api/report/provider4/fetch"},
}

PROVIDER_5 = {
    "name": "Provider5",
    "process": {},
    "credit_access": {},
    "fetch": {"path": "/api/report/provider5/fetch"},
}

PROVIDER_6 = {
    "name": "Provider6",
    "process": {},
    "credit_access": {},
    "fetch": {"path": "/api/report/provider6/fetch"},
}
